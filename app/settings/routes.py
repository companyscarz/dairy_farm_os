from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from ..auth import login_required, roles_required, get_current_user
from ..database import fetch_one, execute

bp=Blueprint("settings",__name__,url_prefix="/settings")

@bp.route("/",methods=["GET","POST"])
@roles_required("owner","manager")
def settings_page():
    user=get_current_user(); farm=fetch_one("SELECT * FROM farms WHERE id=%s",(user["farm_id"],))
    if request.method=="POST":
        execute("""UPDATE farms SET name=%s,location=%s,phone=%s,email=%s,currency=%s,timezone=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s""",
                (request.form["name"].strip(),request.form.get("location") or None,request.form.get("phone") or None,request.form.get("email") or None,request.form.get("currency","UGX"),request.form.get("timezone","Africa/Kampala"),user["farm_id"]))
        flash("Farm settings updated.","success"); return redirect(url_for("settings.settings_page"))
    return render_template("settings/index.html",active="settings",farm=farm)

@bp.route("/password",methods=["POST"])
@login_required
def password():
    user=get_current_user(); old=request.form.get("current_password",""); new=request.form.get("new_password","")
    from werkzeug.security import check_password_hash
    row=fetch_one("SELECT password_hash FROM users WHERE id=%s",(user["id"],))
    if not check_password_hash(row["password_hash"],old): flash("Current password is incorrect.","error")
    elif len(new)<10: flash("New password must be at least 10 characters.","error")
    else:
        execute("UPDATE users SET password_hash=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s",(generate_password_hash(new),user["id"]))
        flash("Password changed.","success")
    return redirect(url_for("settings.settings_page"))
