import pytest
import docker
import socket
import requests
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
