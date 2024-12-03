# Kent Tolzmann
# CS361 - Microservice A
# 11/18/24


def lms_microservice():
    print('LMS MICROSERVICE is running....')
    import zmq
    import json

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5554")

    users = []
    books = []
    messages = []

    while True:
        message = socket.recv()
        data = json.loads(message.decode())
        print(f"Received: {message}")
        operation = data[0]
        user_operations = [{'sign_up': True},
                           {'sign_in': True},
                           {'delete_user_id': True}
                           ]
        book_operations = [{'store_book': True},
                           {'borrow_book': True},
                           {'delete_book_id': True},
                           {'return_book': True},
                           {'delete_all_books': True}
                           ]

        # User Authentication
        if operation in user_operations:
            user = data[1]
            reply = user_authentication(operation, user, users)

        # Books CRUD Operations
        elif operation in book_operations:
            book = data[1]
            reply = book_ops(operation, book, books)

        # Message storing
        else:
            new_message = data[0]
            messages.append(new_message)
            reply = messages

        response = json.dumps(reply)
        socket.send(response.encode())
        print(f'Response: {response}')
        print(f"users:\n {users}")
        print(f"books:\n {books}")
        print()


def user_authentication(operation, user, users):
    # Add user
    if operation == {'sign_up': True}:
        print(f'USER SIGN UP')
        new_user = user
        for user in users:
            if new_user['username'] == user['username']:
                return [{'sign_up': 'username already exists'}]
        else:
            users.append(new_user)
            print(f'user login successful: {new_user["username"]}')
            return users

    # Authenticate user
    elif operation == {'sign_in': True}:
        print('USER SIGN IN')
        auth_user = user
        for user in users:
            if auth_user['username'] == user['username'] and auth_user['password'] == user['password']:
                return [{'sign_in': True}]
        else:
            return [{'sign_in': False}]

    # Delete user
    elif operation == {'delete_user_id': True}:
        print('DELETE USER')
        user_id = user
        for user in users:
            if user['id'] == user_id:
                users.remove(user)
                return users
        return [{'delete_user_id': 'user id not found'}]


def book_ops(operation, book, books):
    # Add book
    if operation == {'store_book': True}:
        print('STORE BOOK')
        new_book = book
        for book in books:
            if new_book['title'] == book['title']:
                return [{'store_book': 'book name already exists'}]
        else:
            books.append(new_book)
            return books

    # Borrow book
    elif operation == {'borrow_book': True}:
        print('BORROW BOOK')
        book_id = book
        for book in books:
            if book['id'] == book_id:
                book['available'] = False
                return books
        return [{'borrow_book': 'book id not found'}]

    # Delete book
    elif operation == {'delete_book_id': True}:
        print('DELETE BOOK ID')
        book_id = book
        for book in books:
            if book['id'] == book_id:
                books.remove(book)
                return books
        return [{'delete_book_id': 'book id not found'}]

    elif operation == {'delete_all_books': True}:
        print('DELETE ALL BOOKS')
        books.clear()
        return books

    elif operation == {'return_book': True}:
        book_id = book
        for book in books:
            if book['id'] == book_id:
                book['available'] = True
                return books
        return [{'borrow_book': 'book id not found'}]


lms_microservice()
