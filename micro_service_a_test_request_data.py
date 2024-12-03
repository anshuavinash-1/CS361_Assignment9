# Author: Kent Tolzmann
# CS361 Test program for Microservice A
# 11/18/2024


def get_micro_response(json_obj):
    import zmq
    import json
    context = zmq.Context()

    print("Connecting to Microservice A server...")
    print()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5554")

    response = json.dumps(json_obj)
    socket.send(response.encode())
    print(f'Sent Request:\n {response}')
    print()

    message = socket.recv()
    print(f"Received Reply:\n {message.decode()}")
    json_obj_message = json.loads(message.decode())
    return json_obj_message



if __name__ == "__main__":
    import time
    delay = 0
    # example requests
    print("Test program running...")
    input()
    print('SIGN UP NEW USER')
    operation1 = [{'sign_up': True},
                  {'username': 'John_Doe',
                   'password': 'password123',
                   'email': 'user@example.com',
                   'id': 4
                   }]
    get_micro_response(operation1)

    input()
    time.sleep(delay)
    print('SIGN UP NEW USER')
    operation2 = [{'sign_up': True},
                  {'username': 'John_Deer',
                   'password': 'password890',
                   'email': 'Deer@example.com',
                   'id': 5
                   }]
    get_micro_response(operation2)

    input()
    time.sleep(delay)
    print('SIGN IN USER with wrong password')
    operation3 = [{'sign_in': True},
                  {'username': 'John_Doe',
                   'password': 'wrong password'
                   }]
    get_micro_response(operation3)

    input()
    time.sleep(delay)
    print('SIGN IN USER')
    operation4 = [{'sign_in': True},
                  {'username': 'John_Doe',
                   'password': 'password123'
                   }]
    get_micro_response(operation4)

    input()
    time.sleep(delay)
    print('DELETE USER ID')
    operation4a = [{'delete_user_id': True}, 4]
    get_micro_response(operation4a)

    input()
    time.sleep(delay)
    print('STORE BOOK')
    operation5 = [{'store_book': True},
                  {'title': 'New Book',
                   'author': 'Author Name',
                   'id': 4,
                   'isbn': 'ISBN004',
                   'available': True
                   }]
    get_micro_response(operation5)

    input()
    time.sleep(delay)
    print('STORE BOOK')
    operation6 = [{'store_book': True},
                  {'title': 'Another Book',
                   'author': 'Author B',
                   'id': 5,
                   'isbn': 'ISBN005',
                   'available': True
                   }]
    get_micro_response(operation6)

    input()
    time.sleep(delay)
    print('STORE BOOK That already exists')
    operation7 = [{'store_book': True},
                  {'title': 'New Book',
                   'author': 'Author Name',
                   'id': 4,
                   'isbn': 'ISBN004',
                   'available': True
                   }]
    get_micro_response(operation7)

    input()
    time.sleep(delay)
    print('BORROW BOOK')
    operation8 = [{'borrow_book': True}, 4]
    get_micro_response(operation8)

    input()
    time.sleep(delay)
    print('RETURN BOOK')
    operation9 = [{'return_book': True}, 4]
    get_micro_response(operation9)

    input()
    time.sleep(delay)
    print('DELETE BOOK ID')
    operation10 = [{'delete_book_id': True}, 4]
    get_micro_response(operation10)

    input()
    time.sleep(delay)
    print('DELETE ALL BOOKS')
    operation10 = [{'delete_all_books': True}, None]
    get_micro_response(operation10)

    input()
    time.sleep(delay)
    print('CREATE MESSAGE')
    operation11 = [{'key1': 'valueA', 'key2': 'valueB', 'id': 100}]
    get_micro_response(operation11)
