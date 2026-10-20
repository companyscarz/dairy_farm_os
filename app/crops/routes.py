from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, roles_required, get_current_user, module_required
from ..database import fetch_all, fetch_one, execute

bp = Blueprint("crops", __name__, url_prefix="/crops")


@bp.get("/")
@login_required
@module_required("crops")
def index():
    farm_id=get_current_user()["farm_id"]
    fields=fetch_all("SELECT * FROM fields WHERE farm_id=%s ORDER BY name", (farm_id,))
    seasons=fetch_all("""
        SELECT cs.*, f.name AS field_name FROM crop_seasons cs
        JOIN fields f ON f.id=cs.field_id AND f.farm_id=cs.farm_id
        WHERE cs.farm_id=%s ORDER BY cs.planting_date DESC NULLS LAST, cs.id DESC
    """, (farm_id,))
    return render_template("crops/index.html", active="crops", fields=fields, seasons=seasons)


@bp.route("/fields/new", methods=["GET","POST"])
@roles_required("owner","manager")
@module_required("crops")
def create_field():
    farm_id=get_current_user()["farm_id"]
    if request.method=="POST":
        try:
            area=float(request.form.get("area","0"))
            if not request.form.get("name","").strip() or area<=0: raise ValueError
            execute("INSERT INTO fields(farm_id,name,area,area_unit,location,notes) VALUES(%s,%s,%s,%s,%s,%s)", (farm_id,request.form["name"].strip(),area,request.form.get("area_unit","acres"),request.form.get("location") or None,request.form.get("notes") or None))
            flash("Field added.","success"); return redirect(url_for("crops.index"))
        except Exception: flash("Could not add the field. Its name may already exist.","error")
    return render_template("crops/field_form.html",active="crops")


@bp.route("/seasons/new", methods=["GET","POST"])
@roles_required("owner","manager","worker")
@module_required("crops")
def create_season():
    farm_id=get_current_user()["farm_id"]
    fields=fetch_all("SELECT id,name FROM fields WHERE farm_id=%s ORDER BY name",(farm_id,))
    if request.method=="POST":
        try:
            field_id=int(request.form["field_id"])
            exists=fetch_one("SELECT id FROM fields WHERE id=%s AND farm_id=%s",(field_id,farm_id))
            if not exists or not request.form.get("crop_name","").strip(): raise ValueError
            execute("""INSERT INTO crop_seasons(farm_id,field_id,crop_name,variety,season_name,planting_date,expected_harvest_date,status,notes) VALUES(%s,%s,%s,%s,%s,NULLIF(%s,'')::date,NULLIF(%s,'')::date,%s,%s)""",(farm_id,field_id,request.form["crop_name"].strip(),request.form.get("variety") or None,request.form.get("season_name") or None,request.form.get("planting_date",""),request.form.get("expected_harvest_date",""),request.form.get("status","planned"),request.form.get("notes") or None))
            flash("Crop season added.","success"); return redirect(url_for("crops.index"))
        except Exception: flash("Could not save the crop season. Check the field and dates.","error")
    return render_template("crops/season_form.html",active="crops",fields=fields)
