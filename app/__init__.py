import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app import logging_config


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    from app import models
    # Create or upgrade the database when the app starts
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logging.error(f"Error initializing database: {e}")

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    return app

