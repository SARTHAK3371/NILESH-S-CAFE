import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from models import db, User, Category, MenuItem, Table, Customer, Order, OrderItem

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cafe-secret-key-change-in-production-2024')

# Database - works on local + Render
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local fallback (SQLite) - change to PostgreSQL when ready
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

        # Default admin - SARTHAK WALUNJ
admin = User.query.filter_by(username='SARTHAKWALUNJ').first()
if not admin:
            admin = User(username='SARTHAKWALUNJ', name='SARTHAK WALUNJ', role='admin')
            admin.set_password('3371')
            db.session.add(admin)
        else:
            admin.set_password('3371')
            admin.name = 'SARTHAK WALUNJ'
        db.session.commit()

        # Sample categories
        if Category.query.count() == 0:
            cats = ['Coffee', 'Tea', 'Snacks', 'Desserts', 'Beverages']
            for c in cats:
                db.session.add(Category(name=c))
            db.session.commit()

            # Sample menu with Unsplash images
            samples = [
                ('Espresso', 'Strong Italian coffee', 80, 'Coffee', 'https://images.unsplash.com/photo-1510591509098-f4fdc6d0f0b6?w=400'),
                ('Cappuccino', 'Espresso with steamed milk foam', 120, 'Coffee', 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400'),
                ('Latte', 'Smooth milk coffee', 130, 'Coffee', 'https://images.unsplash.com/photo-1561882468-9110e03e0f78?w=400'),
                ('Americano', 'Espresso with hot water', 100, 'Coffee', 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400'),
                ('Masala Chai', 'Spiced Indian tea', 60, 'Tea', 'https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=400'),
                ('Green Tea', 'Healthy green tea', 70, 'Tea', 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400'),
                ('Sandwich', 'Veg grilled sandwich', 90, 'Snacks', 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400'),
                ('Burger', 'Classic veg burger', 110, 'Snacks', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'),
                ('Brownie', 'Chocolate brownie with ice cream', 150, 'Desserts', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400'),
                ('Cold Coffee', 'Iced coffee with cream', 140, 'Beverages', 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400'),
            ]
            for name, desc, price, cat_name, img in samples:
                cat = Category.query.filter_by(name=cat_name).first()
                item = MenuItem(name=name, description=desc, price=price, image_url=img, category_id=cat.id)
                db.session.add(item)

        # Sample tables
        if Table.query.count() == 0:
            for i in range(1, 11):
                db.session.add(Table(number=i, capacity=4 if i <= 6 else 6))

        db.session.commit()
        print("Database initialized with sample data!")

# ---------- Routes ----------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    today_orders = Order.query.filter(db.func.date(Order.created_at) == today).all()
    total_sales = sum(o.total_amount for o in today_orders if o.status != 'cancelled')
    pending = Order.query.filter_by(status='pending').count()
    preparing = Order.query.filter_by(status='preparing').count()
    available_tables = Table.query.filter_by(status='available').count()
    
    # Popular items
    popular = db.session.query(
        MenuItem.name, db.func.sum(OrderItem.quantity).label('qty')
    ).join(OrderItem).group_by(MenuItem.name).order_by(db.desc('qty')).limit(5).all()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    
    return render_template('dashboard.html',
                           total_sales=total_sales,
                           order_count=len(today_orders),
                           pending=pending,
                           preparing=preparing,
                           available_tables=available_tables,
                           popular=popular,
                           recent_orders=recent_orders)

# ---- Menu ----
@app.route('/menu')
@login_required
def menu():
    categories = Category.query.all()
    items = MenuItem.query.order_by(MenuItem.name).all()
    return render_template('menu.html', categories=categories, items=items)

@app.route('/menu/add', methods=['POST'])
@login_required
def add_menu_item():
    name = request.form.get('name')
    price = float(request.form.get('price', 0))
    desc = request.form.get('description')
    cat_id = request.form.get('category_id')
    img = request.form.get('image_url') or 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400'
    stock = int(request.form.get('stock', 100))
    
    item = MenuItem(name=name, price=price, description=desc, category_id=cat_id, image_url=img, stock=stock)
    db.session.add(item)
    db.session.commit()
    flash('Menu item added!', 'success')
    return redirect(url_for('menu'))

@app.route('/menu/edit/<int:id>', methods=['POST'])
@login_required
def edit_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    item.name = request.form.get('name')
    item.price = float(request.form.get('price'))
    item.description = request.form.get('description')
    item.category_id = request.form.get('category_id')
    item.image_url = request.form.get('image_url')
    item.stock = int(request.form.get('stock', 100))
    item.is_available = True if request.form.get('is_available') else False
    db.session.commit()
    flash('Item updated!', 'success')
    return redirect(url_for('menu'))

@app.route('/menu/delete/<int:id>')
@login_required
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'info')
    return redirect(url_for('menu'))

# ---- Orders ----
@app.route('/orders')
@login_required
def orders():
    status = request.args.get('status')
    query = Order.query.order_by(Order.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    all_orders = query.limit(50).all()
    tables = Table.query.all()
    items = MenuItem.query.filter_by(is_available=True).all()
    customers = Customer.query.all()
    return render_template('orders.html', orders=all_orders, tables=tables, items=items, customers=customers)

@app.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    table_id = request.form.get('table_id') or None
    customer_id = request.form.get('customer_id') or None
    notes = request.form.get('notes')
    item_ids = request.form.getlist('item_id')
    quantities = request.form.getlist('quantity')

    order = Order(table_id=table_id, customer_id=customer_id, notes=notes, status='pending')
    db.session.add(order)
    db.session.flush()

    total = 0
    for iid, qty in zip(item_ids, quantities):
        if not iid or not qty:
            continue
        menu_item = MenuItem.query.get(int(iid))
        qty = int(qty)
        if menu_item and qty > 0:
            oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=qty, price=menu_item.price)
            db.session.add(oi)
            total += menu_item.price * qty
            menu_item.stock = max(0, menu_item.stock - qty)

    order.total_amount = total
    if table_id:
        table = Table.query.get(int(table_id))
        if table:
            table.status = 'occupied'
    db.session.commit()
    flash(f'Order #{order.id} created successfully!', 'success')
    return redirect(url_for('orders'))

@app.route('/orders/status/<int:id>/<status>')
@login_required
def update_order_status(id, status):
    order = Order.query.get_or_404(id)
    order.status = status
    if status == 'completed' and order.table_id:
        table = Table.query.get(order.table_id)
        if table:
            table.status = 'available'
    db.session.commit()
    flash(f'Order status updated to {status}', 'success')
    return redirect(url_for('orders'))

# ---- Tables ----
@app.route('/tables')
@login_required
def tables():
    all_tables = Table.query.order_by(Table.number).all()
    return render_template('tables.html', tables=all_tables)

@app.route('/tables/add', methods=['POST'])
@login_required
def add_table():
    number = int(request.form.get('number'))
    capacity = int(request.form.get('capacity', 4))
    if Table.query.filter_by(number=number).first():
        flash('Table number already exists', 'danger')
    else:
        db.session.add(Table(number=number, capacity=capacity))
        db.session.commit()
        flash('Table added!', 'success')
    return redirect(url_for('tables'))

@app.route('/tables/status/<int:id>/<status>')
@login_required
def update_table_status(id, status):
    table = Table.query.get_or_404(id)
    table.status = status
    db.session.commit()
    return redirect(url_for('tables'))

# ---- Customers ----
@app.route('/customers')
@login_required
def customers():
    all_customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=all_customers)

@app.route('/customers/add', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    db.session.add(Customer(name=name, phone=phone, email=email))
    db.session.commit()
    flash('Customer added!', 'success')
    return redirect(url_for('customers'))

# ---- Inventory ----
@app.route('/inventory')
@login_required
def inventory():
    items = MenuItem.query.order_by(MenuItem.stock).all()
    return render_template('inventory.html', items=items)

@app.route('/inventory/update/<int:id>', methods=['POST'])
@login_required
def update_stock(id):
    item = MenuItem.query.get_or_404(id)
    item.stock = int(request.form.get('stock', 0))
    db.session.commit()
    flash('Stock updated!', 'success')
    return redirect(url_for('inventory'))

# ---- Bill ----
@app.route('/bill/<int:order_id>')
@login_required
def bill(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('bill.html', order=order)

# Tables create करा (Render + Local दोन्हीसाठी)
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
