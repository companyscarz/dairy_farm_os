from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, fetch_one, execute, execute_returning

bp = Blueprint("animals", __name__, url_prefix="/animals")

@bp.get("/")
@login_required
def index():
    farm_id = get_current_user()["farm_id"]
    animals = fetch_all("SELECT * FROM animals WHERE farm_id=%s ORDER BY tag", (farm_id,))
    return render_template("animals/index.html", active="animals", animals=animals)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        tag = request.form.get("tag", "").strip()
        if not tag:
            flash("Animal tag is required.", "error")
        else:
            try:
                execute("""INSERT INTO animals(farm_id,tag,name,breed,sex,date_of_birth,status,last_calving,notes)
                    VALUES(%s,%s,%s,%s,%s,NULLIF(%s,'')::date,%s,NULLIF(%s,'')::date,%s)""",
                    (farm_id, tag, request.form.get("name") or None, request.form.get("breed") or None,
                     request.form.get("sex", "female"), request.form.get("date_of_birth", ""),
                     request.form.get("status", "active"), request.form.get("last_calving", ""), request.form.get("notes") or None))
                flash("Animal added.", "success")
                return redirect(url_for("animals.index"))
            except Exception:
                flash("Could not add animal. The tag may already exist.", "error")
    return render_template("animals/form.html", active="animals", animal=None)

@bp.route("/<int:animal_id>/edit", methods=["GET", "POST"])
@login_required
def edit(animal_id):
    farm_id = get_current_user()["farm_id"]
    animal = fetch_one("SELECT * FROM animals WHERE id=%s AND farm_id=%s", (animal_id, farm_id))
    if not animal:
        return ("Not found", 404)
    if request.method == "POST":
        execute("""UPDATE animals SET tag=%s,name=%s,breed=%s,sex=%s,date_of_birth=NULLIF(%s,'')::date,
            status=%s,last_calving=NULLIF(%s,'')::date,notes=%s,updated_at=CURRENT_TIMESTAMP
            WHERE id=%s AND farm_id=%s""",
            (request.form.get("tag", "").strip(), request.form.get("name") or None, request.form.get("breed") or None,
             request.form.get("sex", "female"), request.form.get("date_of_birth", ""), request.form.get("status", "active"),
             request.form.get("last_calving", ""), request.form.get("notes") or None, animal_id, farm_id))
        flash("Animal updated.", "success")
        return redirect(url_for("animals.index"))
    return render_template("animals/form.html", active="animals", animal=animal)

@bp.post("/<int:animal_id>/delete")
@roles_required("owner", "manager")
def delete(animal_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM animals WHERE id=%s AND farm_id=%s", (animal_id, farm_id))
    flash("Animal deleted.", "success")
    return redirect(url_for("animals.index"))
