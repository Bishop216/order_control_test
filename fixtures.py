from application import create_app
from application.models import Product, User, db
from sqlalchemy.exc import IntegrityError

app = create_app()
app.app_context().push()

User.query.delete()
Product.query.delete()


def load_products():
    # Products
    product_1 = Product(name="product_1", price=29.99)
    db.session.add(product_1)

    product_2 = Product(name="product_2", price=15.00)
    db.session.add(product_2)

    product_3 = Product(name="product_3", price=12.34)
    db.session.add(product_3)

    db.session.commit()

    return True


def load_users():
    # Users
    cashier = User(username="user1", role="cashier")
    cashier.set_password("pass123")
    db.session.add(cashier)

    shop_assistant = User(username="user2", role="shop-assistant")
    shop_assistant.set_password("pass123")
    db.session.add(shop_assistant)

    accountant = User(username="user3", role="accountant")
    accountant.set_password("pass123")
    db.session.add(accountant)

    admin = User(username="user4", role="admin")
    admin.set_password("pass123")
    db.session.add(admin)

    db.session.commit()

    return True


if __name__ == "__main__":
    load_products()
    load_users()
