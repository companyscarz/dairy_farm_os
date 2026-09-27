from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, get_current_user
from ..database import fetch_all, fetch_one, execute

bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    items = fetch_all("SELECT * FROM inventory_items WHERE farm_id=%s ORDER BY name", (farm_id,))
    return render_template("inventory/index.html", active="inventory", items=items)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            q = float(request.form.get("quantity", "0")); r = float(request.form.get("reorder_level", "0"))
            if q < 0 or r < 0: raise ValueError
            execute("""INSERT INTO inventory_items(farm_id,name,category,quantity,unit,reorder_level)
                VALUES(%s,%s,%s,%s,%s,%s)""", (farm_id, request.form["name"].strip(), request.form["category"], q, request.form["unit"].strip(), r))
            flash("Inventory item added.", "success"); return redirect(url_for("inventory.index"))
        except Exception:
            flash("Could not add the item. It may already exist.", "error")
    return render_template("inventory/form.html", active="inventory", item=None)

@bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit(item_id):
    farm_id = get_current_user()["farm_id"]
    item = fetch_one("SELECT * FROM inventory_items WHERE id=%s AND farm_id=%s", (item_id, farm_id))
    if not item: return ("Not found", 404)
    if request.method == "POST":
        try:
            execute("""UPDATE inventory_items SET name=%s,category=%s,quantity=%s,unit=%s,reorder_level=%s,updated_at=CURRENT_TIMESTAMP
                WHERE id=%s AND farm_id=%s""", (request.form["name"].strip(), request.form["category"], float(request.form["quantity"]), request.form["unit"].strip(), float(request.form["reorder_level"]), item_id, farm_id))
            flash("Inventory item updated.", "success"); return redirect(url_for("inventory.index"))
        except Exception: flash("Could not update the item.", "error")
    return render_template("inventory/form.html", active="inventory", item=item)

@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM inventory_items WHERE id=%s AND farm_id=%s", (item_id, farm_id))
    flash("Inventory item deleted.", "success"); return redirect(url_for("inventory.index"))
