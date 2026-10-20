import math

from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, execute

bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    records = fetch_all("SELECT * FROM expenses WHERE farm_id=%s ORDER BY expense_date DESC, id DESC", (farm_id,))
    return render_template("expenses/index.html", active="expenses", records=records)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", ""))
            expense_date = request.form.get("expense_date", "").strip()
            category = request.form.get("category", "").strip()
            if not expense_date or not category or not math.isfinite(amount) or amount < 0:
                raise ValueError
            execute(
                """INSERT INTO expenses(farm_id,expense_date,category,description,amount)
                   VALUES(%s,%s,%s,%s,%s)""",
                (farm_id, expense_date, category,
                 request.form.get("description", "").strip() or None, amount),
            )
            flash("Expense recorded.", "success")
            return redirect(url_for("expenses.index"))
        except (ValueError, KeyError):
            flash("Enter a date, category, and valid non-negative amount.", "error")
        except Exception:
            flash("Could not save the expense.", "error")
    return render_template("expenses/form.html", active="expenses")

@bp.post("/<int:record_id>/delete")
@roles_required("owner", "manager")
def delete(record_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM expenses WHERE id=%s AND farm_id=%s", (record_id, farm_id))
    flash("Expense record deleted.", "success")
    return redirect(url_for("expenses.index"))

