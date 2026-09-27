from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, get_current_user
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
            litres = float(request.form.get("litres", "0"))
            if litres < 0: raise ValueError
            execute("""INSERT INTO milk_production(farm_id,production_date,session,litres,notes)
                VALUES(%s,%s,%s,%s,%s)""", (farm_id, request.form["production_date"], request.form["session"], litres, request.form.get("notes") or None))
            flash("Milk production recorded.", "success")
            return redirect(url_for("milk.index"))
        except Exception:
            flash("Could not save the milk record. Check the date, session and litres.", "error")
    return render_template("milk/form.html", active="production")
