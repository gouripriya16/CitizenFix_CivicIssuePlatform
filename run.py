from flask import render_template
from flask_login import login_user, logout_user, login_required
from flask import request, redirect, url_for, flash

from app import create_app, db
from app.models import User


app = create_app()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        # email = request.form["email"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            role="citizen"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # email = request.form["email"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)