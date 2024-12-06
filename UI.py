import tkinter as tk
from tkinter import messagebox
from datetime import date # for working with dates
from data_layer import *
from business_model import *  # Importing everything from business_model

class AdventureLandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adventure Land Theme Park")
        self.root.geometry("1000x800")
        self.logged_in_user = None
        self.logged_in_admin = None
        self.data_layer = DataLayer()  # Use DataLayer for persistence
        self.data = self.data_layer.load_all()  # Load all entities
        self.business_model = self  # Use the current class to interact with the business model methods
        self.fix_checkout_cart()  # Call the fix_checkout_cart method
        self.create_login_page()
        self.data_layer.initialize_files()
    def fix_checkout_cart(self):
        def checkout_cart():
            current_customer = self.get_logged_in_customer(self.logged_in_user.get_username())
            if not current_customer:
                messagebox.showerror("Error", "No customer is logged in.")
                return
            cart = current_customer.get_cart()
            items = cart.get_cart_items()
            if not items:
                messagebox.showerror("Error", "Your cart is empty.")
                return

            if hasattr(self,
                       'payment_window') and self.payment_window is not None and self.payment_window.winfo_exists():
                messagebox.showinfo("Info", "Payment window is already open.")
                return

            self.payment_window = tk.Toplevel(self.root)
            self.payment_window.title("Payment")
            self.payment_window.geometry("400x450")

            # Payment Details UI
            tk.Label(self.payment_window, text="Enter Payment Details", font=("Arial", 14)).pack(pady=10)

            # Payment Method Selection
            tk.Label(self.payment_window, text="Select Payment Method:").pack(pady=5)
            payment_method = tk.StringVar(value="Credit Card")  # Default to Credit Card
            tk.Radiobutton(self.payment_window, text="Credit Card", variable=payment_method, value="Credit Card").pack(
                pady=5)
            tk.Radiobutton(self.payment_window, text="Debit Card", variable=payment_method, value="Debit Card").pack(
                pady=5)

            # Card Number
            tk.Label(self.payment_window, text="Card Number:").pack(pady=5)
            card_number_entry = tk.Entry(self.payment_window)
            card_number_entry.pack(pady=5)

            # Expiration Date
            tk.Label(self.payment_window, text="Expiration Date (MM/YY):").pack(pady=5)
            expire_date_entry = tk.Entry(self.payment_window)
            expire_date_entry.pack(pady=5)

            # CCV
            tk.Label(self.payment_window, text="CCV:").pack(pady=5)
            ccv_entry = tk.Entry(self.payment_window)
            ccv_entry.pack(pady=5)

            def process_payment():
                card_number = card_number_entry.get()
                expire_date = expire_date_entry.get()
                ccv = ccv_entry.get()
                amount = sum(ticket.get_price() for ticket in items)

                # Validate card number
                if not card_number.isdigit() or len(card_number) < 12:
                    messagebox.showerror("Error", "Invalid card number. Please enter a valid card number.")
                    return

                # Validate expiration date
                if not expire_date or len(expire_date) != 5 or '/' not in expire_date:
                    messagebox.showerror("Error", "Invalid expiration date. Please use MM/YY format.")
                    return

                # Validate CCV
                if not ccv.isdigit() or len(ccv) != 3:
                    messagebox.showerror("Error", "Invalid CCV. Please enter a 3-digit CCV.")
                    return

                # Handle Payment Logic
                payment_type = payment_method.get()
                if payment_type == "Debit Card":
                    # Additional Debit Card validation logic (if any) can go here
                    if not card_number.startswith("4"):  # Example: Only accept cards starting with '4' for Debit
                        messagebox.showerror("Error", "Invalid Debit Card number.")
                        return

                # Create Payment and Order
                payment = Payment(payment_method=payment_type, amount=amount)
                new_order = Order(
                    purchase_date=date.today(),
                    status=Status.Paid,
                    tickets=items,
                    payment=payment
                )

                # Save to customer's history and data layer
                current_customer.add_order_to_history(new_order)
                self.data["orders"].append(new_order)
                self.data_layer.save_customers(self.data["customers"])
                self.data_layer.save_orders(self.data["orders"])

                # Clear the cart and close the window
                cart.clear_cart()
                self.payment_window.destroy()
                self.payment_window = None
                messagebox.showinfo("Success",
                                    f"Payment completed successfully using {payment_type}!\nTotal Price: {new_order.get_total_price():.2f} AED.")
                self.show_home_page("customer")

            # Payment Buttons
            tk.Button(self.payment_window, text="Pay", command=process_payment).pack(pady=20)
            tk.Button(self.payment_window, text="Cancel", command=lambda: self.payment_window.destroy()).pack()

        # Assign the updated checkout_cart method
        self.checkout_cart = checkout_cart
        # Update the app's checkout_cart method
        self.checkout_cart = checkout_cart

    def show_home_page(self, user_type):
        # Check if the user type is valid and redirect appropriately
        if user_type == "customer":
            self.create_customer_home()
        elif user_type == "admin":
            self.create_admin_home()
        else:
            # Log out or return to login
            self.create_login_page()


    def create_login_page(self):

        # Set a new optimized window size
        self.root.geometry("380x400")

        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Login Page Layout
        tk.Label(self.root, text="Adventure Land Login", font=("Arial", 18), anchor="center").grid(row=0, column=0, columnspan=3, pady=20)
        tk.Label(self.root, text="Username:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        username_entry = tk.Entry(self.root, font=("Arial", 12))
        username_entry.grid(row=1, column=1, pady=10, ipadx=10)
        tk.Label(self.root, text="Password:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        password_entry.grid(row=2, column=1, pady=10, ipadx=10)
        tk.Label(self.root, text="Login As:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        user_type = tk.StringVar(value="customer")  # Default to customer
        tk.Radiobutton(self.root, text="Customer", variable=user_type, value="customer", font=("Arial", 12)).grid(row=3, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Admin", variable=user_type, value="admin", font=("Arial", 12)).grid(row=3, column=2, sticky="w")
        def validate_login():
            username = username_entry.get()
            password = password_entry.get()
            if user_type.get() == "customer":
                for customer in self.data["customers"]:
                    if customer.get_username() == username and customer.validate_password(password):
                        self.logged_in_user = customer
                        messagebox.showinfo("Login Success", "Welcome Customer!")
                        self.show_home_page("customer")
                        return
                messagebox.showerror("Login Failed", "Invalid username or password for customer.")
            elif user_type.get() == "admin":
                for admin in self.data["admins"]:
                    if admin.get_admin_id() == username and admin.validate_password(password):
                        self.logged_in_admin = admin
                        messagebox.showinfo("Login Success", "Welcome Admin!")
                        self.show_home_page("admin")
                        return
                messagebox.showerror("Login Failed", "Invalid username or password for admin.")
        # Buttons
        tk.Button(self.root, text="Log In", command=validate_login, font=("Arial", 12), width=15).grid(row=4, column=1, pady=20, ipadx=5, ipady=5)
        tk.Button(self.root, text="Sign Up", command=self.create_signup_page, font=("Arial", 12), width=15).grid(row=5, column=1, pady=5, ipadx=5, ipady=5)
    def create_signup_page(self):
        # Set a new optimized window size
        self.root.geometry("600x450")
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Sign-Up Page Layout
        tk.Label(self.root, text="Adventure Land Sign-Up", font=("Arial", 18)).grid(row=0, column=1, pady=20)
        tk.Label(self.root, text="Username:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        username_entry = tk.Entry(self.root, font=("Arial", 12))
        username_entry.grid(row=1, column=1, pady=10, ipadx=10)
        tk.Label(self.root, text="Password:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        password_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        password_entry.grid(row=2, column=1, pady=10, ipadx=10)
        tk.Label(self.root, text="Email:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        email_entry = tk.Entry(self.root, font=("Arial", 12))
        email_entry.grid(row=3, column=1, pady=10, ipadx=10)
        tk.Label(self.root, text="Sign Up As:", font=("Arial", 12)).grid(row=4, column=0, sticky="e", padx=10, pady=10)
        user_type = tk.StringVar(value="customer")  # Default to customer
        tk.Radiobutton(self.root, text="Customer", variable=user_type, value="customer", font=("Arial", 12)).grid(row=4, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Admin", variable=user_type, value="admin", font=("Arial", 12)).grid(row=4, column=2, sticky="w")
        def register_account():
            username = username_entry.get()
            password = password_entry.get()
            email = email_entry.get()
            if user_type.get() == "customer":
                try:
                    # Create a new CustomerAccount and validate it
                    customer = CustomerAccount(username=username, password=password, email=email, purchase_date=date.today(), tickets=[])
                    customer.validate_account_creation()  # Business Model
                    self.data["customers"].append(customer)  # Add the customer to the in-memory data
                    self.data_layer.save_customers(self.data["customers"])  # Save updated customers list
                    messagebox.showinfo("Sign Up Successful", "Customer account created successfully!")
                    self.create_login_page()
                except ValueError as e:
                    messagebox.showerror("Sign Up Failed", str(e))
            elif user_type.get() == "admin":
                try:
                    # Create a new Admin account and validate it
                    admin = Admin(admin_id=username, password=password, orders=[])
                    admin.validate_admin_creation()  # Business Model
                    self.data["admins"].append(admin)  # Add the admin to the in-memory data
                    self.data_layer.save_admins(self.data["admins"])  # Save updated admins list
                    messagebox.showinfo("Sign Up Successful", "Admin account created successfully!")
                    self.create_login_page()
                except ValueError as e:
                    messagebox.showerror("Sign Up Failed", str(e))
        # Buttons
        tk.Button(self.root, text="Sign Up", command=register_account, font=("Arial", 12), width=15).grid(row=5, column=1, pady=20, ipadx=5, ipady=5)
        tk.Button(self.root, text="Back to Login", command=self.create_login_page, font=("Arial", 12), width=15).grid(row=6, column=1, pady=10, ipadx=5, ipady=5)
    def get_logged_in_customer(self, username):
        for customer in self.data["customers"]:
            if customer.get_username() == username:
                return customer
        return None  # Return None if no matching customer is found
    def create_customer_home(self):
        self.root.geometry("500x500")  # Adjust the window size
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Title
        tk.Label(self.root,text="Customer Home Page",font=("Arial", 20, "bold"),anchor="center").pack(pady=20)
        # Buttons layout
        buttons = [("About", self.show_about),("Purchase Tickets", self.purchase_tickets),("Order History", self.view_order_history),("Account Settings", self.create_customer_account_settings),("View Cart", self.view_cart),("Log Out", self.create_login_page),]
        button_frame = tk.Frame(self.root)  # Create a frame to group the buttons
        button_frame.pack(pady=20)
        for text, command in buttons: tk.Button(button_frame, text=text, command=command, font=("Arial", 14), width=20, height=1).pack(pady=10)  # Add padding between buttons
    def show_about(self):
        self.root.geometry("600x300")  # Adjust window size for readability
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Title
        tk.Label(self.root, text="About Adventure Land Theme Park", font=("Arial", 18, "bold"), anchor="center").pack(pady=20)
        # About Text
        about_text = ("Welcome to Adventure Land Theme Park! \nYour ultimate destination for fun, thrills, and unforgettable family moments.\n\nWith exciting rides, delicious food, and captivating shows, there’s something for everyone!\nJoin us for an adventure of a lifetime!")
        tk.Label(self.root, text=about_text, font=("Arial", 12), wraplength=500, anchor="center").pack(pady=20)
        # Back Button
        tk.Button(self.root, text="Back to Home", command=lambda: self.show_home_page("customer"), font=("Arial", 14), width=15, height=1).pack(pady=10)

    def purchase_tickets(self):
        self.root.geometry("1000x500")  # Adjust window size to fit ticket details

        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Update ticket_data from the DataLayer
        self.data["tickets"] = self.data_layer.load_tickets()

        # Debugging: Check if tickets are loaded
        print("Loaded Tickets:", self.data["tickets"])

        if not self.data["tickets"]:
            print("No tickets found. Initializing default tickets.")
            messagebox.showwarning("Warning", "No tickets found. Initializing default tickets.")
            self.data_layer.initialize_files()
            self.data["tickets"] = self.data_layer.load_tickets()
            print("Reloaded Tickets:", self.data["tickets"])

        # Validate loaded tickets
        if not self.data["tickets"]:
            messagebox.showerror("Error", "Tickets could not be loaded. Please check the data layer.")
            return

        # Prepare ticket details
        ticket_details = [
            {
                "ticket_type": ticket.get_ticket_type(),
                "description": ticket.get_description(),
                "price": ticket.get_price(),
                "validity": ticket.get_validity(),
                "limitations": ticket.get_limitations(),
                "discount": ticket.get_discount(),
            }
            for ticket in self.data["tickets"]
        ]

        # Title
        tk.Label(self.root, text="Purchase Tickets", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=7,
                                                                                      pady=20)

        # Column headers
        headers = ["Ticket Type", "Description", "Price (AED)", "Validity", "Discount", "Limitations", "Action"]
        for col_index, header in enumerate(headers):
            tk.Label(self.root, text=header, font=("Arial", 12, "bold"), anchor="center").grid(row=1, column=col_index,
                                                                                               padx=10, pady=5)

        # Display ticket details
        for row_index, ticket in enumerate(ticket_details, start=2):
            discounted_price = ticket["price"] * (1 - ticket["discount"] / 100)
            details = [
                ticket["ticket_type"],
                ticket["description"],
                f"{discounted_price:.2f}",
                ticket["validity"],
                f"{ticket['discount']}%",
                ticket["limitations"],
            ]
            for col_index, detail in enumerate(details):
                tk.Label(
                    self.root, text=detail, font=("Arial", 10), wraplength=150, justify="left"
                ).grid(row=row_index, column=col_index, padx=5, pady=5)

            # Add 'Add to Cart' button
            tk.Button(
                self.root,
                text="Add to Cart",
                font=("Arial", 10),
                command=lambda t=ticket: self.add_to_cart(t),
            ).grid(row=row_index, column=len(details), padx=10, pady=5)

        # Back Button
        tk.Button(
            self.root,
            text="Back to Home",
            command=lambda: self.show_home_page("customer"),
            font=("Arial", 14),
            width=15,
        ).grid(row=row_index + 2, column=3, pady=20)

    def create_customer_account_settings(self):
        self.root.geometry("300x280")  # Adjust window size to fit ticket details
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Customer Account Settings").grid(row=0, column=1, pady=10)
        # View Account Information Button
        tk.Button(self.root,text="View Account Information",command=self.view_account_information).grid(row=1, column=1, pady=5)
        # Adjust Account Information Button
        tk.Button(self.root,text="Adjust Account Information",command=self.adjust_account_information).grid(row=2, column=1, pady=5)
        # Delete Account Button
        tk.Button(self.root,text="Delete Account",command=self.delete_account).grid(row=3, column=1, pady=5)
        # Back to Home Button
        tk.Button(self.root,text="Back to Home",command=lambda: self.show_home_page("customer")).grid(row=4, column=1, pady=10)
    def delete_account(self):
        current_customer = self.logged_in_user
        if not current_customer:
            messagebox.showerror("Error", "No customer is logged in.")
            return
        # Confirmation dialog
        confirm = messagebox.askyesno("Delete Account","Are you sure you want to delete your account? This action cannot be undone.")
        if confirm:
            self.data["customers"].remove(current_customer)  # Remove the account from the list
            self.logged_in_user = None  # Log the user out
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
            self.create_login_page()  # Redirect to the login page
    def view_cart(self):
        self.root.geometry("450x500")  # Adjust window size for cart details
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Title
        tk.Label(self.root, text="Your Cart", font=("Arial", 18, "bold"), anchor="center").grid(row=0, column=0, columnspan=4, pady=20)
        # Get the logged-in customer and their cart
        current_customer = self.business_model.get_logged_in_customer(self.logged_in_user.get_username())
        if not current_customer:
            messagebox.showerror("Error", "No customer is logged in.")
            return
        cart = current_customer.get_cart()
        items = cart.get_cart_items()

        # Define total_row early
        total_row = 1  # Default row for empty cart

        # If the cart is empty
        if not items:
            tk.Label(self.root, text="Your cart is empty.", font=("Arial", 14), anchor="center").grid(row=1, column=0, columnspan=4, pady=20)
            total_row = 2  # Adjust for the "Back to Home" button when the cart is empty
        else:
            # Column Headers
            headers = ["Ticket Type", "Price (AED)", "Action"]
            for col, header in enumerate(headers):
                tk.Label(self.root, text=header, font=("Arial", 12, "bold"), anchor="center").grid(row=1, column=col, padx=10, pady=10)
            # cart items
            for row, ticket in enumerate(items, start=2):
                # Display ticket type and price
                tk.Label(self.root, text=ticket.get_ticket_type(), font=("Arial", 11)).grid(row=row, column=0, padx=5, pady=5)
                tk.Label(self.root, text=f"{ticket.get_price():.2f}", font=("Arial", 11)).grid(row=row, column=1, padx=5, pady=5)
                # Add 'Remove' button with correct ticket binding
                def make_remove_command(t):
                    return lambda: self.remove_ticket_from_cart(t)

                tk.Button(self.root, text="Remove", font=("Arial", 10), command=make_remove_command(ticket)).grid(row=row, column=2, padx=5, pady=5)
            # Total Price
            total_row = len(items) + 2  # Set total_row for buttons
            tk.Label(self.root, text=f"Total: {cart.calculate_cart_total():.2f} AED", font=("Arial", 14, "bold")).grid(row=total_row, column=0, columnspan=3, pady=20)
            # Checkout and Clear Cart Buttons
            tk.Button(self.root, text="Checkout", font=("Arial", 14), command=self.checkout_cart, width=15).grid(row=total_row + 1, column=1, pady=10)
            tk.Button(self.root, text="Clear Cart", font=("Arial", 14), command=lambda: self.clear_cart(cart), width=15).grid(row=total_row + 2, column=1, pady=10)
        # Back to Home Button
        tk.Button(self.root, text="Back to Home", font=("Arial", 14), command=lambda: self.show_home_page("customer"), width=15).grid(row=total_row + 3, column=1, pady=20)
    def add_to_cart(self, ticket_info):
        # Fetch the updated discount dynamically
        ticket_type = ticket_info["ticket_type"]
        updated_discount = next(
            (ticket.get_discount() for ticket in self.data["tickets"] if ticket.get_ticket_type() == ticket_type), 0)

        # Adjust the price based on the discount
        discounted_price = ticket_info["price"] * (1 - updated_discount / 100)
        new_ticket = Ticket(
            ticket_type=ticket_info["ticket_type"],
            description=ticket_info["description"],
            price=discounted_price,
            validity=ticket_info["validity"],
            limitations=ticket_info["limitations"],
            discount=updated_discount
        )

        current_customer = self.logged_in_user
        if not current_customer:
            messagebox.showerror("Error", "No customer is logged in.")
            return

        current_customer.get_cart().add_to_cart(new_ticket)
        messagebox.showinfo("Success", f"{ticket_info['ticket_type']} has been added to your cart!")
    def remove_ticket_from_cart(self, ticket):
        current_customer = self.logged_in_user
        cart = current_customer.get_cart()
        cart.remove_from_cart(ticket)
        self.view_cart()
    def clear_cart(self, cart):
        cart.clear_cart()
        self.view_cart()
    def view_order_history(self):
        self.root.geometry("1020x500")  # Adjust window size
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()
        # Title
        tk.Label(self.root, text="Order History", font=("Arial", 20, "bold"), anchor="center").grid(row=0, column=0, columnspan=4, pady=20)
        # Get the logged-in customer
        current_customer = self.logged_in_user
        if not current_customer:
            messagebox.showerror("Error", "No customer is logged in.")
            return
        # Retrieve the purchase history
        history = current_customer.get_purchase_history()
        if not history:
            # No orders found message
            tk.Label(self.root, text="You have no orders yet.", font=("Arial", 14, "italic"), fg="gray").grid(row=1, column=0, columnspan=4, pady=20)
            tk.Button(self.root, text="Back to Home", font=("Arial", 14), command=lambda: self.show_home_page("customer"), width=20).grid(row=2, column=1, pady=20)
            return
        # Column Headers
        headers = ["Order ID", "Date", "Total Price (AED)", "Tickets"]
        for col, header in enumerate(headers):
            tk.Label(self.root, text=header, font=("Arial", 14, "bold"), anchor="center", bg="#f0f0f0", relief="groove", width=20).grid(row=1, column=col, padx=5, pady=10)
        # Display orders
        row_index = 2
        for order in history:
            tk.Label(self.root, text=order.get_order_id(), font=("Arial", 12)).grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
            tk.Label(self.root, text=order.get_purchase_date(), font=("Arial", 12)).grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
            tk.Label(self.root, text=f"{order.get_total_price():.2f} AED", font=("Arial", 12)).grid(row=row_index, column=2, padx=10, pady=5, sticky="w")
            # Ticket details
            tickets_info = "\n".join(
                [f"{ticket.get_ticket_type()} - {ticket.get_price():.2f} AED" for ticket in order.get_tickets()])
            tk.Label(self.root, text=tickets_info, font=("Arial", 12), anchor="w", justify="left", wraplength=300).grid(row=row_index, column=3, padx=10, pady=5, sticky="w")
            row_index += 1
        # Back to Home Button
        tk.Button(self.root, text="Back to Home", font=("Arial", 16, "bold"), command=lambda: self.show_home_page("customer"), width=25).grid(row=row_index, column=0, columnspan=4, pady=30)
    def view_account_information(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Account Information").grid(row=0, column=1, pady=10)
        current_customer = self.business_model.get_logged_in_customer(self.logged_in_user.get_username())
        if current_customer:
            # Display username and email
            tk.Label(self.root, text=f"Username: {current_customer.get_username()}").grid(row=1,column=1,pady=5)
            tk.Label(self.root, text=f"Email: {current_customer.get_email()}").grid(row=2, column=1,pady=5)
            # Display purchase history
            purchase_history = current_customer.view_purchase_history()
            if not purchase_history:
                tk.Label(self.root, text="No purchase history found.").grid(row=3, column=1, pady=5)
            else:
                tk.Label(self.root, text="Purchase History:").grid(row=3, column=1, pady=10)
                for i, order in enumerate(purchase_history, start=1):
                    order_text = f"Order {i}: Date - {order['purchase_date']}, Total - ${order['total_price']}"
                    tk.Label(self.root, text=order_text).grid(row=3 + i, column=1, pady=5)
        # Back Button
        tk.Button(self.root,text="Back to Settings",command=self.create_customer_account_settings).grid(row=8 + len(purchase_history) + 1, column=1, pady=10)
    def adjust_account_information(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Adjust Account Information").grid(row=0, column=1, pady=10)
        tk.Label(self.root, text="New Username:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        new_username_entry = tk.Entry(self.root)
        new_username_entry.grid(row=1, column=1, pady=5)
        tk.Label(self.root, text="New Password:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        new_password_entry = tk.Entry(self.root, show="*")
        new_password_entry.grid(row=2, column=1, pady=5)
        tk.Label(self.root, text="New Email:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        new_email_entry = tk.Entry(self.root)
        new_email_entry.grid(row=3, column=1, pady=5)

        def update_account():
            current_customer = self.business_model.get_logged_in_customer(self.logged_in_user.get_username())
            if not current_customer:
                messagebox.showerror("Error", "No customer is logged in.")
                return
            new_username = new_username_entry.get()
            new_password = new_password_entry.get()
            new_email = new_email_entry.get()

            try:
                # Update customer account using the business model
                current_customer.modify_account(username=new_username if new_username else None,password=new_password if new_password else None,email=new_email if new_email else None,)
                messagebox.showinfo("Success", "Account information updated successfully!")
                self.create_customer_account_settings()  # Return to the account settings page
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        # Update Button
        tk.Button(self.root,text="Update",command=update_account).grid(row=4, column=1, pady=10)

        # Back Button
        tk.Button(self.root,text="Back to Settings",command=self.create_customer_account_settings).grid(row=5, column=1, pady=10)

    def create_admin_home(self):
        # Clear the window before displaying admin home
        for widget in self.root.winfo_children():
            widget.destroy()
        # Set up the admin home page
        self.root.geometry("250x350")  # Adjust the window size
        tk.Label(self.root, text="Admin Home Page", font=("Arial", 18, "bold")).grid(row=0, column=1, pady=20)
        tk.Button(self.root, text="Modify Tickets' Discount", command=self.modify_discounts, font=("Arial", 14)).grid(row=1, column=1, pady=10)
        tk.Button(self.root, text="Display Ticket Sales", command=self.display_ticket_sales, font=("Arial", 14)).grid(row=2, column=1, pady=10)
        tk.Button(self.root, text="Account Settings", command=self.create_admin_account_settings, font=("Arial", 14)).grid(row=3, column=1, pady=10)
        tk.Button(self.root, text="Log Out", command=self.create_login_page, font=("Arial", 14)).grid(row=4, column=1, pady=10)

    def display_ticket_sales(self):
        self.root.geometry("1200x500")  # Adjust window size
        # Clear the current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Daily Ticket Sales", font=("Arial", 16)).grid(row=0, column=1, pady=10)
        # Retrieve all orders from all customers
        all_orders = []
        for customer in self.data["customers"]:
            customer_orders = customer.get_purchase_history()
            all_orders.extend(customer_orders)
        if not all_orders:
            tk.Label(self.root, text="No ticket sales found.").grid(row=1, column=1, pady=10)
            last_row = 2  # Next row for the button
        else:
            # Calculate ticket sales details per day
            daily_sales = {}
            for order in all_orders:
                if order.get_status() == Status.Paid:  # Only count paid orders
                    purchase_date = order.get_purchase_date()
                    if purchase_date not in daily_sales:
                        daily_sales[purchase_date] = {"ticket_count": 0, "ticket_types": {}, "total_price": 0.0}

                    # Aggregate ticket count, types, and total price
                    daily_sales[purchase_date]["ticket_count"] += len(order.get_tickets())
                    daily_sales[purchase_date]["total_price"] += order.get_total_price()
                    for ticket in order.get_tickets():
                        ticket_type = ticket.get_ticket_type()
                        if ticket_type not in daily_sales[purchase_date]["ticket_types"]:
                            daily_sales[purchase_date]["ticket_types"][ticket_type] = 0
                        daily_sales[purchase_date]["ticket_types"][ticket_type] += 1

            # Display column headers
            tk.Label(self.root, text="Date", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5)
            tk.Label(self.root, text="Tickets Sold", font=("Arial", 12, "bold")).grid(row=1, column=1, padx=10, pady=5)
            tk.Label(self.root, text="Ticket Types", font=("Arial", 12, "bold")).grid(row=1, column=2, padx=10, pady=5)
            tk.Label(self.root, text="Total Price (AED)", font=("Arial", 12, "bold")).grid(row=1, column=3, padx=10,pady=5)

            # Display daily ticket sales data
            row_index = 2
            for date in daily_sales:
                data = daily_sales[date]
                ticket_types = ""
                for ticket_type, count in data["ticket_types"].items():
                    ticket_types += f"{ticket_type} ({count}), "
                ticket_types = ticket_types.rstrip(", ")  # Remove the trailing comma and space
                tk.Label(self.root, text=str(date)).grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
                tk.Label(self.root, text=str(data["ticket_count"])).grid(row=row_index, column=1, padx=10, pady=5,sticky="w")
                tk.Label(self.root, text=ticket_types).grid(row=row_index, column=2, padx=10, pady=5, sticky="w")
                tk.Label(self.root, text=f"{data['total_price']:.2f}").grid(row=row_index, column=3, padx=10, pady=5,sticky="w")
                row_index += 1  # Increment the row index for the next set of data
            last_row = row_index  # Track the last row used
        # Back to Home Button
        tk.Button(self.root, text="Back to Home", command=lambda: self.show_home_page("admin")).grid(row=last_row, column=1, pady=10)
    def modify_discounts(self):
        self.root.geometry("500x500")  # Adjust window size
        # Clear the current window
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Modify Tickets' Discounts", font=("Arial", 16)).grid(row=0, column=0, columnspan=4, pady=10)

        # Fetch ticket data
        discount_entries = {}
        row_index = 1  # Initialize row index

        for ticket in self.data["tickets"]:  # Iterate through tickets without enumerate
            tk.Label(self.root, text=f"{ticket.get_ticket_type()}").grid(row=row_index, column=0, sticky="w", pady=5, padx=10)
            tk.Label(self.root, text=f"Current Discount: {ticket.get_discount()}%").grid(row=row_index, column=1, sticky="w", pady=5)
            discount_entry = tk.Entry(self.root, width=10)
            discount_entry.insert(0, str(ticket.get_discount()))  # Fill with the current discount
            discount_entry.grid(row=row_index, column=2, pady=5, padx=10)
            discount_entries[ticket.get_ticket_type()] = discount_entry
            row_index += 1  # Increment row index for the next ticket

        def save_discounts():
            # Iterate over discount entries and update the tickets
            for ticket in self.data["tickets"]:
                if ticket.get_ticket_type() in discount_entries:
                    new_discount = discount_entries[ticket.get_ticket_type()].get()
                    if not new_discount.isdigit() or int(new_discount) < 0 or int(new_discount) > 100:
                        messagebox.showerror("Error", f"Invalid discount value for {ticket.get_ticket_type()}. Enter 0-100.")
                        return
                    ticket.set_discount(int(new_discount))  # Update discount for the ticket

            # Save updated tickets to the data layer
            self.data_layer.save_tickets(self.data["tickets"])
            messagebox.showinfo("Success", "Discounts updated successfully!")

        tk.Button(self.root, text="Save Discounts", command=save_discounts).grid(row=row_index + 1, column=1, pady=20)
        tk.Button(self.root, text="Back to Admin Home", command=lambda: self.show_home_page("admin")).grid(
            row=row_index + 2, column=1, pady=5)
    def create_admin_account_settings(self):
        self.root.geometry("230x250")  # Adjust window size
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Admin Account Settings").grid(row=0, column=1, pady=10)
        # View Account Information Button
        tk.Button(self.root,text="View Account Information",command=self.view_admin_account_information).grid(row=1, column=1, pady=5)
        # Adjust Account Information Button
        tk.Button(self.root,text="Adjust Account Information",command=self.adjust_admin_account_information).grid(row=2, column=1, pady=5)
        # Back to Home Button
        tk.Button(self.root,text="Back to Home",command=lambda: self.show_home_page("admin")).grid(row=3, column=1, pady=10)
    def view_admin_account_information(self):
        """Display admin account information."""
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Admin Account Information").grid(row=0, column=1, pady=10)

        current_admin = self.logged_in_admin  # Retrieve logged-in admin
        if current_admin:
            # Display admin details
            tk.Label(self.root, text=f"Admin ID: {current_admin.get_admin_id()}").grid(row=1, column=1, pady=5)
            tk.Label(self.root, text=f"Password: {current_admin.get_password()}").grid(row=2, column=1, pady=5)
            tk.Label(self.root, text=f"Email: {current_admin.get_email()}").grid(row=3, column=1, pady=5)
        else:
            tk.Label(self.root, text="No admin account is logged in.").grid(row=1, column=1, pady=10)

        # Back to Admin Home Button
        tk.Button(self.root, text="Back to Admin Home", command=lambda: self.show_home_page("admin")).grid(row=4, column=1, pady=10)
    def adjust_admin_account_information(self):
        self.root.geometry("400x300")  # Adjust window size
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Adjust Admin Account Information").grid(row=0, column=1, pady=10)
        tk.Label(self.root, text="New Username:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        new_username_entry = tk.Entry(self.root)
        new_username_entry.grid(row=1, column=1, pady=5)
        tk.Label(self.root, text="New Password:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        new_password_entry = tk.Entry(self.root, show="*")
        new_password_entry.grid(row=2, column=1, pady=5)
        tk.Label(self.root, text="New Email:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        new_email_entry = tk.Entry(self.root)
        new_email_entry.grid(row=3, column=1, pady=5)

        def update_admin_account():
            new_username = new_username_entry.get()
            new_password = new_password_entry.get()
            new_email = new_email_entry.get()
            logged_in_admin = self.logged_in_admin
            if not logged_in_admin:
                messagebox.showerror("Error", "No admin is currently logged in.")
                return
            if new_username:
                logged_in_admin.set_admin_id(new_username)
            if new_password:
                logged_in_admin.set_password(new_password)
            if new_email:
                logged_in_admin.set_email(new_email)
            messagebox.showinfo("Success", "Admin account information updated successfully!")
            self.view_admin_account_information()  # Redirect to view updated information
        # Update Button
        tk.Button(self.root, text="Update", command=update_admin_account).grid(row=4, column=1, pady=10)
        # Back Button
        tk.Button(self.root, text="Back to Settings", command=self.create_admin_account_settings).grid(row=5, column=1, pady=10)
# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = AdventureLandApp(root)
    root.mainloop()
