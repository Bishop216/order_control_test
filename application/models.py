from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import calendar

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

    def get_discount(self):
        current_date = datetime.utcnow()
        days_in_month = calendar.monthrange(self.date_created.year, self.date_created.month)[1]
        month_later = self.date_created + timedelta(days=days_in_month)

        if current_date >= month_later:
            # 20% discount
            return 20
        else:
            return None

    def get_current_price(self):
        discount = self.get_discount()
        if discount:
            return str(self.price - self.price * (self.get_discount() / 100))
        else:
            return str(self.price)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="processing")
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
