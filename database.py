# database.py
from app import db  # Importing the SQLAlchemy instance from your main app file (app.py)
from models import User, Expense  # Importing the models (User, Expense)

def create_table():
    """Function to create the tables in the database."""
    with db.app_context():  # Ensuring the app context is active
        db.create_all()  # This creates all the tables based on the models defined in app.py

    print("Tables created successfully!")
