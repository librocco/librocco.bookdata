import click
import csv
from tqdm import tqdm
from urllib.parse import urlparse
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator

from librocco.bookdata import feed_book


@click.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.argument("db_url")
def main(csv_file, db_url):
    """A click command that loops over the given CSV file"""
    couchdb, db_name = make_db_connection(db_url)
    updated_books_num = 0
    new_books_num = 0

    # Use nonlocal keyword to modify the counter in the enclosing scope
    def inc_updated():
        nonlocal updated_books_num
        updated_books_num += 1
        updated_books_bar.update(1)  # Update progress bar for updated books

    def inc_new():
        nonlocal new_books_num
        new_books_num += 1
        new_books_bar.update(1)  # Update progress bar for new books

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file, delimiter="|")
        processed_books_bar = tqdm(
            total=number_of_rows(open(csv_file, "r")), desc="Processed Books"
        )
        updated_books_bar = tqdm(
            total=0, desc="Updated Books"
        )  # Start at zero and increase
        new_books_bar = tqdm(total=0, desc="New Books")  # Start at zero and increase
        for row in reader:
            book = convert_book(row)
            feed_book(book, couchdb, db_name, inc_updated=inc_updated, inc_new=inc_new)
            processed_books_bar.update(1)  # Update progress bar for each processed book

        processed_books_bar.close()
        updated_books_bar.close()
        new_books_bar.close()


def number_of_rows(file):
    file.seek(0)  # Go to the beginning of the file
    return len(file.readlines()) - 1  # Subtract one to exclude the header line


def make_db_connection(url):
    """
    Take a URL and return a couchdb connection plus a db name
    """
    parsed_url = urlparse(url)

    # Extract the username and password
    username = parsed_url.username
    password = parsed_url.password

    # Create a BasicAuthenticator
    authenticator = BasicAuthenticator(username, password)

    # Create a CloudantV1 instance
    service = CloudantV1(authenticator=authenticator)

    # Set the service URL
    service.set_service_url(parsed_url.geturl()[: -len(parsed_url.path) + 1])

    return service, parsed_url.path[1:]


def convert_book(row):
    """Convert a row from the CSV file into a dictionary"""
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
