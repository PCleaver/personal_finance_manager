import sqlite3

# Connect to the database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()

# Query the user table
cursor.execute('SELECT * FROM user')  # 'user' table is lowercase by default
users = cursor.fetchall()

print("Users in database:")
for user in users:
    print(user)

# Query the expense table
cursor.execute('SELECT * FROM expense')  # 'expense' table is lowercase by default
expenses = cursor.fetchall()

print("\nExpenses in database:")
for expense in expenses:
    print(expense)

# Close the connection
conn.close()
