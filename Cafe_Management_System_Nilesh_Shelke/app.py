"""
Cafe Management System
Developed by: Nilesh Shelke
A complete web-based Cafe Management System with menu, orders, billing, and admin panel.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nilesh_shelke_cafe_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')  # admin or staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(200), default='')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(100), default='Guest')
    status = db.Column(db.String(20), default='Pending')  # Pending, Preparing, Served, Paid, Cancelled
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # price at time of order
    menu_item = db.relationship('MenuItem')

# ==================== HELPERS ====================

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    preparing_orders = Order.query.filter_by(status='Preparing').count()
    today = datetime.utcnow().date()
    today_orders = Order.query.filter(db.func.date(Order.created_at) == today).all()
    today_revenue = sum(o.total_amount for o in today_orders if o.status == 'Paid')
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    menu_count = MenuItem.query.count()
    return render_template('dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           preparing_orders=preparing_orders,
                           today_revenue=today_revenue,
                           recent_orders=recent_orders,
                           menu_count=menu_count)

# ---------- Menu Management ----------

@app.route('/menu')
@login_required
def menu():
    categories = Category.query.all()
    items = MenuItem.query.all()
    return render_template('menu.html', categories=categories, items=items)

@app.route('/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        price = float(request.form.get('price', 0))
        category_id = int(request.form.get('category_id'))
        is_available = True if request.form.get('is_available') else False
        item = MenuItem(name=name, description=description, price=price,
                        category_id=category_id, is_available=is_available)
        db.session.add(item)
        db.session.commit()
        flash(f'Menu item "{name}" added successfully!', 'success')
        return redirect(url_for('menu'))
    return render_template('add_menu_item.html', categories=categories)

@app.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    categories = Category.query.all()
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description', '')
        item.price = float(request.form.get('price', 0))
        item.category_id = int(request.form.get('category_id'))
        item.is_available = True if request.form.get('is_available') else False
        db.session.commit()
        flash(f'Menu item "{item.name}" updated!', 'success')
        return redirect(url_for('menu'))
    return render_template('edit_menu_item.html', item=item, categories=categories)

@app.route('/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'Menu item "{name}" deleted.', 'info')
    return redirect(url_for('menu'))

@app.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        existing = Category.query.filter_by(name=name).first()
        if not existing:
            cat = Category(name=name)
            db.session.add(cat)
            db.session.commit()
            flash(f'Category "{name}" added!', 'success')
        else:
            flash('Category already exists.', 'warning')
    return redirect(url_for('menu'))

# ---------- Orders ----------

@app.route('/orders')
@login_required
def orders():
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        all_orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        all_orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=all_orders, status_filter=status_filter)

@app.route('/orders/new', methods=['GET', 'POST'])
@login_required
def new_order():
    categories = Category.query.all()
    items = MenuItem.query.filter_by(is_available=True).all()
    if request.method == 'POST':
        table_number = request.form.get('table_number')
        customer_name = request.form.get('customer_name', 'Guest')
        item_ids = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')

        if not item_ids:
            flash('Please select at least one item.', 'warning')
            return redirect(url_for('new_order'))

        order = Order(table_number=table_number, customer_name=customer_name, status='Pending')
        db.session.add(order)
        db.session.flush()

        total = 0.0
        for iid, qty in zip(item_ids, quantities):
            qty = int(qty)
            if qty > 0:
                menu_item = MenuItem.query.get(int(iid))
                if menu_item:
                    oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id,
                                   quantity=qty, price=menu_item.price)
                    db.session.add(oi)
                    total += menu_item.price * qty

        order.total_amount = total
        db.session.commit()
        flash(f'Order #{order.id} created successfully! Total: ₹{total:.2f}', 'success')
        return redirect(url_for('order_detail', order_id=order.id))

    return render_template('new_order.html', categories=categories, items=items)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_detail.html', order=order)

@app.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Preparing', 'Served', 'Paid', 'Cancelled']:
        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders/<int:order_id>/bill')
@login_required
def print_bill(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('bill.html', order=order)

# ---------- Reports ----------

@app.route('/reports')
@login_required
def reports():
    all_orders = Order.query.filter_by(status='Paid').all()
    total_revenue = sum(o.total_amount for o in all_orders)
    today = datetime.utcnow().date()
    today_orders = [o for o in all_orders if o.created_at.date() == today]
    today_revenue = sum(o.total_amount for o in today_orders)

    # Simple item sales count
    item_sales = {}
    for order in all_orders:
        for oi in order.items:
            name = oi.menu_item.name if oi.menu_item else 'Unknown'
            item_sales[name] = item_sales.get(name, 0) + oi.quantity

    top_items = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    return render_template('reports.html',
                           total_revenue=total_revenue,
                           today_revenue=today_revenue,
                           total_paid_orders=len(all_orders),
                           today_orders_count=len(today_orders),
                           top_items=top_items)

# ---------- Seed Data ----------

def seed_data():
    if User.query.first():
        return  # already seeded

    # Admin user
    admin = User(username='admin',
                 password=generate_password_hash('admin123'),
                 role='admin')
    staff = User(username='staff',
                 password=generate_password_hash('staff123'),
                 role='staff')
    db.session.add(admin)
    db.session.add(staff)

    # Categories
    cats = {
        'Coffee': Category(name='Coffee'),
        'Tea': Category(name='Tea'),
        'Snacks': Category(name='Snacks'),
        'Beverages': Category(name='Beverages'),
        'Desserts': Category(name='Desserts'),
    }
    for c in cats.values():
        db.session.add(c)
    db.session.flush()

    # Menu items
    menu_data = [
        ('Espresso', 'Strong black coffee', 80, 'Coffee'),
        ('Cappuccino', 'Espresso with steamed milk foam', 120, 'Coffee'),
        ('Latte', 'Espresso with lots of steamed milk', 130, 'Coffee'),
        ('Americano', 'Espresso diluted with hot water', 100, 'Coffee'),
        ('Cold Coffee', 'Chilled coffee with ice cream', 150, 'Coffee'),
        ('Masala Chai', 'Indian spiced tea', 40, 'Tea'),
        ('Green Tea', 'Healthy green tea', 50, 'Tea'),
        ('Lemon Tea', 'Refreshing lemon tea', 45, 'Tea'),
        ('Samosa', 'Crispy potato filled snack (2 pcs)', 40, 'Snacks'),
        ('Veg Sandwich', 'Fresh vegetable sandwich', 80, 'Snacks'),
        ('French Fries', 'Crispy golden fries', 90, 'Snacks'),
        ('Paneer Tikka', 'Grilled cottage cheese', 180, 'Snacks'),
        ('Fresh Lime Soda', 'Refreshing lime soda', 60, 'Beverages'),
        ('Mango Shake', 'Thick mango milkshake', 100, 'Beverages'),
        ('Chocolate Shake', 'Rich chocolate milkshake', 110, 'Beverages'),
        ('Brownie', 'Warm chocolate brownie', 90, 'Desserts'),
        ('Ice Cream', 'Vanilla / Chocolate scoop', 70, 'Desserts'),
        ('Cheesecake', 'Creamy New York style', 150, 'Desserts'),
    ]

    for name, desc, price, cat_name in menu_data:
        item = MenuItem(name=name, description=desc, price=price,
                        category_id=cats[cat_name].id, is_available=True)
        db.session.add(item)

    db.session.commit()
    print("Database seeded successfully!")

# ==================== MAIN ====================

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    with app.app_context():
        db.create_all()
        seed_data()
    print("=" * 50)
    print("  Cafe Management System")
    print("  Developed by: Nilesh Shelke")
    print("=" * 50)
    print("  Login Credentials:")
    print("  Admin  -> username: admin  | password: admin123")
    print("  Staff  -> username: staff  | password: staff123")
    print("=" * 50)
    print("  Open browser: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
