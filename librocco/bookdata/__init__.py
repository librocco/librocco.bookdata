from ibm_cloud_sdk_core.api_exception import ApiException


def feed_book(book, couchdb, db_name):
    """Takes a dictionary with book data and a database connection.
    Checks if the book is already in the db. If it is, only the price will be updated.
    If it's not, a new document will be created.
    """
    doc_id = f"books/{book['isbn']}"
    # See if the book is already in the database
    try:
        doc = couchdb.get_document(db=db_name, doc_id=doc_id).get_result()
    except ApiException:
        doc = None

    if doc and doc["price"] != book["price"]:
        # Update the price
        doc["price"] = book["price"]
        couchdb.post_document(db=db_name, document=doc)
    elif not doc:
        # Create a new document
        couchdb.put_document(db=db_name, doc_id=doc_id, document=book)
