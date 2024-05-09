from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Create or upgrade the database when the app starts
    with app.app_context():
        db.create_all()
        # Apply migrations
        migrate_upgrade()

    return app

def migrate_upgrade():
    from flask_migrate import upgrade
    upgrade()
