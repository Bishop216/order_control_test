import logging
from datetime import datetime

from flask import Blueprint, request, jsonify

from application.models import User, Product, Order, db
from application.auth import cashier_required, shop_assistant_required, accountant_required, blacklist_check
from application.serializer import ProductSchema, OrderSchema

from flask_jwt_extended import get_jwt_identity, jwt_required

logger = logging.getLogger(__file__)
bp = Blueprint('store', __name__, url_prefix='/store')


@bp.route("/create_order", methods=["POST"])
@jwt_required
@blacklist_check
def create_order():
    """
    Saves new order to DB
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity["username"]).first()

    product_id = request_json.get("product_id")

    if not product_id:
        return jsonify({"msg": "Missing product_id parameter"}), 400

    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({"msg": "Product doesn't exist"}), 400

    new_order = Order(user_id=user.id, product_id=product.id)

    db.session.add(new_order)
    db.session.commit()

    schema = OrderSchema()
    return jsonify(order=schema.dump(new_order)), 200


@bp.route("/confirm_order", methods=["POST"])
@jwt_required
@blacklist_check
@shop_assistant_required
def confirm_order():
    """
    Lets shop-assistant change order status to "completed"
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    order_id = request_json.get("order_id")

    if not order_id:
        return jsonify({"msg": "Missing order_id parameter"}), 400

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        return jsonify({"msg": "Order doesn't exist"}), 400

    order.status = "completed"

    db.session.commit()

    return jsonify(msg="success"), 200


@bp.route("/get_products", methods=["GET"])
def get_products():
    """
    Returns all the products
    :return:
    """
    products = Product.query.all()

    schema = ProductSchema(many=True)

    return jsonify(products=schema.dump(products)), 200


@bp.route("/get_bill", methods=["GET"])
@jwt_required
@blacklist_check
@cashier_required
def get_bill():
    """
    Returns the bill associated with specified order
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    order_id = request_json.get("order_id")

    if not order_id:
        return jsonify({"msg": "Missing order_id parameter"}), 400

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        return jsonify({"msg": "Order doesn't exist"}), 400

    schema = OrderSchema()
    return jsonify(order=schema.dump(order)), 200


@bp.route("/order_paid", methods=["POST"])
@jwt_required
@blacklist_check
@cashier_required
def order_paid():
    """
    Lets cashier change order status to "paid"
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    order_id = request_json.get("order_id")

    if not order_id:
        return jsonify({"msg": "Missing order_id parameter"}), 400

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        return jsonify({"msg": "Order doesn't exist"}), 400

    order.status = "paid"

    db.session.commit()

    return jsonify(msg="success"), 200


@bp.route("/get_orders", methods=["GET"])
@jwt_required
@blacklist_check
@accountant_required
def get_orders():
    """
    Lets accountant see all the orders
    :return:
    """
    request_json = request.get_json()

    if request_json:
        filters = request_json.get("filters")
        if filters:
            date_from = filters.get("date_from")
            date_to = filters.get("date_to")

            try:
                if date_from and date_to:
                    date_from = datetime.strptime(date_from, "%Y-%m-%d")
                    date_to = datetime.strptime(date_to, "%Y-%m-%d")
                    orders = Order.query.filter(Order.date_created >= date_from).filter(Order.date_created <= date_to)

                elif date_from:
                    date_from = datetime.strptime(date_from, "%Y-%m-%d")
                    orders = Order.query.filter(Order.date_created >= date_from)

                elif date_to:
                    date_to = datetime.strptime(date_to, "%Y-%m-%d")
                    orders = Order.query.filter(Order.date_created <= date_to)

                else:
                    orders = Order.query.all()

            except ValueError:
                orders = Order.query.all()

        else:
            orders = Order.query.all()

    else:
        orders = Order.query.all()

    schema = OrderSchema(many=True)
    return jsonify(orders=schema.dump(orders)), 200


