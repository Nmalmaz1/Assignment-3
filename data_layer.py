import pickle
import os
from business_model import *


ticket_data = [
    {"ticket_type": "Single-Day Pass", "description": "Access to the park for one day", "price": 275.0, "validity": "1 Day", "discount": 0, "limitations": "Valid only on selected date"},
    {"ticket_type": "Two-Day Pass", "description": "Access to the park for two consecutive days", "price": 480.0, "validity": "2 Days", "discount": 10, "limitations": "Cannot be split over multiple trips"},
    {"ticket_type": "Annual Membership", "description": "Unlimited access for one year", "price": 1840.0, "validity": "1 Year", "discount": 15, "limitations": "Must be used by the same person"},
    {"ticket_type": "Child Ticket", "description": "Discounted ticket for children (ages 3-12)", "price": 185.0, "validity": "1 Day", "discount": 0, "limitations": "Valid only on selected date, must be accompanied by an adult"},
    {"ticket_type": "Group Ticket (10+)", "description": "Special rate for groups of 10 or more", "price": 220.0, "validity": "1 Day", "discount": 20, "limitations": "Must be booked in advance"},
    {"ticket_type": "VIP Experience Pass", "description": "Includes expedited access and reserved seating for shows", "price": 550.0, "validity": "1 Day", "discount": 0, "limitations": "Limited availability, must be purchased in advance"},]

# Base path for all data files
BASE_PATH = os.environ.get("DATA_LAYER_PATH", os.getcwd())
def get_filepath(filename):
    return os.path.join(BASE_PATH, filename)


def save_to_file(data, filepath):
    try:
        with open(filepath, 'wb') as file:
            pickle.dump(data, file)
    except Exception as e:
        print(f"Failed to save data to {filepath}: {e}")
        raise


