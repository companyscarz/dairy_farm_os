import math

from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, roles_required, get_current_user
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
            quantity = float(request.form.get("quantity", ""))
            total = float(request.form.get("total", ""))
            sale_date = request.form.get("sale_date", "").strip()
            category = request.form.get("category", "").strip()
            unit = request.form.get("unit", "").strip()
            if (not sale_date or not category or not unit or
                    not math.isfinite(quantity) or not math.isfinite(total) or
                    quantity <= 0 or total < 0):
                raise ValueError
            execute(
                """INSERT INTO sales(farm_id,sale_date,customer_name,category,quantity,unit,total,notes)
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                (farm_id, sale_date, request.form.get("customer_name", "").strip() or None,
                 category, quantity, unit, total, request.form.get("notes", "").strip() or None),
            )
            flash("Sale recorded.", "success")
            return redirect(url_for("sales.index"))
        except (ValueError, KeyError):
            flash("Enter a date, category, unit, positive quantity, and valid non-negative total.", "error")
        except Exception:
            flash("Could not save the sale. Check the values.", "error")
    return render_template("sales/form.html", active="sales")

@bp.post("/<int:record_id>/delete")
@roles_required("owner", "manager")
def delete(record_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM sales WHERE id=%s AND farm_id=%s", (record_id, farm_id))
    flash("Sale record deleted.", "success")
    return redirect(url_for("sales.index"))

