"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False,static_folder='static',template_folder='templates')
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        from app.admin import routes
        db.create_all()  # Create database tables for our data models

        return app
