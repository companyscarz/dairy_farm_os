from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from ..auth import roles_required, get_current_user
from ..database import fetch_all, fetch_one, execute

bp = Blueprint("workers", __name__, url_prefix="/workers")


def _farm_worker(worker_id, farm_id):
    return fetch_one(
        "SELECT id,name,email,role,active,created_at FROM users WHERE id=%s AND farm_id=%s AND role='worker'",
        (worker_id, farm_id),
    )


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
        "SELECT id,name,email,role,active,created_at FROM users WHERE farm_id=%s AND role='worker' ORDER BY created_at DESC,id DESC",
        (farm_id,),
    )
    return render_template("workers/index.html", active="workers", workers=workers)


@bp.route("/<int:worker_id>/edit", methods=["GET", "POST"])
@roles_required("owner", "manager")
def edit(worker_id):
    farm_id = get_current_user()["farm_id"]
    worker = _farm_worker(worker_id, farm_id)
    if not worker:
        return ("Not found", 404)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        active = request.form.get("active") == "true"
        if not name or not email or "@" not in email:
            flash("Enter a valid name and email address.", "error")
        elif fetch_one("SELECT id FROM users WHERE LOWER(email)=LOWER(%s) AND id<>%s", (email, worker_id)):
            flash("That email address is already registered.", "error")
        elif password and len(password) < 10:
            flash("A new password must contain at least 10 characters.", "error")
        else:
            if password:
                execute(
                    """UPDATE users SET name=%s,email=%s,password_hash=%s,active=%s,updated_at=CURRENT_TIMESTAMP
                       WHERE id=%s AND farm_id=%s AND role='worker'""",
                    (name, email, generate_password_hash(password), active, worker_id, farm_id),
                )
            else:
                execute(
                    """UPDATE users SET name=%s,email=%s,active=%s,updated_at=CURRENT_TIMESTAMP
                       WHERE id=%s AND farm_id=%s AND role='worker'""",
                    (name, email, active, worker_id, farm_id),
                )
            flash("Worker account updated.", "success")
            return redirect(url_for("workers.index"))
    return render_template("workers/edit.html", active="workers", worker=worker)


@bp.post("/<int:worker_id>/delete")
@roles_required("owner", "manager")
def delete(worker_id):
    farm_id = get_current_user()["farm_id"]
    worker = _farm_worker(worker_id, farm_id)
    if not worker:
        return ("Not found", 404)
    execute("DELETE FROM users WHERE id=%s AND farm_id=%s AND role='worker'", (worker_id, farm_id))
    flash("Worker account deleted.", "success")
    return redirect(url_for("workers.index"))
