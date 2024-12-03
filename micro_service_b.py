# Microservice B: Book Returns and Overdue Alerts
import zmq
import json
from datetime import datetime, timedelta

# In-memory storage for borrowed books
borrowed_books = []

def borrowed_books_service():
    """
    Microservice B: Manages borrowed books.
    Operations:
        - get_borrowed_books: Fetch the list of books borrowed by a specific user.
        - borrow_book: Add a book to the borrowed list with a due date.
        - return_book: Remove a book from the borrowed list.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")  # Bind to port 5556 for Microservice B

    print("Microservice B (Borrowed Books Management) is running...")

    while True:
        # Receive the request
        message = socket.recv()
        data = json.loads(message.decode())
        operation = data[0]  # Operation type
        payload = data[1]    # Data sent with the request

        # Handle operations
        if operation == "get_borrowed_books":
            response = handle_get_borrowed_books(payload)

        if operation =="get_history_borrowed_books":
            response = handle_get_history_borrowed_books(payload)
        
        elif operation == "borrow_book":
            response = handle_borrow_book(payload)

        elif operation == "return_book":
            response = handle_return_book(payload)

        elif operation == "check_overdue_books":
            response = handle_check_overdue_books(payload)
        else:
            response = {"status": "error", "message": "Invalid operation"}

        # Send the response
        socket.send(json.dumps(response).encode())

def handle_get_history_borrowed_books(user_id):
    """
    Fetch the list of books borrowed by a specific user.
    :param user_id: The ID of the user.
    :return: A response containing the list of borrowed books.
    """
    user_books = [book for book in borrowed_books if book["user_id"] == user_id]
    return {"status": "success", "borrowed_books": user_books}


def handle_get_borrowed_books(user_id):
    """
    Fetch the list of books borrowed by a specific user.
    :param user_id: The ID of the user.
    :return: A response containing the list of borrowed books.
    """
    user_books = [book for book in borrowed_books if book["user_id"] == user_id and book['status'] == "borrowed"]
    for book in borrowed_books:
        print(book)
    return {"status": "success", "borrowed_books": user_books}
    

def handle_borrow_book(book_data):
    """
    Add a book to the borrowed books list with a due date.
    :param book_data: A dictionary containing user_id, book_id, title, borrowed_date, and due_date.
    :return: A response indicating success or failure.
    """
    for book in borrowed_books:
        if book["user_id"] == book_data["user_id"] and book["book_id"] == book_data["book_id"]:
            return {"status": "error", "message": "Book already borrowed"}

    # Calculate due date (e.g., 7 days from borrowed_date)
    borrowed_date = datetime.now()
    due_date = borrowed_date + timedelta(days=7)

    book_data["borrowed_date"] = borrowed_date.strftime("%Y-%m-%d")
    book_data["due_date"] = due_date.strftime("%Y-%m-%d")
    book_data["status"] = "borrowed" 
    borrowed_books.append(book_data)
    print("Current borrowed_books list after borrow operation:")
    for book in borrowed_books:
        print(book)
    return {"status": "success", "message": "Book borrowed successfully", "due_date": book_data["due_date"]}

def handle_return_book(return_data):
    """
    Remove a book from the borrowed books list.
    :param return_data: A dictionary containing user_id and book_id.
    :return: A response indicating success or failure.
    """
    for book in borrowed_books:
        if book["user_id"] == return_data["user_id"] and book["book_id"] == return_data["book_id"]:
            book["status"] = "returned"
            borrowed_books.remove(book)
            return {"status": "success", "message": "Book returned successfully"}

    return {"status": "error", "message": "Book not found in borrowed list"}

def handle_check_overdue_books(user_id):
    """
    Check if the user has any overdue books.
    :param user_id: The ID of the user.
    :return: A response containing overdue books or a message if no overdue books are found.
    """
    overdue_books = []
    today = datetime.now().date()

    for book in borrowed_books:
        if book["user_id"] == user_id:
            due_date = datetime.strptime(book["due_date"], "%Y-%m-%d").date()
            if today > due_date:
                overdue_books.append(book)

    if overdue_books:
        return {"status": "alert", "message": "You have overdue books!", "overdue_books": overdue_books}
    else:
        return {"status": "success", "message": "No overdue books."}

if __name__ == "__main__":
    borrowed_books_service()
