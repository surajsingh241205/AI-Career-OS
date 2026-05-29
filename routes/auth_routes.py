from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db
from app.models.user import User


auth = Blueprint(
    "auth",
    __name__
)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        # Hash password
        hashed_password = generate_password_hash(
            password
        )

        # Create user
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            flash(
                f"Welcome back, {user.name}!",
                "success"
            )

            return redirect(
                url_for("auth.dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


@auth.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=current_user
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )