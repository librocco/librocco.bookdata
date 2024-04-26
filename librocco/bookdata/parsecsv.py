import click
import csv
from tqdm import tqdm
from urllib.parse import urlparse
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
from multiprocessing import Process, Queue, Value, Lock
from librocco.bookdata import feed_book


@click.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.argument("db_url")
def main(csv_file, db_url):
    couchdb, db_name = make_db_connection(db_url)

    # Shared counters with lock for thread-safe increments
    updated_books_num = Value("i", 0)
    new_books_num = Value("i", 0)

    # Lock for updating progress bars
    lock = Lock()

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file, delimiter="|")
        processed_books_bar = tqdm(
            total=number_of_rows(open(csv_file, "r")), desc="Processed Books"
        )
        updated_books_bar = tqdm(total=0, desc="Updated Books")
        new_books_bar = tqdm(total=0, desc="New Books")

        # Worker function adapted for multiprocessing
        def process_books(queue):
            while True:
                row = queue.get()
                if row is None:  # Poison pill means shutdown
                    break
                book = convert_book(row)
                feed_book(
                    book,
                    couchdb,
                    db_name,
                    lambda: inc_counter(updated_books_num, updated_books_bar, lock),
                    lambda: inc_counter(new_books_num, new_books_bar, lock),
                )
                lock.acquire()
                processed_books_bar.update(1)
                lock.release()

        # Helper function to safely increment counters and update progress bars
        def inc_counter(counter, bar, lock):
            with lock:
                counter.value += 1
                bar.update(1)

        # Create a queue and populate it with data rows
        queue = Queue()
        for row in reader:
            queue.put(row)

        # Start worker processes
        workers = []
        for _ in range(40):  # Number of workers
            p = Process(target=process_books, args=(queue,))
            p.start()
            workers.append(p)
            queue.put(None)  # Each worker gets a poison pill for termination

        # Wait for all workers to complete
        for p in workers:
            p.join()

        processed_books_bar.close()
        updated_books_bar.close()
        new_books_bar.close()


def number_of_rows(file):
    file.seek(0)
    return len(file.readlines()) - 1


def make_db_connection(url):
    parsed_url = urlparse(url)
    username = parsed_url.username
    password = parsed_url.password
    authenticator = BasicAuthenticator(username, password)
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(parsed_url.geturl()[: -len(parsed_url.path) + 1])
    return service, parsed_url.path[1:]


def convert_book(row):
    return {
        "title": row["titolo"],
        "authors": row["autore"],
        "price": row["prezzo"],
        "isbn": row["ean13"],
        "publisher": row["editore"],
        "year": row["data_pubblicazione"][:4],
    }


if __name__ == "__main__":
    main()
