import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, Beneficiary, RationItem, Stock, Distribution, AuditLog, Complaint
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

def login_required(role=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return "Access denied ❌"
            return f(*args, **kwargs)
        return decorated
    return wrapper

def log_action(action):
    entry = AuditLog(
        action=action,
        performed_by=session.get('user_id', 'unknown')
    )
    db.session.add(entry)
    db.session.commit()

@app.route('/')
def home():
    return "Home Page"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            elif user.role == "user":
                return redirect(url_for('user_dashboard'))
            elif user.role == "shopkeeper":
                return redirect(url_for('stop_dashboard'))
            else:
                return "Role not defined"
        else:
            return "Invalid Credentials ❌"
    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/user_dashboard')
@login_required('user')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/stop_dashboard')
@login_required('shopkeeper')
def stop_dashboard():
    return render_template('stop_dashboard.html')

@app.route('/add_beneficiary', methods=['GET', 'POST'])
@login_required('admin')
def add_beneficiary():
    if request.method == 'POST':
        name = request.form['name'].strip()
        ration_card = request.form['ration_card'].strip()
        if not name or not ration_card:
            return "Name and Ration Card are required ❌"
        new_data = Beneficiary(
            name=name,
            ration_card=ration_card,
            members=request.form['members']
        )
        db.session.add(new_data)
        db.session.commit()
        log_action(f"Added beneficiary: {new_data.name}")
        return redirect(url_for('view_beneficiary'))
    return render_template('edit_beneficiary.html', data={})

@app.route('/view_beneficiary')
@login_required('admin')
def view_beneficiary():
    data = Beneficiary.query.all()
    return render_template('view_beneficiary.html', data=data)

@app.route('/delete/<int:id>')
@login_required('admin')
def delete(id):
    data = Beneficiary.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    log_action(f"Deleted beneficiary: {data.name}")
    return redirect(url_for('view_beneficiary'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required('admin')
def edit(id):
    data = Beneficiary.query.get_or_404(id)
    if request.method == 'POST':
        data.name = request.form['name']
        data.ration_card = request.form['ration_card']
        data.members = request.form['members']
        db.session.commit()
        log_action(f"Edited beneficiary: {data.name}")
        return redirect(url_for('view_beneficiary'))
    return render_template('edit_beneficiary.html', data=data)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required('admin')
def add_item():
    if request.method == 'POST':
        item = RationItem(
            name=request.form['name'],
            unit=request.form['unit'],
            price_per_unit=request.form['price_per_unit']
        )
        db.session.add(item)
        db.session.commit()
        log_action(f"Added ration item: {item.name}")
        return redirect(url_for('view_stock'))
    return render_template('add_item.html')

@app.route('/add_stock', methods=['GET', 'POST'])
@login_required('admin')
def add_stock():
    items = RationItem.query.all()
    if request.method == 'POST':
        stock = Stock(
            item_id=request.form['item_id'],
            shop_name=request.form['shop_name'],
            quantity=request.form['quantity']
        )
        db.session.add(stock)
        db.session.commit()
        log_action(f"Added stock: {stock.quantity} units to {stock.shop_name}")
        return redirect(url_for('view_stock'))
    return render_template('add_stock.html', items=items)

@app.route('/view_stock')
@login_required('admin')
def view_stock():
    stocks = Stock.query.all()
    return render_template('view_stock.html', stocks=stocks)

@app.route('/delete_stock/<int:id>')
@login_required('admin')
def delete_stock(id):
    stock = Stock.query.get_or_404(id)
    db.session.delete(stock)
    db.session.commit()
    log_action(f"Deleted stock ID {id}")
    return redirect(url_for('view_stock'))

@app.route('/view_items')
@login_required('admin')
def view_items():
    items = RationItem.query.all()
    return render_template('view_items.html', items=items)

@app.route('/delete_item/<int:id>')
@login_required('admin')
def delete_item(id):
    item = RationItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    log_action(f"Deleted ration item: {item.name}")
    return redirect(url_for('view_items'))

@app.route('/distribute', methods=['GET', 'POST'])
@login_required('admin')
def distribute():
    beneficiaries = Beneficiary.query.all()
    items = RationItem.query.all()
    if request.method == 'POST':
        beneficiary_id = request.form['beneficiary_id']
        item_id = request.form['item_id']
        quantity = float(request.form['quantity'])
        this_month = datetime.utcnow().month
        this_year = datetime.utcnow().year
        existing = Distribution.query.filter_by(
            beneficiary_id=beneficiary_id,
            item_id=item_id
        ).filter(
            db.extract('month', Distribution.date) == this_month,
            db.extract('year', Distribution.date) == this_year
        ).first()
        if existing:
            return "This beneficiary already received this item this month ❌"
        stock = Stock.query.filter_by(item_id=item_id).first()
        if not stock or stock.quantity < quantity:
            return "Not enough stock available ❌"
        stock.quantity -= quantity
        record = Distribution(
            beneficiary_id=beneficiary_id,
            item_id=item_id,
            quantity=quantity
        )
        db.session.add(record)
        db.session.commit()
        log_action(f"Distributed {quantity} units to beneficiary ID {beneficiary_id}")
        return redirect(url_for('view_distribution'))
    return render_template('distribute.html', beneficiaries=beneficiaries, items=items)

@app.route('/view_distribution')
@login_required('admin')
def view_distribution():
    records = Distribution.query.all()
    return render_template('view_distribution.html', records=records)

@app.route('/view_logs')
@login_required('admin')
def view_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('view_logs.html', logs=logs)

@app.route('/report_monthly')
@login_required('admin')
def report_monthly():
    this_month = datetime.utcnow().month
    this_year = datetime.utcnow().year
    results = db.session.query(
        RationItem.name,
        func.sum(Distribution.quantity)
    ).join(Distribution, Distribution.item_id == RationItem.id).filter(
        db.extract('month', Distribution.date) == this_month,
        db.extract('year', Distribution.date) == this_year
    ).group_by(RationItem.name).all()
    return render_template('report_monthly.html', results=results)

@app.route('/report_stock')
@login_required('admin')
def report_stock():
    stocks = Stock.query.all()
    return render_template('report_stock.html', stocks=stocks)

@app.route('/report_performance')
@login_required('admin')
def report_performance():
    total_beneficiaries = Beneficiary.query.count()
    total_distributions = Distribution.query.count()
    total_items = RationItem.query.count()
    total_stock_shops = db.session.query(Stock.shop_name).distinct().count()
    return render_template('report_performance.html',
        total_beneficiaries=total_beneficiaries,
        total_distributions=total_distributions,
        total_items=total_items,
        total_stock_shops=total_stock_shops
    )

@app.route('/raise_complaint', methods=['GET', 'POST'])
@login_required('admin')
def raise_complaint():
    beneficiaries = Beneficiary.query.all()
    if request.method == 'POST':
        description = request.form['description'].strip()
        if not description:
            return "Description cannot be empty ❌"
        complaint = Complaint(
            beneficiary_id=request.form['beneficiary_id'],
            description=description
        )
        db.session.add(complaint)
        db.session.commit()
        log_action(f"Complaint raised by beneficiary ID {complaint.beneficiary_id}")
        return redirect(url_for('view_complaints'))
    return render_template('raise_complaint.html', beneficiaries=beneficiaries)

@app.route('/view_complaints')
@login_required('admin')
def view_complaints():
    complaints = Complaint.query.order_by(Complaint.date.desc()).all()
    return render_template('view_complaints.html', complaints=complaints)

@app.route('/resolve_complaint/<int:id>')
@login_required('admin')
def resolve_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    complaint.status = "Resolved"
    db.session.commit()
    log_action(f"Resolved complaint ID {id}")
    return redirect(url_for('view_complaints'))

@app.errorhandler(404)
def page_not_found(e):
    return "Page Not Found ❌ (404)", 404

@app.errorhandler(500)
def internal_error(e):
    return "Something went wrong on our end ❌ (500)", 500

if __name__ == '__main__':
    app.run(debug=True)