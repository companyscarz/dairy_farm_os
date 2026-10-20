from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..auth import login_required, roles_required, get_current_user, get_user_farms, switch_farm, get_farm_modules
from ..database import fetch_one, fetch_all, execute, get_db

bp = Blueprint("settings", __name__, url_prefix="/settings")

FARM_TYPES = {
    "dairy": "Dairy",
    "crop": "Crop",
    "poultry": "Poultry",
    "pig": "Pig",
    "fish": "Fish / Aquaculture",
    "mixed": "Mixed farm",
    "other": "Other",
}
MODULES_BY_TYPE = {
    "dairy": {"dairy"}, "crop": {"crops"}, "poultry": {"poultry"},
    "pig": {"pigs"}, "fish": {"aquaculture"},
    "mixed": {"dairy", "crops", "poultry", "pigs", "aquaculture"}, "other": set(),
}


def _sync_modules(db, farm_id, farm_type):
    desired = MODULES_BY_TYPE.get(farm_type, set()) | {"core"}
    db.execute("UPDATE farm_modules SET enabled=FALSE WHERE farm_id=%s", (farm_id,))
    for module in desired:
        db.execute("""
            INSERT INTO farm_modules(farm_id,module_key,enabled) VALUES(%s,%s,TRUE)
            ON CONFLICT (farm_id,module_key) DO UPDATE SET enabled=TRUE
        """, (farm_id, module))


@bp.route("/", methods=["GET", "POST"])
@roles_required("owner", "manager")
def settings_page():
    user = get_current_user()
    farm = fetch_one("SELECT * FROM farms WHERE id=%s", (user["farm_id"],))
    if request.method == "POST":
        farm_type = request.form.get("farm_type", "other")
        if farm_type not in FARM_TYPES:
            farm_type = "other"
        with get_db() as db:
            db.execute("""UPDATE farms SET name=%s,location=%s,phone=%s,email=%s,currency=%s,timezone=%s,farm_type=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s""", (
                request.form["name"].strip(), request.form.get("location") or None, request.form.get("phone") or None,
                request.form.get("email") or None, request.form.get("currency", "UGX"), request.form.get("timezone", "Africa/Kampala"), farm_type, user["farm_id"]))
            _sync_modules(db, user["farm_id"], farm_type)
            db.commit()
        flash("Farm settings updated.", "success")
        return redirect(url_for("settings.settings_page"))
    return render_template("settings/index.html", active="settings", farm=farm, farm_types=FARM_TYPES)


@bp.route("/users")
@roles_required("owner")
def users():
    user = get_current_user()
    members = fetch_all("""
        SELECT u.id,u.name,u.email,uf.active,uf.role,uf.is_default
        FROM user_farms uf JOIN users u ON u.id=uf.user_id
        WHERE uf.farm_id=%s ORDER BY u.name
    """, (user["farm_id"],))
    return render_template("settings/users.html", active="settings", members=members)


@bp.route("/users/new", methods=["GET", "POST"])
@roles_required("owner")
def create_user():
    user = get_current_user()
    if request.method == "POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower(); role=request.form.get("role","worker"); password=request.form.get("password","")
        if role not in {"owner","manager","worker"}: role="worker"
        if not name or not email or len(password)<10:
            flash("Name, email and a password of at least 10 characters are required.", "error")
        else:
            try:
                with get_db() as db:
                    existing=db.execute("SELECT id,active FROM users WHERE LOWER(email)=LOWER(%s)", (email,)).fetchone()
                    if existing and not existing["active"]:
                        raise ValueError("This user account is inactive.")
                    if existing:
                        db.execute("""
                            INSERT INTO user_farms(user_id,farm_id,role,is_default,active) VALUES(%s,%s,%s,FALSE,TRUE)
                            ON CONFLICT (user_id,farm_id) DO UPDATE SET role=EXCLUDED.role, active=TRUE
                        """, (existing["id"],user["farm_id"],role))
                    else:
                        new_user=db.execute("""
                            INSERT INTO users(farm_id,name,email,password_hash,role) VALUES(%s,%s,%s,%s,%s) RETURNING id
                        """, (user["farm_id"],name,email,generate_password_hash(password),role)).fetchone()
                        db.execute("INSERT INTO user_farms(user_id,farm_id,role,is_default,active) VALUES(%s,%s,%s,FALSE,TRUE)", (new_user["id"],user["farm_id"],role))
                    db.commit()
                flash("User added to this farm.", "success")
                return redirect(url_for("settings.users"))
            except ValueError as exc: flash(str(exc), "error")
            except Exception: flash("Could not add the user. The email may already be in use in an incompatible way.", "error")
    return render_template("settings/user_form.html", active="settings")


