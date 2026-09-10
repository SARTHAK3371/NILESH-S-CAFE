# Cafe Management System

Professional Cafe Management System built with Flask + PostgreSQL + HTML/CSS/JS.

## Features
- Admin Login
- Dashboard with live stats
- Menu Management (CRUD + images)
- Order Management with status flow
- Table Management
- Customer Management
- Inventory / Stock tracking
- Billing / Invoice print
- Beautiful coffee-themed UI with Unsplash images

## Default Login
- Username: `admin`
- Password: `admin123`

## Local Run (CMD / Terminal)

```bash
cd cafe_management
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

> Note: By default uses SQLite. For PostgreSQL set DATABASE_URL in .env

## Deploy on Render
1. Push this folder to GitHub
2. Create new Web Service on Render
3. Add PostgreSQL database
4. Set Environment Variables:
   - DATABASE_URL = (from Render Postgres)
   - SECRET_KEY = any random string
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`

## Tech Stack
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- Backend: Python Flask
- Database: PostgreSQL (SQLite fallback for local)
