def test_make_db_connection(couchdb_url, db_name):
    from librocco.bookdata.parsecsv import make_db_connection

    url = couchdb_url.replace("localhost", "admin:secret@localhost") + f"/{db_name}"
    service, res_db_name = make_db_connection(url)
    assert res_db_name == db_name
