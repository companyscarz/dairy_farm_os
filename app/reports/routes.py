import csv
import io
from datetime import date, timedelta

from flask import Blueprint, Response, abort, render_template
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, fetch_one

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    today = date.today()
    start = today - timedelta(days=29)
    revenue = fetch_one(
        "SELECT COALESCE(SUM(total),0) v FROM sales WHERE farm_id=%s AND sale_date BETWEEN %s AND %s",
        (farm_id, start, today),
    )["v"]
    expenses = fetch_one(
        "SELECT COALESCE(SUM(amount),0) v FROM expenses WHERE farm_id=%s AND expense_date BETWEEN %s AND %s",
        (farm_id, start, today),
    )["v"]
    rows = fetch_all(
        """SELECT production_date,COALESCE(SUM(litres),0) litres
           FROM milk_production WHERE farm_id=%s AND production_date BETWEEN %s AND %s
           GROUP BY production_date ORDER BY production_date""",
        (farm_id, start, today),
    )
    return render_template(
        "reports/index.html",
        active="reports",
        data={
            "revenue": float(revenue),
            "expenses": float(expenses),
            "profit": float(revenue - expenses),
            "chart": {
                "labels": [r["production_date"].strftime("%d %b") for r in rows],
                "values": [float(r["litres"]) for r in rows],
            },
        },
    )


# Only farm owners (the administrator role) can download backups.
# Each query is explicitly scoped to the signed-in owner's farm.
EXPORTS = {
    "animals": {
        "filename": "animals.csv",
        "headers": ["ID", "Tag", "Name", "Breed", "Sex", "Date of birth", "Status", "Last calving", "Notes", "Image URL", "Created at"],
        "sql": """SELECT id,tag,name,breed,sex,date_of_birth,status,last_calving,notes,image_url,created_at
                  FROM animals WHERE farm_id=%s ORDER BY tag""",
    },
    "milk": {
        "filename": "milk-production.csv",
        "headers": ["ID", "Production date", "Session", "Litres", "Notes", "Created at"],
        "sql": """SELECT id,production_date,session,litres,notes,created_at
                  FROM milk_production WHERE farm_id=%s ORDER BY production_date,id""",
    },
    "inventory": {
        "filename": "inventory.csv",
        "headers": ["ID", "Name", "Category", "Quantity", "Unit", "Reorder level", "Created at", "Updated at"],
        "sql": """SELECT id,name,category,quantity,unit,reorder_level,created_at,updated_at
                  FROM inventory_items WHERE farm_id=%s ORDER BY name""",
    },
    "sales": {
        "filename": "sales.csv",
        "headers": ["ID", "Sale date", "Customer", "Category", "Quantity", "Unit", "Total", "Notes", "Created at"],
        "sql": """SELECT id,sale_date,customer_name,category,quantity,unit,total,notes,created_at
                  FROM sales WHERE farm_id=%s ORDER BY sale_date,id""",
    },
    "expenses": {
        "filename": "expenses.csv",
        "headers": ["ID", "Expense date", "Category", "Description", "Amount", "Created at"],
        "sql": """SELECT id,expense_date,category,description,amount,created_at
                  FROM expenses WHERE farm_id=%s ORDER BY expense_date,id""",
    },
    "workers": {
        "filename": "farm-users.csv",
        "headers": ["ID", "Name", "Email", "Role", "Active", "Created at", "Updated at"],
        "sql": """SELECT id,name,email,role,active,created_at,updated_at
                  FROM users WHERE farm_id=%s ORDER BY role,name""",
    },
}


def _safe_csv_cell(value):
    # Prevent spreadsheet formula injection in text fields without changing
    # numeric values (including legitimate negative numbers).
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


@bp.get("/export/<dataset>.csv")
@roles_required("owner")
def export_csv(dataset):
    export = EXPORTS.get(dataset)
    if not export:
        abort(404)

    farm_id = get_current_user()["farm_id"]
    records = fetch_all(export["sql"], (farm_id,))
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(export["headers"])
    for record in records:
        writer.writerow([_safe_csv_cell(value) for value in record.values()])

    filename = export["filename"]
    response = Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
