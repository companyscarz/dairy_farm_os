from datetime import date, timedelta
from flask import Blueprint, render_template
from ..auth import login_required, get_current_user
from ..database import fetch_all, fetch_one

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.get("/")
@login_required
def index():
    farm_id=get_current_user()["farm_id"]; today=date.today(); start=today-timedelta(days=29)
    revenue=fetch_one("SELECT COALESCE(SUM(total),0) v FROM sales WHERE farm_id=%s AND sale_date BETWEEN %s AND %s",(farm_id,start,today))["v"]
    expenses=fetch_one("SELECT COALESCE(SUM(amount),0) v FROM expenses WHERE farm_id=%s AND expense_date BETWEEN %s AND %s",(farm_id,start,today))["v"]
    rows=fetch_all("SELECT production_date,COALESCE(SUM(litres),0) litres FROM milk_production WHERE farm_id=%s AND production_date BETWEEN %s AND %s GROUP BY production_date ORDER BY production_date",(farm_id,start,today))
    return render_template("reports/index.html",active="reports",data={"revenue":float(revenue),"expenses":float(expenses),"profit":float(revenue-expenses),"chart":{"labels":[r["production_date"].strftime("%d %b") for r in rows],"values":[float(r["litres"]) for r in rows]}})
