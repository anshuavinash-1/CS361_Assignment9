# Microservice D: Book Search and Reservation
import zmq
import json

#  in-memory book database
books = [
    {"id": 1, "title": "The Hunger Games", "author": "Suzanne Collins", "available": True, "reserved": False},
    {"id": 2, "title": "Dune", "author": "Frank Herbert", "available": True, "reserved": False},
    {"id": 3, "title": "1989", "author": "Maya Taeli", "available": True, "reserved": False},
    {"id": 4, "title": "Half Girlfriend", "author": "Chetan Bhagat", "available": True, "reserved": False},
    {"id": 5, "title": "Macbeth", "author": "William Shakespeare", "available": True, "reserved": False},
    {"id": 6, "title": "The Merchant of Venice", "author": "William Shakespeare", "available": True, "reserved": False},
    {"id": 7, "title": "Mein Kamph", "author": "Adolf Hitler", "available": True, "reserved": False},
    {"id": 8, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available": True, "reserved": False},
    {"id": 9, "title": "Treasure Island", "author": "R.L. Stevenson", "available": True, "reserved": False},  # Reserved by someone
    {"id": 10, "title": "1984", "author": "George Orwell", "available": False, "reserved": True},  # Reserved by someone
]


def book_service():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5557")  # Bind to port 5557 for book microservice

    print("Microservice D (Book Service) is running...")

    while True:
        message = socket.recv()
        data = json.loads(message.decode())
        operation = data[0]  # Operation type
        payload = data[1]    # Data sent with the request

        if operation == "get_books":
            # Return the list of books
            response = {"books": books}

        elif operation == "search_books":
            # Search for books by title or author
            query = payload.lower()
            results = [book for book in books if query in book["title"].lower() or query in book["author"].lower()]
            response = {"books": results}

        elif operation == "borrow_book":
            # Borrow a book
            book_id = payload
            book = next((b for b in books if b["id"] == book_id), None)
            if book and book["available"]:
                book["available"] = False
                response = {"status": "success", "message": "Book marked as borrowed"}
            else:
                response = {"status": "error", "message": "Book not available"}
                

        elif operation == "reserve_book":
            # Reserve a book
            book_id = payload
            book = next((b for b in books if b["id"] == book_id), None)
            if book:
                if not book["available"] and not book["reserved"]:
                    # Reserve the book
                    book["reserved"] = True
                    response = {"status": "success", "message": "Book reserved successfully"}
                elif book["reserved"]:
                    response = {"status": "error", "message": "Book is already reserved"}
                else:
                    response = {"status": "error", "message": "Book is available, no need to reserve"}
            else:
                response = {"status": "error", "message": "Book not found"}
        elif operation == "return_book":
            # Return a borrowed book
            book_id = payload  # Payload is the book id
            book = next((b for b in books if b["id"] == book_id), None)
            if book:
                book["available"] = True  # Mark the book as available
                response = {"status": "success", "message": "Book returned successfully"}
            else:
                response = {"status": "error", "message": "Book not found"}



        else:
            response = {"status": "error", "message": "Invalid operation"}

        socket.send(json.dumps(response).encode())
if __name__ == "__main__":
    book_service()
