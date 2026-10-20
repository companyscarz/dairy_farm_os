import math

from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, execute

bp = Blueprint("milk", __name__, url_prefix="/production")


@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    records = fetch_all("SELECT * FROM milk_production WHERE farm_id=%s ORDER BY production_date DESC, id DESC", (farm_id,))
    return render_template("milk/index.html", active="production", records=records)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            litres = float(request.form.get("litres", ""))
            production_date = request.form.get("production_date", "").strip()
            session_name = request.form.get("session", "").strip()
            if not production_date or not session_name or not math.isfinite(litres) or litres < 0:
                raise ValueError
            execute(
                """INSERT INTO milk_production(farm_id,production_date,session,litres,notes)
                   VALUES(%s,%s,%s,%s,%s)""",
                (farm_id, production_date, session_name, litres,
                 request.form.get("notes", "").strip() or None),
            )
            flash("Milk production recorded.", "success")
            return redirect(url_for("milk.index"))
        except (ValueError, KeyError):
            flash("Enter a date, session, and valid non-negative litres.", "error")
        except Exception:
            flash("Could not save the milk record. Check the date, session and litres.", "error")
    return render_template("milk/form.html", active="production")

@bp.post("/<int:record_id>/delete")
@roles_required("owner", "manager")
def delete(record_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM milk_production WHERE id=%s AND farm_id=%s", (record_id, farm_id))
    flash("Milk production record deleted.", "success")
    return redirect(url_for("milk.index"))

