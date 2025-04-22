from db import db  # Importing the SQLAlchemy database instance
from datetime import datetime  # For handling date and time
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing

# User model representing a user in the system
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the Expense model (lazy loading for performance)
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} | Created: {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}>'

    def set_password(self, password):
        """Set password as a hashed value."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

from db import db  # Importing the SQLAlchemy database instance
from datetime import datetime  # For handling date and time

# Expense model representing a user's spending entry
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    def __repr__(self):
        return f"<Expense {self.name} | {self.category} | {self.amount} | {self.date.strftime('%Y-%m-%d %H:%M:%S')} | {self.description}>"

    @classmethod
    def create(cls, name, category, amount, date=None, description=None, user_id=None):
        """Helper method to create and add a new expense."""
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")
        if not name or not category:
            raise ValueError("Name and category cannot be empty.")
        if not user_id:
            raise ValueError("User ID is required.")

        if not date:
            date = datetime.utcnow()

        expense = cls(name=name, category=category, amount=amount, date=date, description=description, user_id=user_id)
        db.session.add(expense)
        db.session.commit()
        return expense

    @classmethod
    def get_expenses_by_user(cls, user_id, order_by_date=False):
        """Helper method to fetch expenses for a particular user."""
        query = cls.query.filter_by(user_id=user_id)
        if order_by_date:
            query = query.order_by(cls.date.desc())
        return query.all()

    @classmethod
    def get_total_expenses(cls, user_id):
        """Helper method to get the total amount of expenses for a user."""
        total = db.session.query(db.func.sum(cls.amount)).filter_by(user_id=user_id).scalar()
        return total if total else 0.0
