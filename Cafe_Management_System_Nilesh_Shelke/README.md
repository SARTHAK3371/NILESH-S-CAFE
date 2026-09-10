# Cafe Management System

**Developed by: Nilesh Shelke**

A complete, ready-to-run web-based Cafe Management System built with Python Flask and SQLite.

---

## Features

- **User Authentication** – Admin & Staff login
- **Dashboard** – Live stats (orders, revenue, pending)
- **Menu Management** – Add / Edit / Delete categories & items
- **Order Taking** – Select items with quantity, create orders by table
- **Order Tracking** – Status: Pending → Preparing → Served → Paid / Cancelled
- **Billing** – Print-ready bill generation
- **Reports** – Total revenue, today’s sales, top-selling items
- **Pre-loaded Demo Data** – Ready menu with Coffee, Tea, Snacks, Beverages, Desserts

---

## How to Run (Direct)

### Requirements
- Python 3.8 or higher
- pip

### Steps

1. **Extract** this ZIP file

2. **Open terminal** in the project folder:
   ```
   cd Cafe_Management_System_Nilesh_Shelke
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python app.py
   ```

5. **Open browser** and go to:
   ```
   http://127.0.0.1:5000
   ```

---

## Login Credentials

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| Staff | staff    | staff123  |

---

## Project Structure

```
Cafe_Management_System_Nilesh_Shelke/
├── app.py                 # Main application
├── requirements.txt       # Python packages
├── README.md              # This file
├── database/              # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── menu.html
    ├── add_menu_item.html
    ├── edit_menu_item.html
    ├── orders.html
    ├── new_order.html
    ├── order_detail.html
    ├── bill.html
    └── reports.html
```

---

## Technologies Used

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Database**: SQLite (no extra setup needed)
- **Frontend**: HTML5, Bootstrap 5, Bootstrap Icons
- **Auth**: Werkzeug password hashing

---

## Developer

**Nilesh Shelke**

Cafe Management System – Full Stack Project

---

*Enjoy managing your cafe!*
