import logging
from functools import wraps

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from flask_jwt_extended import create_access_token, get_jwt_identity, get_raw_jwt, \
    jwt_required, jwt_refresh_token_required, create_refresh_token

from application.models import User, db
from application.serializer import UserSchema

from redis import StrictRedis

logger = logging.getLogger(__file__)
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Redis for storing blacklisted auth tokens
redis_conn = StrictRedis()


# Decorator that restricts access to endpoint only to user with admin role
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity['role'] == 'admin':
            return jsonify(message="You are not admin"), 403
        return func(*args, **kwargs)

    return wrapper


# Decorator that restricts access to endpoint only to user with cashier role
def cashier_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity['role'] == 'cashier':
            return jsonify(message="You are not cashier"), 403
        return func(*args, **kwargs)

    return wrapper


# Decorator that restricts access to endpoint only to user with shop-assistant role
def shop_assistant_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity['role'] == 'shop-assistant':
            return jsonify(message="You are not shop-assistant"), 403
        return func(*args, **kwargs)

    return wrapper


# Decorator that restricts access to endpoint only to user with accountant role
def accountant_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity['role'] == 'accountant':
            return jsonify(message="You are not accountant"), 403
        return func(*args, **kwargs)

    return wrapper


# Decorator that checks if user JWT token is blacklisted
def blacklist_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        jti = get_raw_jwt()['jti']
        if redis_conn.get('disabled_token' + jti):
            return jsonify(message='Unauthorized'), 401
        return func(*args, **kwargs)

    return wrapper


@bp.route("/signup", methods=["POST"])
def signup():
    """
    Signup
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request_json.get('username')
    password = request_json.get('password')

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({"msg": "Username is already in use "}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    schema = UserSchema()
    return jsonify(user=schema.dump(new_user)), 200


@bp.route("/login", methods=["POST"])
def login():
    """
    Login
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request_json.get('username')
    password = request_json.get('password')

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 400

    identity = {
        "username": user.username,
        "role": user.role
    }

    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@bp.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    """
    Refreshes user access token
    :return:
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200


@bp.route("/logout", methods=["GET"])
@jwt_required
@blacklist_check
def logout():
    """
    Logout
    :return:
    """
    jti = get_raw_jwt().get("jti")
    redis_conn.set("disabled_token" + jti, 1, 3600)
    return jsonify(msg="success"), 200


@bp.route("/set_role", methods=["PATCH"])
@jwt_required
@blacklist_check
@admin_required
def set_role():
    """
    Allows admin to assign a role to user
    :return:
    """
    request_json = request.get_json()

    if not request_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request_json.get('username')
    role = request_json.get('role')

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not role:
        return jsonify({"msg": "Missing role parameter"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "User doesn't exist"}), 400

    user.role = role

    db.session.commit()

    return jsonify(msg="success"), 200
