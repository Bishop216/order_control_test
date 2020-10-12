from flask_marshmallow import Marshmallow
from marshmallow import fields
from application.models import Product, Order, User

ma = Marshmallow()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = ma.auto_field()


class ProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Product

    id = ma.auto_field()
    name = ma.auto_field()
    price = fields.Method("price_method")
    date_created = ma.auto_field()

    @staticmethod
    def price_method(obj):
        return str(obj.price)


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order

    id = ma.auto_field()
    user_id = ma.auto_field()
    status = ma.auto_field()
    date_created = ma.auto_field()
    product = fields.Method("product_method")

    @staticmethod
    def product_method(obj):
        schema = ProductSchema()
        product = Product.query.filter_by(id=obj.product_id).first()
        return schema.dump(product)
