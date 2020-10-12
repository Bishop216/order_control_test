from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=True)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(20, 2), default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="processing")
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
