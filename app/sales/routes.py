from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, get_current_user
from ..database import fetch_all, execute

bp = Blueprint("sales", __name__, url_prefix="/sales")

@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    records = fetch_all("SELECT * FROM sales WHERE farm_id=%s ORDER BY sale_date DESC, id DESC", (farm_id,))
    return render_template("sales/index.html", active="sales", records=records)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            quantity=float(request.form["quantity"]); total=float(request.form["total"])
            if quantity <= 0 or total < 0: raise ValueError
            execute("""INSERT INTO sales(farm_id,sale_date,customer_name,category,quantity,unit,total,notes)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", (farm_id, request.form["sale_date"], request.form.get("customer_name") or None,
                request.form["category"], quantity, request.form["unit"], total, request.form.get("notes") or None))
            flash("Sale recorded.", "success"); return redirect(url_for("sales.index"))
        except Exception: flash("Could not save the sale. Check the values.", "error")
    return render_template("sales/form.html", active="sales")
