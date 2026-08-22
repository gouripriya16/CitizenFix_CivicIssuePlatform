import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )


    # ==========================================================
    # APPLICATION CONFIGURATION
    # ==========================================================

    app.config["SECRET_KEY"] = "citizenfix-secret-key-2026"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///citizenfix.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # ==========================================================
    # FILE UPLOAD CONFIGURATION
    # ==========================================================

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.static_folder,
        "uploads"
    )

    app.config["MAX_CONTENT_LENGTH"] = (
        5 * 1024 * 1024
    )


    # ==========================================================
    # INITIALIZE EXTENSIONS
    # ==========================================================

    db.init_app(app)

    login_manager.init_app(app)


    # ==========================================================
    # LOGIN CONFIGURATION
    # ==========================================================

    login_manager.login_view = "login"


    from .models import User


    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )


    # ==========================================================
    # CREATE DATABASE TABLES
    # ==========================================================

    with app.app_context():

        db.create_all()


    return app