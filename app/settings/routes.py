from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_one, execute

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/", methods=["GET", "POST"])
@roles_required("owner", "manager")
def settings_page():
    user = get_current_user()
    farm = fetch_one("SELECT * FROM farms WHERE id=%s", (user["farm_id"],))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        currency = request.form.get("currency", "UGX").strip().upper()
        timezone = request.form.get("timezone", "Africa/Kampala").strip()
        try:
            ZoneInfo(timezone)
            valid_timezone = True
        except (ZoneInfoNotFoundError, ValueError):
            valid_timezone = False

        if not name:
            flash("Farm name is required.", "error")
        elif currency not in {"UGX", "USD"}:
            flash("Choose a supported currency.", "error")
        elif not valid_timezone:
            flash("Enter a valid IANA timezone, such as Africa/Kampala.", "error")
        else:
            execute(
                """UPDATE farms
                   SET name=%s,location=%s,phone=%s,email=%s,currency=%s,timezone=%s,
                       updated_at=CURRENT_TIMESTAMP
                   WHERE id=%s""",
                (name, request.form.get("location", "").strip() or None,
                 request.form.get("phone", "").strip() or None,
                 request.form.get("email", "").strip() or None,
                 currency, timezone, user["farm_id"]),
            )
            flash("Farm settings updated.", "success")
        return redirect(url_for("settings.settings_page"))
    return render_template("settings/index.html", active="settings", farm=farm, user=user)


@bp.post("/profile")
@login_required
def update_profile():
    user = get_current_user()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    current_password = request.form.get("current_password", "")
    if not name or not email or "@" not in email or email.startswith("@") or email.endswith("@"):
        flash("Enter a valid name and email address.", "error")
        return redirect(url_for("settings.settings_page"))
    row = fetch_one("SELECT password_hash FROM users WHERE id=%s", (user["id"],))
    if not row or not check_password_hash(row["password_hash"], current_password):
        flash("Enter your current password to confirm profile changes.", "error")
        return redirect(url_for("settings.settings_page"))
    existing = fetch_one("SELECT id FROM users WHERE LOWER(email)=LOWER(%s) AND id<>%s", (email, user["id"]))
    if existing:
        flash("That email address is already used by another account.", "error")
        return redirect(url_for("settings.settings_page"))
    execute("UPDATE users SET name=%s,email=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s",
            (name, email, user["id"]))
    flash("Administrator details updated.", "success")
    return redirect(url_for("settings.settings_page"))


@bp.post("/password")
@login_required
def password():
    user = get_current_user()
    old = request.form.get("current_password", "")
    new = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")
    row = fetch_one("SELECT password_hash FROM users WHERE id=%s", (user["id"],))
    if not row or not check_password_hash(row["password_hash"], old):
        flash("Current password is incorrect.", "error")
    elif len(new) < 10:
        flash("New password must be at least 10 characters.", "error")
    elif new != confirm:
        flash("New passwords do not match.", "error")
    else:
        execute("UPDATE users SET password_hash=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s",
                (generate_password_hash(new), user["id"]))
        flash("Password changed successfully.", "success")
    return redirect(url_for("settings.settings_page"))
