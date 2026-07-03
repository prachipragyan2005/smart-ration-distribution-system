from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))

class Beneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ration_card = db.Column(db.String(100))
    members = db.Column(db.Integer)

# 🍚 Ration Item Table
class RationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    unit = db.Column(db.String(20))          # e.g. kg, litre
    price_per_unit = db.Column(db.Float)

# 📦 Stock Table
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('ration_item.id'))
    shop_name = db.Column(db.String(100))
    quantity = db.Column(db.Float)
    item = db.relationship('RationItem', backref='stocks')

# 🚚 Distribution Table
class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('ration_item.id'))
    quantity = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    beneficiary = db.relationship('Beneficiary', backref='distributions')
    item = db.relationship('RationItem', backref='distributions')

# 📝 Audit Log Table
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    performed_by = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 📢 Complaint Table
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Open")
    date = db.Column(db.DateTime, default=datetime.utcnow)

    beneficiary = db.relationship('Beneficiary', backref='complaints')