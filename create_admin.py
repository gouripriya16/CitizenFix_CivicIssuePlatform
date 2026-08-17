from app import create_app, db
from app.models import User


app = create_app()

with app.app_context():

    email = "mangagouripriya@gmail.com"

    existing_admin = User.query.filter_by(email=email).first()

    if existing_admin:
        print("Admin account already exists.")

    else:
        admin = User(
            name="CitizenFix Admin",
            email=email,
            role="admin"
        )

        admin.set_password("Priya@123")

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")
        print("Email: mangagouripriya@gmail.com")
        print("Password: Priya@123")