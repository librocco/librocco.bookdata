Parse a CSV file and feed it to couchdb
=======================================

TODO: write a description


Running tests
-------------

The tests will start a couchdb docker image automatically.
If you prefer bringing your own couchdb, pass the COUCHDB_URL variable to `pytest`. Example:

    docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=secret couchdb:latest
    COUCHDB_URL=http://localhost:5984 pytest
