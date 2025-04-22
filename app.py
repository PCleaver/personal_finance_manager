from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from db import db
from models import User, Expense
from flask import send_from_directory
from sqlalchemy.exc import IntegrityError
from functools import wraps
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message, Mail
from werkzeug.exceptions import BadRequestKeyError
import re
from flask_migrate import Migrate
import matplotlib.pyplot as plt
import io
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')  # Ensure you set this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

mail = Mail(app)
migrate = Migrate(app, db)
db.init_app(app)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Password validation function
def is_password_strong(password):
    if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        flash('Password must be at least 8 characters long, contain a number, and include a special character.', 'danger')
        return False
    return True

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to view this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    # Query expenses for this user
    expenses = Expense.query.filter_by(user_id=user_id).all()

    # Compute total spending per category
    expenses_by_category = {}
    for expense in expenses:
        expenses_by_category[expense.category] = expenses_by_category.get(expense.category, 0) + expense.amount

    categories = list(expenses_by_category.keys())
    amounts = list(expenses_by_category.values())

    # Create a bar chart using matplotlib
    fig, ax = plt.subplots()
    ax.bar(categories, amounts, color='#ADD8E6')  # Light blue color for the bars
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Spending')
    ax.set_title('Spending Trend by Category')

    # Save the plot to a BytesIO object and encode it as base64 for embedding in HTML
    img_io = io.BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
    img_io.close()

    # Render the dashboard template with the chart image data
    return render_template('dashboard.html', img_data=img_data, expenses_by_category=expenses_by_category)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get the username and password from the form
            username = request.form['username']
            password = request.form['password']

            # Check if the username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already taken, please choose another.", 'danger')
                return redirect(url_for('register'))

            # Create a new user without the email field
            user = User(username=username)
            user.set_password(password)

            # Add the user to the session and commit to save
            db.session.add(user)
            db.session.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))  # Assuming there is a login view

        except BadRequestKeyError as e:
            flash(f"Missing field: {str(e)}", 'danger')
            return redirect(url_for('register'))

    return render_template('register.html') 


@app.route('/upload_transactions', methods=['GET', 'POST'])
@login_required
def upload_transactions():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = 'uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)

                # Print the columns to debug
                print("Columns in the uploaded file:", df.columns)

                required_columns = ['name', 'category', 'amount']
                if not all(col in df.columns for col in required_columns):
                    flash('Invalid file format. File must contain name, category, and amount.', 'danger')
                    return redirect(request.url)

                user_id = session['user_id']
                for _, row in df.iterrows():
                    expense = Expense(name=row['name'], category=row['category'], amount=row['amount'], user_id=user_id)
                    db.session.add(expense)
                db.session.commit()

                flash('Transactions uploaded successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f"Error reading file: {e}", 'danger')
                return redirect(request.url)

    return render_template('upload.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)  # Get page number from query string
    expenses = Expense.query.filter_by(user_id=user_id).paginate(page=page, per_page=10, error_out=False)

    # Calculate category totals for the chart
    category_totals = {}
    for expense in expenses.items:
        category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount

    # Prepare categories and amounts for the pie chart
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    # Handle the bulk actions (edit/delete)
    if request.method == 'POST':
        action = request.form.get('action')
        selected_expenses = request.form.getlist('selected_expenses')

        if action == 'delete' and selected_expenses:
            # Delete selected expenses
            Expense.query.filter(Expense.id.in_(selected_expenses)).delete(synchronize_session=False)
            db.session.commit()
            flash('Selected expenses deleted successfully!', 'success')
        
        elif action == 'edit' and selected_expenses:
            # Redirect to edit page for the first selected expense
            return redirect(url_for('edit_expense', expense_id=selected_expenses[0]))

    return render_template('index.html', expenses=expenses, categories=categories, amounts=amounts)

# NEW ROUTE FOR BULK EDIT OR DELETE
@app.route('/bulk_edit_or_delete', methods=['POST'])
@login_required
def bulk_edit_or_delete():
    action = request.form.get('action')
    selected_expenses = request.form.getlist('selected_expenses')

    if action == 'delete' and selected_expenses:
        # Delete selected expenses
        Expense.query.filter(Expense.id.in_(selected_expenses)).delete(synchronize_session=False)
        db.session.commit()
        flash('Selected expenses deleted successfully!', 'success')
    
    elif action == 'edit' and selected_expenses:
        # Redirect to edit page for the first selected expense (or handle bulk edit logic as needed)
        return redirect(url_for('edit_expense', expense_id=selected_expenses[0]))

    return redirect(url_for('index'))  # Redirect back to the index page after the bulk action

@app.route('/spending_trend')
@login_required
def spending_trend():
    # Query all expenses for the logged-in user
    user_id = session['user_id']
    expenses = Expense.query.filter_by(user_id=user_id).all()

    if not expenses:
        flash('No expenses found for this user.', 'info')
        return redirect(url_for('index'))  # Redirect to index or another page if no data exists

    # Group expenses by category
    expenses_by_category = {}
    for expense in expenses:
        if expense.category in expenses_by_category:
            expenses_by_category[expense.category] += expense.amount
        else:
            expenses_by_category[expense.category] = expense.amount

    categories = list(expenses_by_category.keys())
    spending = list(expenses_by_category.values())

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))  # Increase figure size for better visibility
    ax.bar(categories, spending, color='#ADD8E6')  # Optional: Add a color for the bars

    # Manually rotate the x-axis labels by adjusting the rotation of the xticks
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels directly

    # Convert the chart to a base64-encoded PNG image
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Pass the base64 image string and expense data to the template
    return render_template('spending_trend.html', img_b64=img_b64, expenses_by_category=expenses_by_category)

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if request.method == 'POST':
        expense.name = request.form['name']
        expense.category = request.form['category']
        expense.amount = request.form['amount']
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_expense.html', expense=expense)

# New route to remove an expense
@app.route('/remove_expense/<int:expense_id>', methods=['POST'])
@login_required
def remove_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    # Delete the expense
    db.session.delete(expense)
    db.session.commit()

    flash('Expense removed successfully!', 'success')
    return redirect(url_for('index'))

# New route to add an expense
@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        amount = float(request.form['amount'])

        # Add the new expense to the database
        expense = Expense(name=name, category=category, amount=amount, user_id=session['user_id'])
        db.session.add(expense)
        db.session.commit()

        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))  # Redirect to the index page after adding the expense

    return render_template('add_expense.html')  # Render the form if GET request

# New route for logging out
@app.route('/logout')
@login_required
def logout():
    """Logs out the user and redirects to login page."""
    session.pop('user_id', None)  # Removes the user from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

# New route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=False)