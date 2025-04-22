# 💸 Personal Finance Manager

A simple yet powerful web application for tracking your personal expenses. Upload your transaction history, view your spending trends, and manage your budget—all in one place.

---

## 🚀 Features

- 🔐 **User Authentication** — Register and log in securely with password hashing.
- 📥 **CSV/XLSX Upload** — Import transactions in bulk using common file formats.
- 📊 **Visual Spending Dashboard** — See your spending habits by category in dynamic bar and pie charts.
- ✏️ **Expense Management** — Add, edit, or delete expenses individually or in bulk.
- 📈 **Spending Trends** — Visualize your overall spending trends by category.
- 🧹 **Secure Sessions** — Routes are protected, and only logged-in users can access personal data.
- 📤 **File Handling** — Files are securely uploaded and managed on the backend.

---

## 🛠️ Technologies Used

- **Flask** — Lightweight Python web framework
- **SQLAlchemy** — ORM for database interactions
- **Flask-Migrate** — For database migrations
- **Werkzeug** — For password hashing and secure file uploads
- **Matplotlib** — To visualize spending data
- **Flask-Mail** — Email capability (if configured)
- **Bootstrap (via HTML templates)** — For responsive front-end styling

---

## 🔐 Authentication

To use the application, you must first **register** an account and log in.

> Passwords must:
> - Be at least 8 characters long  
> - Contain at least one number  
> - Include a special character

Sessions are maintained securely so your data is private and personalized.

---

## 📁 Uploading Transactions

Supported file formats:
- `.csv`
- `.xls`
- `.xlsx`

Make sure your file contains the following columns:
- `name` — Description of the transaction  
- `category` — Category name (e.g., Food, Transport, etc.)  
- `amount` — Numeric value of the transaction

---

## 📸 Screenshots

Spending visualizations are automatically generated based on your data.

- 📊 Pie charts for current overview  
- 📈 Bar charts for trend analysis

---

## 🔧 Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/personal_finance_manager.git
   cd personal_finance_manager
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export FLASK_SECRET_KEY=your_secret_key
   export MAIL_USERNAME=your_email@gmail.com
   export MAIL_PASSWORD=your_email_password
   ```

4. Run the app:
   ```bash
   flask run
   ```

---

## ✉️ Email Configuration (Optional)

To enable email-based features (like password reset), configure `MAIL_USERNAME` and `MAIL_PASSWORD` in your environment or `.env` file.

---

## 📌 Notes

- Make sure `uploads/` directory exists and is writable.
- Use a virtual environment for dependency isolation.
- For production deployment, use a WSGI server like Gunicorn.

---

## 🧾 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Built with ❤️ by **Philip Cleaver**
