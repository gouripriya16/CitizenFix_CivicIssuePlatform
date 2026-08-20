from datetime import datetime, timezone

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import create_app, db
from app.models import User, Issue
from app.time_utils import format_india_time
from app.priority_predictor import predict_priority
from app.duplicate_detector import find_possible_duplicate


app = create_app()


# ==========================================================
# INDIA TIME FILTER
# ==========================================================

@app.template_filter("india_time")
def india_time_filter(value):

    return format_india_time(value)


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================================
# REGISTER
# ==========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered."
            )

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

    return render_template(
        "register.html"
    )


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            if user.role == "admin":

                return redirect(
                    url_for(
                        "admin_dashboard"
                    )
                )

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        flash(
            "Invalid email or password."
        )

    return render_template(
        "login.html"
    )


# ==========================================================
# CITIZEN DASHBOARD
# ==========================================================

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


# ==========================================================
# REPORT ISSUE
# ==========================================================

@app.route(
    "/report-issue",
    methods=["GET", "POST"]
)
@login_required
def report_issue():

    if request.method == "POST":

        title = request.form[
            "title"
        ].strip()

        description = request.form[
            "description"
        ].strip()

        category = request.form[
            "category"
        ].strip()

        location = request.form[
            "location"
        ].strip()


        # --------------------------------------------------
        # DUPLICATE DETECTION
        # --------------------------------------------------

        existing_issues = Issue.query.all()

        duplicate_result = find_possible_duplicate(
            title,
            description,
            category,
            location,
            existing_issues
        )


        # --------------------------------------------------
        # If duplicate is found
        # --------------------------------------------------

        if duplicate_result["is_duplicate"]:

            duplicate_issue = duplicate_result["issue"]

            score = duplicate_result["score"] * 100

            flash(
                f"Possible duplicate issue detected. "
                f"This appears similar to: "
                f"'{duplicate_issue.title}' "
                f"({score:.0f}% similarity). "
                f"Please check before submitting."
            )

            return redirect(
                url_for(
                    "report_issue"
                )
            )


        # --------------------------------------------------
        # AUTOMATIC PRIORITY PREDICTION
        # --------------------------------------------------

        predicted_priority = predict_priority(
            title,
            description,
            category
        )


        # --------------------------------------------------
        # CREATE ISSUE
        # --------------------------------------------------

        issue = Issue(

            title=title,

            description=description,

            category=category,

            location=location,

            priority=predicted_priority,

            status="Pending",

            user_id=current_user.id

        )


        db.session.add(issue)

        db.session.commit()


        flash(
            f"Issue reported successfully. "
            f"Suggested priority: "
            f"{predicted_priority}."
        )


        return redirect(
            url_for(
                "dashboard"
            )
        )


    return render_template(
        "report_issue.html"
    )


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":

        flash(
            "Access denied."
        )

        return redirect(
            url_for("dashboard")
        )


    # --------------------------------------------------
    # ISSUE STATISTICS
    # --------------------------------------------------

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


    # --------------------------------------------------
    # PRIORITY STATISTICS
    # --------------------------------------------------

    high_priority = Issue.query.filter_by(
        priority="High"
    ).count()

    medium_priority = Issue.query.filter_by(
        priority="Medium"
    ).count()

    low_priority = Issue.query.filter_by(
        priority="Low"
    ).count()


    # --------------------------------------------------
    # CATEGORY STATISTICS
    # --------------------------------------------------

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


    # --------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------

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

        high_priority=high_priority,

        medium_priority=medium_priority,

        low_priority=low_priority,

        category_counts=category_counts

    )


# ==========================================================
# UPDATE ISSUE STATUS
# ==========================================================

@app.route(
    "/admin/update-issue/<int:issue_id>",
    methods=["POST"]
)
@login_required
def update_issue_status(issue_id):

    if current_user.role != "admin":

        flash(
            "Access denied."
        )

        return redirect(
            url_for("dashboard")
        )


    issue = Issue.query.get_or_404(
        issue_id
    )


    new_status = request.form[
        "status"
    ]


    issue.status = new_status


    issue.updated_at = datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )


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


# ==========================================================
# UPDATE ISSUE PRIORITY
# ==========================================================

@app.route(
    "/admin/update-priority/<int:issue_id>",
    methods=["POST"]
)
@login_required
def update_issue_priority(issue_id):

    if current_user.role != "admin":

        flash(
            "Access denied."
        )

        return redirect(
            url_for("dashboard")
        )


    issue = Issue.query.get_or_404(
        issue_id
    )


    new_priority = request.form[
        "priority"
    ]


    if new_priority not in [
        "High",
        "Medium",
        "Low"
    ]:

        flash(
            "Invalid priority selected."
        )

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    issue.priority = new_priority


    issue.updated_at = datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )


    db.session.commit()


    flash(
        "Issue priority updated successfully."
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


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )