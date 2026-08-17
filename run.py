from flask import render_template
from flask_login import login_user, logout_user, login_required, current_user
from flask import request, redirect, url_for, flash

from app import create_app, db
from app.models import User, Issue


app = create_app()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
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

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            # Temporary debug information
            print(
                "LOGIN:",
                user.name,
                user.email,
                user.role,
                user.id
            )

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    issues = Issue.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "dashboard.html",
        issues=issues
    )


@app.route("/report-issue", methods=["GET", "POST"])
@login_required
def report_issue():

    if request.method == "POST":

        title = request.form["title"].strip()
        description = request.form["description"].strip()
        category = request.form["category"]
        location = request.form["location"].strip()

        issue = Issue(
            title=title,
            description=description,
            category=category,
            location=location,
            user_id=current_user.id
        )

        db.session.add(issue)
        db.session.commit()

        flash("Issue reported successfully.")

        return redirect(url_for("dashboard"))

    return render_template("report_issue.html")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    issues = Issue.query.all()

    return render_template(
        "admin_dashboard.html",
        issues=issues
    )


@app.route("/admin/update-issue/<int:issue_id>", methods=["POST"])
@login_required
def update_issue_status(issue_id):

    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    issue = Issue.query.get_or_404(issue_id)

    new_status = request.form["status"]

    issue.status = new_status

    db.session.commit()

    flash("Issue status updated successfully.")

    return redirect(url_for("admin_dashboard"))


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)