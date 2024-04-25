import click
import csv
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
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file, delimiter="|")
        for row in reader:
            book = convert_book(row)
            feed_book(book, couchdb, db_name)
            print(f"Added {book['isbn']}")


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
    service.set_service_url(url)

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
