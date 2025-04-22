import sqlite3

def get_db_connection():
    """Function to establish a database connection."""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def create_table():
    """Function to create the 'expenses' table if it doesn't already exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Table 'expenses' created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def insert_expense(name, amount, category, date):
    """Function to insert an expense into the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (name, amount, category, date)
            VALUES (?, ?, ?, ?)
        ''', (name, amount, category, date))
        conn.commit()
        print(f"Expense '{name}' added successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting expense: {e}")
    finally:
        conn.close()

def get_all_expenses():
    """Function to retrieve all expenses from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses')
        expenses = cursor.fetchall()
        return expenses
    except sqlite3.Error as e:
        print(f"Error fetching expenses: {e}")
    finally:
        conn.close()
