from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

migrate = Migrate()
jwt = JWTManager()


def create_app():
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__)

    # Config
    from application.config import Config
    app.config.from_object(Config)

    # SQLAlchemy
    from application.models import db
    db.init_app(app)

    # Migrate
    migrate.init_app(app, db)

    # JWT
    jwt.init_app(app)

    # Marshmallow serializer
    from application.serializer import ma
    ma.init_app(app)

    # Blueprint
    from application.auth import bp as bp_auth
    from application.store import bp as bp_store
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_store)

    return app
