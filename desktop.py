import tkinter as tk
from tkinter import messagebox
from tkmacosx import Button
import zmq
import json
from datetime import datetime, timedelta

# Communicate with microservices
def communicate_with_microservice(port, operation, data=None):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")
    request = [operation, data]
    socket.send(json.dumps(request).encode())
    response = socket.recv()
    return json.loads(response.decode())

# Placeholder management for Entry fields
def setup_entry_with_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", lambda e: e.widget.delete(0, tk.END) if e.widget.get() == placeholder else None)
    entry.bind("<FocusOut>", lambda e, ph=placeholder: e.widget.insert(0, ph) if not e.widget.get() else None)

# Main Application Class
class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f7f7f7")
        self.user_borrowed_books = []  # List of books borrowed by the user
        self.current_user = None  # Current user's ID

        # Show the first screen
        self.show_first_screen()

    def clear_screen(self):
        """Clear all widgets from the screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_first_screen(self):
        """Show the initial screen with Login and Register options."""
        self.clear_screen()

        # Title
        tk.Label(
            self.root,
            text="Welcome to the Library System",
            font=("Helvetica", 24, "bold"),
            bg="#f7f7f7",
            fg="#333"
        ).pack(pady=50)

        # Login Button
        Button(
            self.root,
            text="Login",
            font=("Helvetica", 16),
            bg="#4CAF50",
            fg="white",
            command=self.show_login_screen,
            borderless=1
        ).pack(pady=10)

        # Register Button
        Button(
            self.root,
            text="Register",
            font=("Helvetica", 16),
            bg="#2196F3",
            fg="white",
            command=self.show_register_screen,
            borderless=1
        ).pack(pady=10)

    def show_login_screen(self):
        """Show the login screen."""
        self.clear_screen()

        tk.Label(
            self.root,
            text="Login",
            font=("Helvetica", 24, "bold"),
            bg="#f7f7f7",
            fg="#333"
        ).pack(pady=20)

        email = tk.StringVar()
        password = tk.StringVar()

        tk.Label(self.root, text="Email:", bg="#f7f7f7").pack(pady=5)
        email_entry = tk.Entry(self.root, textvariable=email, font=("Helvetica", 14), bd=2, relief="solid")
        email_entry.pack(pady=5, padx=50, fill="x")

        tk.Label(self.root, text="Password:", bg="#f7f7f7").pack(pady=5)
        password_entry = tk.Entry(self.root, textvariable=password, font=("Helvetica", 14), bd=2, relief="solid", show="*")
        password_entry.pack(pady=5, padx=50, fill="x")

        def login():
            """Handle login functionality."""
            response = communicate_with_microservice(5554, {'sign_in': True}, {"username": email.get(), "password": password.get()})
            if response and response[0].get("sign_in"):
                self.current_user = email.get()
                messagebox.showinfo("Success", "Login successful!")
                self.get_user_borrowed_books()  # Fetch the borrowed books after login
                self.show_overdue_alerts()  
                self.show_book_list_screen()
            else:
                messagebox.showerror("Error", "Invalid credentials!")

        Button(
            self.root,
            text="Login",
            font=("Helvetica", 14),
            bg="#4CAF50",
            fg="white",
            command=login,
            borderless=1
        ).pack(pady=20)

        Button(
            self.root,
            text="Back",
            font=("Helvetica", 14),
            bg="#FF5722",
            fg="white",
            command=self.show_first_screen,
            borderless=1
        ).pack(pady=10)
    
    def show_register_screen(self):
        """Show the registration screen."""
        self.clear_screen()

        tk.Label(
            self.root,
            text="Register",
            font=("Helvetica", 24, "bold"),
            bg="#f7f7f7",
            fg="#333"
        ).pack(pady=20)

        email = tk.StringVar()
        password = tk.StringVar()
        confirm_password = tk.StringVar()

        tk.Label(self.root, text="Email:", bg="#f7f7f7").pack(pady=5)
        email_entry = tk.Entry(self.root, textvariable=email, font=("Helvetica", 14), bd=2, relief="solid")
        email_entry.pack(pady=5, padx=50, fill="x")

        tk.Label(self.root, text="Password:", bg="#f7f7f7").pack(pady=5)
        password_entry = tk.Entry(self.root, textvariable=password, font=("Helvetica", 14), bd=2, relief="solid", show="*")
        password_entry.pack(pady=5, padx=50, fill="x")

        tk.Label(self.root, text="Confirm Password:", bg="#f7f7f7").pack(pady=5)
        confirm_password_entry = tk.Entry(self.root, textvariable=confirm_password, font=("Helvetica", 14), bd=2, relief="solid", show="*")
        confirm_password_entry.pack(pady=5, padx=50, fill="x")

        def register():
            if password.get() != confirm_password.get():
                messagebox.showerror("Error", "Passwords do not match!")
                return

            response = communicate_with_microservice(5554, {'sign_up': True}, {"username": email.get(), "password": password.get()})
            if response and response[0].get("sign_up") == "username already exists":
                messagebox.showerror("Error", "Email already registered!")
            else:
                messagebox.showinfo("Success", "Registration successful!")
                self.show_login_screen()

        Button(
            self.root,
            text="Register",
            font=("Helvetica", 14),
            bg="#4CAF50",
            fg="white",
            command=register,
            borderless=1
        ).pack(pady=20)

        Button(
            self.root,
            text="Back",
            font=("Helvetica", 14),
            bg="#FF5722",
            fg="white",
            command=self.show_first_screen,
            borderless=1
        ).pack(pady=10)

    def get_user_borrowed_books(self):
        """Fetch the list of borrowed books for the current user."""
        # Fetch borrowed books from Microservice B ( user_id is self.current_user)
        response = communicate_with_microservice(5556, "get_borrowed_books", self.current_user)
        if response.get("status") == "success":
            self.user_borrowed_books = [book["book_id"] for book in response["borrowed_books"]]  # Save borrowed book IDs
        else:
            self.user_borrowed_books = []
    def show_return_book_screen(self):
            """Show the Return Book screen where the user can return borrowed books."""
            self.clear_screen()

            tk.Label(self.root, text="Return Book", font=("Helvetica", 24, "bold"), bg="#f7f7f7", fg="#333").pack(pady=20)

            # Fetch the borrowed books for the current user
         
            response = communicate_with_microservice(5558, "get_borrowing_history", self.current_user)
            borrowed_books = response.get("borrowed_books", [])

            # Display borrowed books in a table with Borrowed Date and Due Date
            table_frame = tk.Frame(self.root, bg="#f7f7f7")
            table_frame.pack(pady=10, fill="both", expand=True)

            tk.Label(table_frame, text="Book Id", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(table_frame, text="Book Name", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=1, padx=10, pady=5, sticky="w")
            tk.Label(table_frame, text="Borrowed Date", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=2, padx=10, pady=5, sticky="w")
            tk.Label(table_frame, text="Due Date", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=3, padx=10, pady=5, sticky="w")
            tk.Label(table_frame, text="Action", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=4, padx=10, pady=5, sticky="w")

            for i, book in enumerate(borrowed_books):
                tk.Label(table_frame, text=book['book_id'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")
                tk.Label(table_frame, text=book['title'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=1, padx=10, pady=5, sticky="w")
                tk.Label(table_frame, text=book['borrowed_date'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=2, padx=10, pady=5, sticky="w")
                tk.Label(table_frame, text=book['due_date'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=3, padx=10, pady=5, sticky="w")

                action_button = Button(
                    table_frame,
                    text="Return Book",
                    font=("Helvetica", 12),
                    bg="#FF5722",
                    fg="white",
                    command=lambda b=book: self.return_book(b),  # Function to return the book
                    borderless=1
                )
                action_button.grid(row=i + 1, column=4, padx=10, pady=5, sticky="w")

            # Back button
            Button(self.root, text="Back", font=("Helvetica", 14), bg="#FF5722", fg="white", command=self.show_book_list_screen, borderless=1).pack(pady=20)
    def show_borrowing_history_screen(self):
        """Show the borrowing history screen."""
        self.clear_screen()
        print(f"Fetching borrowing history for user: {self.current_user}")
        tk.Label(self.root, text="Borrowing History", font=("Helvetica", 24, "bold"), bg="#f7f7f7", fg="#333").pack(pady=20)

        # Fetch the borrowing history for the current user
        response = communicate_with_microservice(5558, "get_borrowing_history", self.current_user)
        borrowed_books = response.get("borrowed_books", [])

        # Display borrowing history in a table
        table_frame = tk.Frame(self.root, bg="#f7f7f7")
        table_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(table_frame, text="Book Name", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(table_frame, text="Borrowed Date", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=1, padx=10, pady=5, sticky="w")

        for i, book in enumerate(borrowed_books):
            tk.Label(table_frame, text=book['title'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")
            tk.Label(table_frame, text=book['borrowed_date'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=1, padx=10, pady=5, sticky="w")

        # Back button
        Button(self.root, text="Back", font=("Helvetica", 14), bg="#FF5722", fg="white", command=self.show_book_list_screen, borderless=1).pack(pady=20)
    def show_overdue_alerts(self):
        """Check and display overdue books for the current user."""
        response = communicate_with_microservice(5556, "check_overdue_books", self.current_user)

        if response.get("status") == "alert":
            overdue_books = response.get("overdue_books", [])
            overdue_titles = ", ".join([book["title"] for book in overdue_books])
            messagebox.showwarning("Overdue Books Alert", f"You have overdue books: {overdue_titles}. Please return them.")
        elif response.get("status") == "success":
            messagebox.showinfo("No Overdue Books", "You have no overdue books!")
        else:
            messagebox.showerror("Error", response.get("message", "Failed to fetch overdue alerts."))

    def return_book(self, book):
        """Return a borrowed book and update both Microservice D and Microservice C."""
        user_id = self.current_user
        # First call Microservice D to mark the book as available (return it)
        response_d = communicate_with_microservice(5557, "return_book", book["book_id"])  # Use port 5557 for Microservice D
        if response_d.get("status") == "success":
            # Now call Microservice B to update the borrowing history
            return_data = {"user_id": user_id, "book_id": book["book_id"]}
            response_c = communicate_with_microservice(5556, "return_book", return_data)  # Use port 5558 for Microservice C
            if response_c.get("status") == "success":
                messagebox.showinfo("Success", f"You have returned '{book['title']}'!")
                self.show_book_list_screen()  # Refresh the book list after returning the book
            else:
                messagebox.showerror("Error", response_c.get("message", "Failed to update borrowing history."))
        else:
            messagebox.showerror("Error", response_d.get("message", "Failed to return the book in Microservice D."))

    def show_book_list_screen(self):
        """Show the book list screen."""
        self.clear_screen()

        # Title
        tk.Label(self.root, text="Book List", font=("Helvetica", 24, "bold"), bg="#f7f7f7", fg="#333").pack(pady=20)

        # Search Bar
        search_var = tk.StringVar()

        # Create a frame to hold the search bar and button
        search_frame = tk.Frame(self.root, bg="#f7f7f7")
        search_frame.pack(pady=10, fill="x", padx=50)

        # Search Bar (with adjusted width)
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Helvetica", 14), bd=2, relief="solid", width=25)
        search_entry.pack(side="left", padx=5)

        # Search Button
        def search_books():
            """Fetch and display books based on the search query."""
            query = search_var.get()
            response = communicate_with_microservice(5557, "search_books", query)
            books = response.get("books", [])
            display_books(books)

        search_button = Button(
            search_frame,
            text="Search",
            font=("Helvetica", 14),
            bg="#4CAF50",
            fg="white",
            command=search_books,
            borderless=1
        )
        search_button.pack(side="left", padx=5)


        # Table Headers
        table_frame = tk.Frame(self.root, bg="#f7f7f7")
        table_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(table_frame, text="Book Name", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(table_frame, text="Author Name", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        tk.Label(table_frame, text="Action", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333").grid(row=0, column=2, padx=10, pady=5, sticky="w")

        def display_books(books):
            """Display books in a table format."""
            # Clear previous rows
            for widget in table_frame.winfo_children():
                if widget.grid_info()["row"] > 0:
                    widget.destroy()

            for i, book in enumerate(books):
                tk.Label(table_frame, text=book['title'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")
                tk.Label(table_frame, text=book['author'], font=("Helvetica", 12), bg="#f7f7f7", fg="#555").grid(row=i + 1, column=1, padx=10, pady=5, sticky="w")

                if book["available"]:
                    # Check if the user has already borrowed the book
                    if book["id"] in self.user_borrowed_books:
                        action_button = Button(
                            table_frame,
                            text="Borrowed",
                            font=("Helvetica", 12),
                            bg="#BDBDBD",
                            fg="white",
                            state="disabled",
                            borderless=1
                        )
                    else:
                        action_button = Button(
                            table_frame,
                            text="Borrow Book",
                            font=("Helvetica", 12),
                            bg="#4CAF50",
                            fg="white",
                            command=lambda b=book: borrow_book(b),
                            borderless=1
                        )
                else:
                    # Book is not available (already borrowed), show "Reserve Book" if not borrowed by current user
                    if book["id"] in self.user_borrowed_books:
                        action_button = Button(
                            table_frame,
                            text="Borrowed",
                            font=("Helvetica", 12),
                            bg="#BDBDBD",
                            fg="white",
                            state="disabled",
                            borderless=1
                        )
                    else:
                        action_button = Button(
                            table_frame,
                            text="Reserve Book",
                            font=("Helvetica", 12),
                            bg="#FF9800",
                            fg="white",
                            command=lambda b=book: reserve_book(b),
                            borderless=1
                        )

                action_button.grid(row=i + 1, column=2, padx=10, pady=5, sticky="w")

        def borrow_book(book):
            """Borrow a book and update both Microservice D and Microservice B."""

           
    
            user_id = self.current_user
            # Call Microservice D to mark the book as borrowed
            response_d = communicate_with_microservice(5557, "borrow_book", book["id"])
            if response_d.get("status") == "success":
                response_b = communicate_with_microservice(5556, "borrow_book", {
                    "user_id": user_id,
                    "book_id": book["id"],
                    "title": book["title"],
                    "borrowed_date": "2024-11-02",  # Example date
                    "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                })
                if response_b.get("status") == "success":
                    messagebox.showinfo("Success", f"You have borrowed '{book['title']}'!")
                    refresh_books()
                else:
                    messagebox.showerror("Error", response_b.get("message", "Failed to borrow book."))
            else:
                messagebox.showerror("Error", response_d.get("message", "Failed to borrow book."))

        def reserve_book(book):
            """Reserve a book and update Microservice D."""
            response = communicate_with_microservice(5557, "reserve_book", book["id"])
            if response.get("status") == "success":
                messagebox.showinfo("Success", f"You have reserved '{book['title']}'!")
                refresh_books()  # Refresh the book list
            else:
                messagebox.showerror("Error", response.get("message", "Failed to reserve book."))

        def refresh_books():
            """Fetch and display updated book list."""
            response = communicate_with_microservice(5557, "get_books")
            books = response.get("books", [])
            display_books(books)


        # Fetch and display all books initially
        refresh_books()
        
        button_frame = tk.Frame(self.root, bg="#f7f7f7")
        button_frame.pack(pady=10)

        # Add the "Return Book" button
        Button(
            button_frame,
            text="Return Book",
            font=("Helvetica", 14),
            bg="#FF5722",
            fg="white",
            command=self.show_return_book_screen,  # Function to handle return book screen
            borderless=1
        ).grid(row=0, column=0, padx=10)

        # Add the "Borrowing History" button
        Button(
            button_frame,
            text="Borrowing History",
            font=("Helvetica", 14),
            bg="#4CAF50",
            fg="white",
            command=self.show_borrowing_history_screen,  # Function to show borrowing history
            borderless=1
        ).grid(row=0, column=1, padx=10)

        # Add the "Logout" button
        Button(
            button_frame,
            text="Logout",
            font=("Helvetica", 14),
            bg="#FF5722",
            fg="white",
            command=self.show_first_screen,  # Function to handle logout
            borderless=1
        ).grid(row=0, column=2, padx=10)
      

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
