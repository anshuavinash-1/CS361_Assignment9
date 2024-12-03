import zmq
import json

# In-memory database for borrowing history
borrowing_history = []

def communicate_with_microservice(port, operation, data=None):
    """Helper function to communicate with other microservices."""
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")
    request = [operation, data]
    socket.send(json.dumps(request).encode())
    response = socket.recv()
    return json.loads(response.decode())

def borrowing_history_service():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5558")  # Bind to port 5558 for borrowing history microservice

    print("Microservice C (Borrowing History Service) is running...")

    while True:
        message = socket.recv()
        data = json.loads(message.decode())
        operation = data[0]  # Operation type
        payload = data[1]    # Data sent with the request

        if operation == "get_borrowing_history":
            # Fetch borrowing history for the user
            user_id = payload
            response_b = communicate_with_microservice(5556, "get_history_borrowed_books", user_id)  # Fetch books from Microservice B

            if response_b.get("status") == "success":
                # Modify the borrowed books' status to 'returned' if already returned
                for book in response_b["borrowed_books"]:
                    if book["status"] == "returned":
                        # Add book to borrowing history with a status
                        borrowing_history.append(book)

                response = {"status": "success", "borrowed_books": response_b["borrowed_books"]}

            else:
                response = {"status": "error", "message": "Failed to fetch borrowing history from Microservice B"}
        elif operation == "get_borrowing_books":
            # Fetch borrowing history for the user
            user_id = payload
            response_b = communicate_with_microservice(5556, "get_borrowed_books", user_id)  # Fetch books from Microservice B

            if response_b.get("status") == "success":
              
                borrowing_history.append(book)

                response = {"status": "success", "borrowed_books": response_b["borrowed_books"]}

            else:
                response = {"status": "error", "message": "Failed to fetch borrowing history from Microservice B"}

        else:
            response = {"status": "error", "message": "Invalid operation"}

        socket.send(json.dumps(response).encode())

if __name__ == "__main__":
    borrowing_history_service()
