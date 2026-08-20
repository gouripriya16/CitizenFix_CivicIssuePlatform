from datetime import datetime, timezone

from flask import render_template
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask import request, redirect, url_for, flash

from app import create_app, db
from app.models import User, Issue
from app.time_utils import format_india_time


app = create_app()


@app.template_filter("india_time")
def india_time_filter(value):
    return format_india_time(value)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already registered.")

            return redirect(
                url_for("register")
            )

        user = User(
            name=name,
            email=email,
            role="citizen"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please login."
        )

        return redirect(
            url_for("login")
        )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            if user.role == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    issues = Issue.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Issue.created_at.desc()
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

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "report_issue.html"
    )


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":

        flash("Access denied.")

        return redirect(
            url_for("dashboard")
        )


    # --------------------------------
    # Issue statistics
    # --------------------------------

    total_issues = Issue.query.count()

    pending_issues = Issue.query.filter_by(
        status="Pending"
    ).count()

    in_progress_issues = Issue.query.filter_by(
        status="In Progress"
    ).count()

    resolved_issues = Issue.query.filter_by(
        status="Resolved"
    ).count()


    # --------------------------------
    # Category statistics
    # --------------------------------

    all_issues = Issue.query.all()

    category_counts = {}

    for issue in all_issues:

        category = issue.category

        if category not in category_counts:

            category_counts[category] = 0

        category_counts[category] += 1


    category_counts = dict(
        sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


    # --------------------------------
    # Status filter
    # --------------------------------

    selected_status = request.args.get(
        "status",
        "All"
    )


    if selected_status == "All":

        issues = Issue.query.order_by(
            Issue.created_at.desc()
        ).all()

    else:

        issues = Issue.query.filter_by(
            status=selected_status
        ).order_by(
            Issue.created_at.desc()
        ).all()


    return render_template(
        "admin_dashboard.html",
        issues=issues,
        selected_status=selected_status,
        total_issues=total_issues,
        pending_issues=pending_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        category_counts=category_counts
    )


@app.route(
    "/admin/update-issue/<int:issue_id>",
    methods=["POST"]
)
@login_required
def update_issue_status(issue_id):

    if current_user.role != "admin":

        flash("Access denied.")

        return redirect(
            url_for("dashboard")
        )


    issue = Issue.query.get_or_404(
        issue_id
    )


    new_status = request.form["status"]

    issue.status = new_status

    issue.updated_at = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    db.session.commit()


    flash(
        "Issue status updated successfully."
    )


    return redirect(
        url_for(
            "admin_dashboard",
            status=request.form.get(
                "current_filter",
                "All"
            )
        )
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )


if __name__ == "__main__":
    app.run(debug=True)