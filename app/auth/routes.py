from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import authenticate, login_user, logout_user, get_current_user, first_admin_exists, create_initial_admin

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("dashboard.dashboard"))
    if request.method == "POST":
        user = authenticate(request.form.get("email", ""), request.form.get("password", ""))
        if not user:
            flash("Invalid email or password.", "error")
        else:
            login_user(user)
            return redirect(request.args.get("next") or url_for("dashboard.dashboard"))
    return render_template("auth/login.html")


@bp.route("/setup", methods=["GET", "POST"])
def setup():
    if first_admin_exists():
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        farm_name = request.form.get("farm_name", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not farm_name or not name or not email or len(password) < 10:
            flash("Complete all required fields. Password must be at least 10 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                user = create_initial_admin(
                    farm_name, request.form.get("location", "").strip(), name, email, password,
                    request.form.get("phone", "").strip(), request.form.get("farm_email", "").strip()
                )
                login_user(user)
                flash("Administrator account created. Welcome to FarmOS.", "success")
                return redirect(url_for("settings.settings_page"))
            except Exception as exc:
                flash("Could not create the administrator. Check the details and try again.", "error")
    return render_template("auth/setup.html")


@bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
