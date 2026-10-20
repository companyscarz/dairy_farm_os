from datetime import date, timedelta
from flask import Blueprint, render_template
from ..auth import login_required, get_current_user, get_farm_modules
from ..database import fetch_one, fetch_all
bp = Blueprint("dashboard", __name__)

@bp.get("/")
@login_required
def dashboard():
    user=get_current_user(); farm_id=user["farm_id"]; modules=get_farm_modules(farm_id); today=date.today(); month_start=today.replace(day=1); start=today-timedelta(days=13)
    revenue=fetch_one("SELECT COALESCE(SUM(total),0) v FROM sales WHERE farm_id=%s AND sale_date>=%s",(farm_id,month_start))["v"]
    expenses=fetch_one("SELECT COALESCE(SUM(amount),0) v FROM expenses WHERE farm_id=%s AND expense_date>=%s",(farm_id,month_start))["v"]
    low_stock=fetch_one("SELECT COUNT(*) n FROM inventory_items WHERE farm_id=%s AND quantity<=reorder_level",(farm_id,))["n"]
    data={"revenue":float(revenue),"expenses":float(expenses),"profit":float(revenue-expenses),"low_stock":low_stock,"farm_type":user["farm_type"],"modules":modules,"animals":0,"milk_today":0.0,"milk_chart":{"labels":[],"values":[]},"fields":0,"active_crops":0,"recent_sales":fetch_all("SELECT id,sale_date,customer_name,category,total FROM sales WHERE farm_id=%s ORDER BY sale_date DESC,id DESC LIMIT 5",(farm_id,)),"recent_expenses":fetch_all("SELECT id,expense_date,category,description,amount FROM expenses WHERE farm_id=%s ORDER BY expense_date DESC,id DESC LIMIT 5",(farm_id,))}
    if "dairy" in modules:
        data["animals"]=fetch_one("SELECT COUNT(*) n FROM animals WHERE farm_id=%s AND status='active'",(farm_id,))["n"]
        data["milk_today"]=float(fetch_one("SELECT COALESCE(SUM(litres),0) v FROM milk_production WHERE farm_id=%s AND production_date=%s",(farm_id,today))["v"])
        rows=fetch_all("SELECT production_date,COALESCE(SUM(litres),0) litres FROM milk_production WHERE farm_id=%s AND production_date BETWEEN %s AND %s GROUP BY production_date ORDER BY production_date",(farm_id,start,today))
        data["milk_chart"]={"labels":[r["production_date"].strftime("%d %b") for r in rows],"values":[float(r["litres"]) for r in rows]}
    if "crops" in modules:
        data["fields"]=fetch_one("SELECT COUNT(*) n FROM fields WHERE farm_id=%s",(farm_id,))["n"]
        data["active_crops"]=fetch_one("SELECT COUNT(*) n FROM crop_seasons WHERE farm_id=%s AND status IN ('planned','growing')",(farm_id,))["n"]
    return render_template("dashboard/index.html",active="dashboard",data=data)