@bp.post("/users/<int:user_id>/role")
@roles_required("owner")
def update_role(user_id):
    current=get_current_user(); role=request.form.get("role","worker")
    if role not in {"owner","manager","worker"}: role="worker"
    if user_id == current["id"] and role != "owner":
        flash("You cannot remove your own owner role.", "error")
    else:
        execute("UPDATE user_farms SET role=%s WHERE user_id=%s AND farm_id=%s", (role,user_id,current["farm_id"]))
        flash("User role updated.", "success")
    return redirect(url_for("settings.users"))


@bp.post("/users/<int:user_id>/toggle")
@roles_required("owner")
def toggle_user(user_id):
    current=get_current_user()
    if user_id == current["id"]:
        flash("You cannot deactivate your own farm membership.", "error")
    else:
        row=fetch_one("SELECT active FROM user_farms WHERE user_id=%s AND farm_id=%s", (user_id,current["farm_id"]))
        if row:
            execute("UPDATE user_farms SET active=NOT active WHERE user_id=%s AND farm_id=%s", (user_id,current["farm_id"]))
            flash("User status updated for this farm.", "success")
    return redirect(url_for("settings.users"))


@bp.route("/farms")
@roles_required("owner")
def farms():
    return render_template("settings/farms.html", active="settings", farms=get_user_farms(), farm_types=FARM_TYPES)


@bp.route("/farms/new", methods=["GET", "POST"])
@roles_required("owner")
def create_farm():
    user=get_current_user()
    if request.method=="POST":
        name=request.form.get("name","").strip(); farm_type=request.form.get("farm_type","other")
        if farm_type not in FARM_TYPES: farm_type="other"
        if not name: flash("Farm name is required.","error")
        else:
            try:
                with get_db() as db:
                    farm=db.execute("""INSERT INTO farms(name,location,phone,email,currency,timezone,farm_type) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id""", (
                        name,request.form.get("location") or None,request.form.get("phone") or None,request.form.get("email") or None,request.form.get("currency","UGX"),request.form.get("timezone","Africa/Kampala"),farm_type)).fetchone()
                    db.execute("INSERT INTO user_farms(user_id,farm_id,role,is_default) VALUES(%s,%s,'owner',FALSE)", (user["id"],farm["id"]))
                    _sync_modules(db,farm["id"],farm_type)
                    db.commit()
                flash("New farm created.","success")
                return redirect(url_for("settings.farms"))
            except Exception: flash("Could not create the farm.","error")
    return render_template("settings/farm_form.html", active="settings", farm=None, farm_types=FARM_TYPES)


@bp.post("/switch-farm/<int:farm_id>")
@login_required
def switch(farm_id):
    if switch_farm(farm_id): flash("Farm switched.","success")
    else: flash("You do not have access to that farm.","error")
    return redirect(request.referrer or url_for("dashboard.dashboard"))


@bp.route("/password", methods=["POST"])
@login_required
def password():
    user=get_current_user(); old=request.form.get("current_password",""); new=request.form.get("new_password","")
    row=fetch_one("SELECT password_hash FROM users WHERE id=%s",(user["id"],))
    if not row or not check_password_hash(row["password_hash"],old): flash("Current password is incorrect.","error")
    elif len(new)<10: flash("New password must be at least 10 characters.","error")
    else:
        execute("UPDATE users SET password_hash=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s",(generate_password_hash(new),user["id"]))
        flash("Password changed.","success")
    return redirect(url_for("settings.settings_page"))