def load_from_file(filepath):
    try:
        with open(filepath, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        print(f"File not found: {filepath}. Returning empty list.")
        save_to_file([], filepath)
        return []

    except (pickle.UnpicklingError, EOFError):
        print(f"Corrupted or empty file: {filepath}. Returning empty list.")
        save_to_file([], filepath)  # Overwrite with an empty list
        return []



class DataLayer:
    def __init__(self):
        self.filepaths = {
            "customers": r"C:\Users\shi5_\OneDrive\Desktop\file\customers.pkl",
            "admins": r"C:\Users\shi5_\OneDrive\Desktop\file\admins.pkl",
            "tickets": r"C:\Users\shi5_\OneDrive\Desktop\file\tickets.pkl",
            "orders": r"C:\Users\shi5_\OneDrive\Desktop\file\orders.pkl",
        }

    # Generalized Methods
    def save_entities(self, entities, filepath, to_serializable):
        try:
            serializable_data = [to_serializable(entity) for entity in entities]
            save_to_file(serializable_data, filepath)
        except Exception as e:
            print(f"Failed to save entities to {filepath}: {e}")
            raise

    def load_entities(self, filepath, from_raw):
        try:
            raw_data = load_from_file(filepath)
            return [from_raw(data) for data in raw_data]
        except Exception as e:
            print(f"Failed to load entities from {filepath}: {e}")
            raise

    # Entity-Specific Save Methods
    def save_customers(self, customers):
        self.save_entities(customers, self.filepaths["customers"], lambda customer: {"username": customer.get_username(), "password": customer.get_password(), "email": customer.get_email(), "purchase_date": customer.get_order().get_purchase_date(), "tickets": [{"ticket_type": ticket.get_ticket_type(), "description": ticket.get_description(), "price": ticket.get_price(), "validity": ticket.get_validity(), "limitations": ticket.get_limitations(),} for ticket in customer.get_order().get_tickets()], "cart": [{"ticket_type": ticket.get_ticket_type(), "description": ticket.get_description(), "price": ticket.get_price(), "validity": ticket.get_validity(), "limitations": ticket.get_limitations(), "discount": ticket.get_discount(),} for ticket in customer.get_cart().get_cart_items()], "purchase_history": [{"purchase_date": order.get_purchase_date(), "status": order.get_status().name, "total_price": order.get_total_price(), "tickets": [{"ticket_type": ticket.get_ticket_type(), "description": ticket.get_description(), "price": ticket.get_price(), "validity": ticket.get_validity(), "limitations": ticket.get_limitations(),} for ticket in order.get_tickets()],} for order in customer.get_purchase_history()],})

    def save_admins(self, admins):
        self.save_entities(admins, self.filepaths["admins"], lambda admin: {"admin_id": admin.get_admin_id(), "password": admin.get_password(), "email": admin.get_email(), "orders": [{   "purchase_date": order.get_purchase_date(), "status": order.get_status().name, "total_price": order.get_total_price(), "tickets": [{   "ticket_type": ticket.get_ticket_type(), "description": ticket.get_description(), "price": ticket.get_price(), "validity": ticket.get_validity(), "limitations": ticket.get_limitations(),} for ticket in order.get_tickets()],} for order in admin.get_orders()],})

    def save_orders(self, orders):
        self.save_entities(orders, self.filepaths["orders"], lambda order: {
            "purchase_date": order.get_purchase_date(),
            "status": order.get_status().name,
            "total_price": order.get_total_price(),
            "tickets": [
                {   "ticket_type": ticket.get_ticket_type(),
                    "description": ticket.get_description(),
                    "price": ticket.get_price(),
                    "validity": ticket.get_validity(),
                    "limitations": ticket.get_limitations(),}
                for ticket in order.get_tickets()],})

    def save_tickets(self, tickets):
        """
        Persist the list of tickets to a .pkl file.
        """
        self.save_entities(tickets, self.filepaths["tickets"], lambda ticket: {
            "ticket_type": ticket.get_ticket_type(),
            "description": ticket.get_description(),
            "price": ticket.get_price(),
            "validity": ticket.get_validity(),
            "limitations": ticket.get_limitations(),
            "discount": ticket.get_discount()  # Include discount attribute
        })

    # Entity-Specific Load Methods
    def load_customers(self):
        try:
            return self.load_entities(self.filepaths["customers"], lambda data: CustomerAccount(
                username=data["username"],
                password=data["password"],
                email=data["email"],
                purchase_date=data["purchase_date"],
                tickets=[
                    Ticket(
                        ticket_type=ticket_data["ticket_type"],
                        description=ticket_data["description"],
                        price=ticket_data["price"],
                        validity=ticket_data["validity"],
                        limitations=ticket_data["limitations"],
                    )
                    for ticket_data in data["tickets"]
                ],
                purchase_history=[
                    Order(
                        purchase_date=history["purchase_date"],
                        status=Status[history["status"]],
                        tickets=[
                            Ticket(
                                ticket_type=ticket["ticket_type"],
                                description=ticket["description"],
                                price=ticket["price"],
                                validity=ticket["validity"],
                                limitations=ticket["limitations"],
                            )
                            for ticket in history["tickets"]
                        ],
                        total_price=history["total_price"],
                    )
                    for history in data["purchase_history"]
                ],
                cart=Cart(items=[
                    Ticket(
                        ticket_type=item["ticket_type"],
                        description=item["description"],
                        price=item["price"],
                        validity=item["validity"],
                        limitations=item["limitations"],
                        discount=item["discount"],
                    )
                    for item in data.get("cart", [])
                ])
            ))
        except ValueError as e:
            print(f"Error loading customers: {e}. Returning empty list.")
            return []

    def load_admins(self):
        return self.load_entities(self.filepaths["admins"], lambda data: Admin(
            admin_id=data["admin_id"],
            password=data["password"],
            email=data["email"],
            orders=[
                Order(
                    purchase_date=order_data["purchase_date"],
                    status=Status[order_data["status"]],
                    tickets=[
                        Ticket(
                            ticket_type=ticket["ticket_type"],
                            description=ticket["description"],
                            price=ticket["price"],
                            validity=ticket["validity"],
                            limitations=ticket["limitations"],)
                        for ticket in order_data["tickets"]],
                    total_price=order_data["total_price"],)
                for order_data in data["orders"]],))

    def load_orders(self):
        return self.load_entities(self.filepaths["orders"], lambda data: Order(
            purchase_date=data["purchase_date"],
            status=Status[data["status"]],
            tickets=[
                Ticket(
                    ticket_type=ticket["ticket_type"],
                    description=ticket["description"],
                    price=ticket["price"],
                    validity=ticket["validity"],
                    limitations=ticket["limitations"],)
                for ticket in data["tickets"]],
            total_price=data["total_price"],))

    def load_tickets(self):
        """
        Load the list of tickets from the .pkl file.
        """
        return self.load_entities(self.filepaths["tickets"], lambda data: Ticket(
            ticket_type=data["ticket_type"],
            description=data["description"],
            price=data["price"],
            validity=data["validity"],
            limitations=data["limitations"],
            discount=data.get("discount", 0)  # Default discount to 0 if not present
        ))

    # Comprehensive Save-All and Load-All
    def save_all(self, data):
        self.save_customers(data.get("customers", []))
        self.save_admins(data.get("admins", []))
        self.save_tickets(data.get("tickets", []))
        self.save_orders(data.get("orders", []))

    def initialize_files(self):
        """Create .pkl files with default data if they do not exist."""
        default_tickets = [
            {
                "ticket_type": "Single-Day Pass",
                "description": "Access to the park for one day",
                "price": 275.0,
                "validity": "1 Day",
                "limitations": "Valid only on selected date",
                "discount": 0
            },
            {
                "ticket_type": "Two-Day Pass",
                "description": "Access to the park for two consecutive days",
                "price": 480.0,
                "validity": "2 Days",
                "limitations": "Cannot be split over multiple trips",
                "discount": 10
            }
        ]

        if not os.path.exists(self.filepaths["tickets"]):
            print("Initializing tickets file with default data.")
            self.save_tickets([
                Ticket(
                    ticket_type=ticket["ticket_type"],
                    description=ticket["description"],
                    price=ticket["price"],
                    validity=ticket["validity"],
                    limitations=ticket["limitations"],
                    discount=ticket["discount"]
                )
                for ticket in default_tickets
            ])

    def load_all(self):return {"customers": self.load_customers(), "admins": self.load_admins(), "tickets": self.load_tickets(), "orders": self.load_orders(),}
