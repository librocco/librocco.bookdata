from ibmcloudant import CouchDbSessionAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
import pytest
import docker
import socket
import os
import random
import requests
import string
import time


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    address, port = s.getsockname()
    s.close()
    return port


def wait_for_couchdb_to_be_ready(url, timeout=60):
    """Wait until CouchDB is ready to accept connections or timeout is reached."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("CouchDB is ready!")
                return True
        except requests.exceptions.ConnectionError:
            print("CouchDB is not ready. Waiting...")
            time.sleep(1)  # wait a bit before trying again
    raise RuntimeError(f"CouchDB did not become ready within {timeout} seconds")


@pytest.fixture(scope="session")
def couchdb_url():
    if os.environ["COUCHDB_URL"]:
        yield os.environ["COUCHDB_URL"]
        return
    port = get_free_port()
    client = docker.from_env()
    print(f"Starting CouchDB container on port {port}...")
    container = client.containers.run(
        "couchdb:latest", 
        detach=True, 
        ports={'5984/tcp': port}, 
        environment={"COUCHDB_USER": "admin", "COUCHDB_PASSWORD": "secret"}
    )
    url = f"http://localhost:{port}"

    wait_for_couchdb_to_be_ready(url)
    print(f"CouchDB started on port {port}...")
    yield url

    # After tests completion, stop the CouchDB container
    print("Stopping CouchDB container...")
    container.stop()
    container.remove()
    print("CouchDB container stopped and removed.")


@pytest.fixture(scope="function")
def db_name():
    """Generates a random database name."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))


@pytest.fixture(scope="function")
def couchdb(couchdb_url, db_name):
    """Connects to couchdb and returns a db object.
    It creates a database with a random name and deletes it after the test.
    """
    # Connect to the CouchDB server using username "admin" and password "secret"
    authenticator = BasicAuthenticator("admin", "secret")
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(couchdb_url)

    # Create the database
    client.put_database(db=db_name)
    print(f"Created database {db_name}")

    yield client

    # After the test, delete the database
    print(f"Deleting {db_name}...")
    client.delete_database(db=db_name)
    print(f"Deleted database {db_name}")