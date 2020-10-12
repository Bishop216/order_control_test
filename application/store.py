import logging
from flask import Blueprint, request, jsonify

from application.models import User, Product, Order, db

from application.auth import cashier_required, shop_assistant_required, accountant_required

from application.serializer import ProductSchema, OrderSchema

from flask_jwt_extended import get_jwt_identity, jwt_required

logger = logging.getLogger(__file__)
bp = Blueprint('store', __name__, url_prefix='/store')


@bp.route("/create_order", methods=["POST"])
@jwt_required
def create_order():
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
@shop_assistant_required
def confirm_order():
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
    products = Product.query.all()

    schema = ProductSchema(many=True)

    return jsonify(products=schema.dump(products)), 200


@bp.route("/get_bill", methods=["GET"])
@jwt_required
@cashier_required
def get_bill():
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



