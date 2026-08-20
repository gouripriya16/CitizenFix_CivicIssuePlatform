import os

from dotenv import load_dotenv

from app import create_app, db
from app.models import User


load_dotenv()

app = create_app()

with app.app_context():

    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email or not password:
        print("ADMIN_EMAIL or ADMIN_PASSWORD is missing from .env")
        exit()

    existing_admin = User.query.filter_by(email=email).first()

    if existing_admin:

        print("Admin account already exists.")

    else:

        admin = User(
            name="CitizenFix Admin",
            email=email,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")
        print("Email:", email)