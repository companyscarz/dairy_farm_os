from flask import Blueprint, render_template, request, redirect, url_for, flash
<<<<<<< HEAD
from ..auth import login_required, roles_required, get_current_user, module_required
from ..database import fetch_all, fetch_one, execute, execute_returning
=======
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_all, fetch_one, execute
from ..storage import upload_animal_image, StorageError
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a

bp = Blueprint("animals", __name__, url_prefix="/animals")
VALID_SEXES = {"female", "male"}
VALID_STATUSES = {"active", "sold", "deceased", "inactive"}


def _animal_fields():
    tag = request.form.get("tag", "").strip()
    sex = request.form.get("sex", "female")
    status = request.form.get("status", "active")
    if not tag or sex not in VALID_SEXES or status not in VALID_STATUSES:
        raise ValueError("Invalid animal details")
    return (
        tag,
        request.form.get("name", "").strip() or None,
        request.form.get("breed", "").strip() or None,
        sex,
        request.form.get("date_of_birth", "").strip(),
        status,
        request.form.get("last_calving", "").strip(),
        request.form.get("notes", "").strip() or None,
    )


@bp.get("/")
@login_required
@module_required("dairy")
def index():
    farm_id = get_current_user()["farm_id"]
    animals = fetch_all("SELECT * FROM animals WHERE farm_id=%s ORDER BY tag", (farm_id,))
    return render_template("animals/index.html", active="animals", animals=animals)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@module_required("dairy")
def create():
    farm_id = get_current_user()["farm_id"]
    if request.method == "POST":
        try:
            fields = _animal_fields()
            image_url, image_key = upload_animal_image(request.files.get("image"), farm_id)
            execute(
                """INSERT INTO animals(farm_id,tag,name,breed,sex,date_of_birth,status,last_calving,notes,image_url,image_key)
                   VALUES(%s,%s,%s,%s,%s,NULLIF(%s,'')::date,%s,NULLIF(%s,'')::date,%s,%s,%s)""",
                (farm_id, *fields, image_url, image_key),
            )
            flash("Animal added.", "success")
            return redirect(url_for("animals.index"))
        except ValueError:
            flash("Enter an animal tag and choose valid sex and status values.", "error")
        except StorageError as exc:
            flash(str(exc), "error")
        except Exception:
            flash("Could not add animal. Check the dates and ensure the tag is unique.", "error")
    return render_template("animals/form.html", active="animals", animal=None)


@bp.route("/<int:animal_id>/edit", methods=["GET", "POST"])
@login_required
@module_required("dairy")
def edit(animal_id):
    farm_id = get_current_user()["farm_id"]
    animal = fetch_one("SELECT * FROM animals WHERE id=%s AND farm_id=%s", (animal_id, farm_id))
    if not animal:
        return ("Not found", 404)
    if request.method == "POST":
        try:
            fields = _animal_fields()
            image_url, image_key = animal.get("image_url"), animal.get("image_key")
            if request.files.get("image") and request.files["image"].filename:
                image_url, image_key = upload_animal_image(request.files["image"], farm_id)
            execute(
                """UPDATE animals
                   SET tag=%s,name=%s,breed=%s,sex=%s,date_of_birth=NULLIF(%s,'')::date,
                       status=%s,last_calving=NULLIF(%s,'')::date,notes=%s,
                       image_url=%s,image_key=%s,updated_at=CURRENT_TIMESTAMP
                   WHERE id=%s AND farm_id=%s""",
                (*fields, image_url, image_key, animal_id, farm_id),
            )
            flash("Animal updated.", "success")
            return redirect(url_for("animals.index"))
        except ValueError:
            flash("Enter an animal tag and choose valid sex and status values.", "error")
        except StorageError as exc:
            flash(str(exc), "error")
        except Exception:
            flash("Could not update the animal. Check the dates and ensure the tag is unique.", "error")
    return render_template("animals/form.html", active="animals", animal=animal)


@bp.post("/<int:animal_id>/delete")
@roles_required("owner", "manager")
@module_required("dairy")
def delete(animal_id):
    farm_id = get_current_user()["farm_id"]
    execute("DELETE FROM animals WHERE id=%s AND farm_id=%s", (animal_id, farm_id))
    flash("Animal deleted.", "success")
    return redirect(url_for("animals.index"))
