from datetime import date
from enum import Enum

class Status(Enum):
    Pending= 1
    Paid= 2
    Cancelled= 3

class Order:
    #to track the next available order ID
    order_id = 1
    def __init__(self, purchase_date: date,status , tickets: list['Ticket'], payment: 'Payment' = None, total_price=0):
        # Automatically assign the next available order ID
        self.__order_id = Order.order_id
        self.__status = status
        Order.order_id += 1  # Increment the class-level order ID for the next instance
        self.__purchase_date = purchase_date
        self.__tickets = tickets #Aggregation: Order can link to Ticket objects, but they exist independently.
        self.__payment = payment
        self.__total_price = total_price
    # Getters
    def get_status(self):
        return self.__status
    def get_order_id(self):
        return self.__order_id
    def get_purchase_date(self):
        return self.__purchase_date
    def get_tickets(self):
        return self.__tickets
    def get_payment(self):
        return self.__payment
    def get_total_price(self):
        return self.__total_price
    # Setters
    def set_purchase_date(self, purchase_date: date):
        self.__purchase_date = purchase_date
    def set_tickets(self, tickets: list['Ticket']):
        self.__tickets = tickets
    def set_payment(self, payment: 'Payment'):
        self.__payment = payment
    def set_total_price(self, total_price: float):
        self.__total_price = total_price
    # Other methods
    def calculate_total_price(self):
        total_price = sum(ticket.get_price() for ticket in self.get_tickets())  # Sum updated ticket prices
        self.set_total_price(total_price)
    def update_tickets(self, new_tickets: list['Ticket']):
        self.set_tickets(new_tickets)  # Aggregation: Updates aggregated Ticket objects.
        self.calculate_total_price()
    def has_payment(self):
        return self.get_payment() is not None  # Aggregation: Checks for the aggregated Payment object.
    def apply_discounts(self, group_size: int = 0, is_online: bool = False, is_renewal: bool = False):
        for ticket in self.__tickets:
            ticket_type = ticket.get_ticket_type()

            # Apply specific discounts
            if ticket_type == "Two-Day Pass" and is_online:
                ticket.set_price(ticket.get_price() * 0.9)  # 10% online discount
            elif ticket_type == "Annual Membership" and is_renewal:
                ticket.set_price(ticket.get_price() * 0.85)  # 15% renewal discount
            elif ticket_type == "Group Ticket" and group_size >= 10:
                ticket.set_price(ticket.get_price() * 0.8)  # 20% group discount
        # Recalculate the total price after applying discounts
        self.calculate_total_price()
        def set_status(self, status: Status):
            if not isinstance(status, Status):
                raise ValueError(f"Invalid status. Status must be one of: {list(Status)}")
            self.__status = status
