
def test_feed_book(couchdb, db_name):
    from librocco.bookdata import feed_book

    book = {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "price": 9.99,
        "isbn": "9780316769488",
        "publisher": "Little, Brown and Company",
        "year": 1951,
    }
    feed_book(book, couchdb, db_name)

    # Fetch the document `books/9780316769488` from the database
    doc = couchdb.get_document(db=db_name, doc_id="books/9780316769488")
    assert doc
