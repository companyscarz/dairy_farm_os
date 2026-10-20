from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from ..auth import roles_required, get_current_user
from ..database import fetch_all, fetch_one, execute

bp = Blueprint("workers", __name__, url_prefix="/workers")


@bp.route("/", methods=["GET", "POST"])
@roles_required("owner", "manager")
def index():
    user = get_current_user()
    farm_id = user["farm_id"]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or "@" not in email or len(password) < 10:
            flash("Enter a name, valid email, and temporary password of at least 10 characters.", "error")
        elif fetch_one("SELECT id FROM users WHERE LOWER(email)=LOWER(%s)", (email,)):
            flash("That email address is already registered.", "error")
        else:
            execute(
                """INSERT INTO users(farm_id,name,email,password_hash,role,active)
                   VALUES(%s,%s,%s,%s,'worker',TRUE)""",
                (farm_id, name, email, generate_password_hash(password)),
            )
            flash("Worker account created. Share the temporary password securely.", "success")
            return redirect(url_for("workers.index"))
    workers = fetch_all(
        "SELECT id,name,email,role,active,created_at FROM users WHERE farm_id=%s ORDER BY created_at DESC,id DESC",
        (farm_id,),
    )
    return render_template("workers/index.html", active="workers", workers=workers)