class CustomerAccount:
    def __init__(self, username, password, email, purchase_date: date, tickets: list, purchase_history=None, cart=None):
        self.__username = username
        self.__password = password
        self.__email = email
        self.__order = Order(purchase_date, Status.Pending, tickets)
        self.__purchase_history = purchase_history or []
        self.__cart = cart or Cart()  # Initialize the cart
        # Getters
    def get_username(self):
        return self.__username
    def get_password(self):
        return self.__password
    def get_email(self):
        return self.__email
    def get_order(self):
        return self.__order
    def get_purchase_history(self):
        return self.__purchase_history
    def get_cart(self):
        return self.__cart
    # Setters
    def set_username(self, username):
        self.__username = username
    def set_password(self, password):
        self.__password = password
    def set_email(self, email):
        self.__email = email
    def set_order(self, purchase_date: date, tickets: list):
        self.__order = Order(purchase_date, tickets)
    def set_purchase_history(self, purchase_history):
        self.__purchase_history = purchase_history
    # Methods
    def get_logged_in_customer(self, logged_in_username):
        if self.username == logged_in_username:
            return self
        return None
    def validate_account_creation(self):
        if not self.__email or "@" not in self.__email:
            raise ValueError("Invalid email. Please provide a valid email address.")
        if not self.__password or len(self.__password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not self.__username or len(self.__username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return True
    # Validate the customer's email
    def validate_email(self, input_email):
        return self.get_email() == input_email  # Check if input matches the stored email
    # Validate the customer's password
    def validate_password(self, input_password):
        return self.get_password() == input_password  # Check if input matches the stored password
    def add_order_to_history(self, order: Order):
        if not isinstance(order, Order):
            raise ValueError("Invalid order. Must be an instance of the Order class.")
        # Recalculate total price and apply discounts before saving
        order.calculate_total_price()
        self.__purchase_history.append(order)
    def view_purchase_history(self):
        history = self.get_purchase_history()  # Access purchase history through getter
        formatted_history = []
        for order in history:
            order_details = {"purchase_date": order.get_purchase_date(),"status": order.get_status().name,"total_price": order.get_total_price(),"tickets": []}
            # Include details for each ticket in the order
            for ticket in order.get_tickets():
                ticket_details = ticket.display_ticket_details()
                ticket_data = {"ticket_type": ticket_details["ticket_type"],"original_price": ticket_details["price"],"discounted_price": ticket.get_price(),"validity": ticket_details["validity"]}
                order_details["tickets"].append(ticket_data)
            formatted_history.append(order_details)
        return formatted_history
    def get_order_details(self):
        order = self.get_order()  # Composition: Accesses the composed Order object.
        return {"purchase_date": order.get_purchase_date(),"total_price": order.get_total_price(),"tickets": order.get_tickets()}
    def add_payment_to_order(self, payment):
        order = self.get_order()  # Composition: Accesses the composed Order object.
        order.set_payment(payment)  # Aggregation: Links a Payment object to the Order.
    def update_email(self, new_email):
        self.set_email(new_email)
    def create_account(self, username, password, email):
        self.set_username(username)
        self.set_password(password)
        self.set_email(email)
        self.set_order(None)  # No order initially, can be added later
    def delete_account(self):
        self.set_username(None)
        self.set_password(None)
        self.set_email(None)
        self.set_order(None)
    def modify_account(self, username=None, password=None, email=None):
        if username:
            self.set_username(username)
        if password:
            self.set_password(password)
        if email:
            self.set_email(email)
    def delete_order(self, order_id: int):
        history = self.get_purchase_history()
        updated_history = [order for order in history if order.get_order_id() != order_id]
        if len(history) == len(updated_history):
            print(f"No order found with ID: {order_id}")
        else:
            self.set_purchase_history(updated_history)
            print(f"Order with ID {order_id} has been successfully deleted.")
    def get_cart(self):
        return self.__cart

class Payment:
    def __init__(self, payment_method: str, amount: float):
        self.__payment_method = payment_method
        self.__amount = amount  # Aggregation: Payment is linked to an Order.
    # Getters
    def get_payment_method(self):
        return self.__payment_method
    def get_amount(self):
        return self.__amount
    # Setters
    def set_payment_method(self, payment_method: str):
        self.__payment_method = payment_method
    def set_amount(self, amount: float):
        self.__amount = amount

class Ticket:
    def __init__(self, ticket_type, description, price, validity, limitations, discount=0):
        self.__ticket_type = ticket_type  # Private attribute
        self.__description = description  # Private attribute
        self.__price = price  # Private attribute
        self.__validity = validity  # Private attribute
        self.__limitations = limitations  # Private attribute
        self.__discount = discount  # Private attribute

    # Getters
    def get_ticket_type(self):
        return self.__ticket_type
    def get_description(self):
        return self.__description
    def get_price(self):
        return self.__price
    def get_validity(self):
        return self.__validity
    def get_limitations(self):
        return self.__limitations

    def get_discount(self):
        return self.__discount
    # Setters
    def set_ticket_type(self, ticket_type):
        if isinstance(ticket_type, str) and ticket_type.strip():
            self.__ticket_type = ticket_type
        else:
            raise ValueError("Ticket type must be a non-empty string.")

    def set_description(self, description):
        if isinstance(description, str) and description.strip():
            self.__description = description
        else:
            raise ValueError("Description must be a non-empty string.")

    def set_price(self, price):
        if isinstance(price, (int, float)) and price > 0:
            self.__price = price
        else:
            raise ValueError("Price must be a positive number.")

    def set_validity(self, validity):
        if isinstance(validity, str) and validity.strip():
            self.__validity = validity
        else:
            raise ValueError("Validity must be a non-empty string.")

    def set_limitations(self, limitations):
        if isinstance(limitations, str):
            self.__limitations = limitations
        else:
            raise ValueError("Limitations must be a string.")

    def set_discount(self, discount):
        if isinstance(discount, int) and 0 <= discount <= 100:
            self.__discount = discount
        else:
            raise ValueError("Discount must be an integer between 0 and 100.")
    # Other methods
    def display_ticket_details(self):
        return {"ticket_type": self.get_ticket_type(),"description": self.get_description(),"price": self.get_price(),"validity": self.get_validity(),"limitations": self.get_limitations()}
    def get_discount(self):
        return self.__discount
# Assuming you have a dictionary or a list that stores ticket details globally


class TicketType(Ticket):  # Inherits from Ticket
    def __init__(self, ticket_type: str, description: str, price: float, validity: str, limitations: str, discount: float):
        super().__init__(ticket_type, description, price, validity, limitations)  # Inheritance: TicketType inherits Ticket attributes.
        self.__discount = discount
    # Getters
    def get_discount(self):
        return self.__discount
    # Setters
    def set_discount(self, discount: float):
        self.__discount = discount
    # Additional methods
    def calculate_discounted_price(self):
        return self.get_price() * (1 - self.get_discount())
    def display_ticket_details_with_discount(self):
        details = super().display_ticket_details()  # Inheritance: Reuses Ticket's method.
        details["discounted_price"] = self.calculate_discounted_price()
        return details

class Cart:
    def __init__(self, items=None):
        if items is None:
            items = []
        self.__items = items  # Initialize the cart with the given items

    def add_to_cart(self, item):
        self.__items.append(item)

    def remove_from_cart(self, item):
        if item in self.__items:
            self.__items.remove(item)

    def clear_cart(self):
        self.__items = []

    def get_cart_items(self):
        return self.__items

    def calculate_cart_total(self):
        return sum(item.get_price() for item in self.__items)

class Admin:
    def __init__(self, admin_id: str, password: str, orders: list['Order'], email: str = "", all_admins: list = None):
        self.__admin_id = admin_id
        self.__password = password
        self.__orders = orders
        self.__all_admins = all_admins or []
        self.__email = email  # Ensure this is set

    # Ensure all methods inside the class are properly indented
    def get_admin_id(self):
        return self.__admin_id
    def get_password(self):
        return self.__password
    def get_email(self):
        return self.__email
    def get_orders(self):
        return self.__orders
    def get_all_admins(self):
        return self.__all_admins
    # Setters
    def set_admin_id(self, admin_id: str):
        self.__admin_id = admin_id
    def set_password(self, password: str):
        self.__password = password
    def set_email(self, email: str):
        self.__email = email
    def set_orders(self, orders: list['Order']):
        self.__orders = orders
    def set_all_admins(self, all_admins: list):
        self.__all_admins = all_admins
    def validate_admin_creation(self):
        if not self.__admin_id or len(self.__admin_id) < 3:
            raise ValueError("Admin ID must be at least 3 characters long.")
        if not self.__password or len(self.__password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return True
    # Validate the admin's email
    def validate_email(self, input_email):
        return self.get_admin_id() == input_email  # Check if input matches the stored admin email (admin_id)
    # Validate the admin's password
    def validate_password(self, input_password):
        return self.get_password() == input_password  # Check if input matches the stored password

    def create_admin_account(self, admin_id: str, password: str, email: str = ""):
        for admin in self.get_all_admins():
            if admin["admin_id"] == admin_id:
                raise ValueError("Admin ID already exists.")
        new_admin = {"admin_id": admin_id, "password": password, "email": email}
        updated_admins = self.get_all_admins()
        updated_admins.append(new_admin)
        self.set_all_admins(updated_admins)
        # Ensure the current admin object is updated
        if self.get_admin_id() == admin_id:
            self.set_email(email)

        # Method to delete an admin account
    def delete_admin_account(self, admin_id: str):
        admins = self.get_all_admins()
        for admin in admins:
            if admin["admin_id"] == admin_id:
                admins.remove(admin)
                self.set_all_admins(admins)
                return
        raise ValueError("Admin ID not found.")
        # Method to modify an admin password
    def modify_admin_password(self, admin_id: str, new_password: str):
        admins = self.get_all_admins()
        for admin in admins:
            if admin["admin_id"] == admin_id:
                admin["password"] = new_password
                self.set_all_admins(admins)
                return
        raise ValueError("Admin ID not found.")
        # Method to validate admin login
    def validate_admin_login(self, admin_id, password):
        return self.get_admin_id() == admin_id and self.get_password() == password
    def modify_ticket_price(self, ticket, new_price):
        """Modify the price of a ticket."""
        if new_price <= 0:
            raise ValueError("Price must be greater than 0.")
        ticket.set_price(new_price)
    def delete_order(self, order):
        """Remove an order from the list of orders."""
        if order in self.__orders:
            self.__orders.remove(order)
        else:
            raise ValueError("Order not found.")
    def modify_ticket_discount(self, ticket: TicketType, new_discount: float):
        if not 0 <= new_discount <= 1:
            raise ValueError("Discount must be a value between 0 and 1.")
        ticket.set_discount(new_discount)
        def delete_order(self, order_id):
            """Delete an order by ID."""
            for order in self.__orders:
                if order.get_order_id() == order_id:
                    self.__orders.remove(order)
                    print(f"Order {order_id} has been deleted.")
                    return
            raise ValueError(f"Order with ID {order_id} not found.")
        # Add the new ticket to the system as part of an Order
        self.__orders.append(Order(purchase_date=date.today(), tickets=[new_ticket]))
        print(f"New ticket '{new_ticket.get_ticket_type()}' created and added to the system.")