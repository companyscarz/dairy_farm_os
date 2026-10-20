import math

from flask import Blueprint, render_template, request, redirect, url_for, flash
<<<<<<< HEAD
from ..auth import login_required, get_current_user, module_required
from ..database import fetch_all, execute
=======
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, fetch_one, execute
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a

bp = Blueprint("milk", __name__, url_prefix="/production")


@bp.get("/")
@login_required
@module_required("dairy")
def index():
    farm_id = get_current_user()["farm_id"]
    records = fetch_all("SELECT * FROM milk_production WHERE farm_id=%s ORDER BY production_date DESC, id DESC", (farm_id,))
    return render_template("milk/index.html", active="production", records=records)


def _fields():
    litres = float(request.form.get("litres", ""))
    production_date = request.form.get("production_date", "").strip()
    session_name = request.form.get("session", "").strip()
    if not production_date or session_name not in {"morning", "afternoon", "evening"} or not math.isfinite(litres) or litres < 0:
        raise ValueError
    return production_date, session_name, litres, request.form.get("notes", "").strip() or None


@bp.route("/new", methods=["GET", "POST"])
@login_required
@module_required("dairy")
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            execute(
                """INSERT INTO milk_production(farm_id,production_date,session,litres,notes)
                   VALUES(%s,%s,%s,%s,%s)""",
                (farm_id, *_fields()),
            )
            flash("Milk production recorded.", "success")
            return redirect(url_for("milk.index"))
        except (ValueError, KeyError):
            flash("Enter a date, valid session, and non-negative litres.", "error")
        except Exception:
            flash("Could not save the milk record. Check the date and ensure this session has not already been recorded.", "error")
    return render_template("milk/form.html", active="production", record=None)


@bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
@roles_required("owner", "manager")
def edit(record_id):
    farm_id = get_current_user()["farm_id"]
    record = fetch_one("SELECT * FROM milk_production WHERE id=%s AND farm_id=%s", (record_id, farm_id))
    if not record:
        return ("Not found", 404)
    if request.method == "POST":
        try:
            production_date, session_name, litres, notes = _fields()
            execute(
                """UPDATE milk_production SET production_date=%s, session=%s, litres=%s, notes=%s
                   WHERE id=%s AND farm_id=%s""",
                (production_date, session_name, litres, notes, record_id, farm_id),
            )
            flash("Milk production record updated.", "success")
            return redirect(url_for("milk.index"))
        except (ValueError, KeyError):
            flash("Enter a date, valid session, and non-negative litres.", "error")
        except Exception:
            flash("Could not update the record. Check the date and ensure another record does not use the same session.", "error")
    return render_template("milk/form.html", active="production", record=record)


@bp.post("/<int:record_id>/delete")
@roles_required("owner", "manager")
def delete(record_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM milk_production WHERE id=%s AND farm_id=%s", (record_id, farm_id))
    flash("Milk production record deleted.", "success")
    return redirect(url_for("milk.index"))
