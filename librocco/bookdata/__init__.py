def feed_book(bookdata, dbconnection):
    """Takes a dictionary with book data and a database connection.
    Checks if the book is already in the db. If it is, only the price will be updated.
    If it's not, a new document will be created.
    """
