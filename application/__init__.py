from flask import Flask
from flask_migrate import Migrate

migrate = Migrate()


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

    # Blueprint
    from application.parser import bp
    app.register_blueprint(bp)

    return app
