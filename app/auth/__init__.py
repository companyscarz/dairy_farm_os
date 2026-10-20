from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import fetch_one, fetch_all


def get_current_user():
    user_id, farm_id = session.get("user_id"), session.get("farm_id")
    if not user_id or not farm_id:
        return None
    user = fetch_one("""
        SELECT u.id, u.name, u.email, u.active, uf.farm_id, uf.role,
               f.name AS farm_name, f.currency, f.timezone, f.farm_type
        FROM users u JOIN user_farms uf ON uf.user_id=u.id AND uf.farm_id=%s AND uf.active=TRUE
        JOIN farms f ON f.id=uf.farm_id
        WHERE u.id=%s AND u.active=TRUE
    """, (farm_id, user_id))
    if not user:
        session.pop("farm_id", None)
        return None
    return user


def get_user_farms(user_id=None):
    user_id = user_id or session.get("user_id")
    if not user_id:
        return []
    return fetch_all("""
        SELECT f.id, f.name, f.location, f.farm_type, uf.role, uf.is_default
        FROM user_farms uf JOIN farms f ON f.id=uf.farm_id JOIN users u ON u.id=uf.user_id
        WHERE uf.user_id=%s AND uf.active=TRUE AND u.active=TRUE ORDER BY uf.is_default DESC, f.name
    """, (user_id,))


def get_farm_modules(farm_id=None):
    farm_id = farm_id or session.get("farm_id")
    if not farm_id:
        return set()
    return {r["module_key"] for r in fetch_all("SELECT module_key FROM farm_modules WHERE farm_id=%s AND enabled=TRUE", (farm_id,))}


def farm_has_module(module_key):
    return module_key in get_farm_modules()


def login_user(user):
    session.clear(); session.permanent = True
    session["user_id"], session["farm_id"], session["role"] = user["id"], user["farm_id"], user["role"]


def switch_farm(farm_id):
    user_id = session.get("user_id")
    if not user_id:
        return False
    membership = fetch_one("""
        SELECT uf.role FROM user_farms uf JOIN users u ON u.id=uf.user_id
        WHERE uf.user_id=%s AND uf.farm_id=%s AND uf.active=TRUE AND u.active=TRUE
    """, (user_id, farm_id))
    if not membership:
        return False
    session["farm_id"], session["role"] = farm_id, membership["role"]
    return True


def logout_user(): session.clear()


def authenticate(email, password):
    user = fetch_one("SELECT * FROM users WHERE LOWER(email)=LOWER(%s) LIMIT 1", (email.strip(),))
    if not user or not user["active"] or not check_password_hash(user["password_hash"], password):
        return None
    membership = fetch_one("SELECT farm_id, role FROM user_farms WHERE user_id=%s AND active=TRUE ORDER BY is_default DESC, farm_id LIMIT 1", (user["id"],))
    if not membership: return None
    user["farm_id"], user["role"] = membership["farm_id"], membership["role"]
    return user


def first_admin_exists():
    row = fetch_one("SELECT EXISTS(SELECT 1 FROM users WHERE role='owner' OR id IN (SELECT user_id FROM user_farms WHERE role='owner')) AS exists")
    return bool(row["exists"])


def _modules_for_type(farm_type):
    return {"dairy":{"dairy"},"crop":{"crops"},"poultry":{"poultry"},"pig":{"pigs"},"fish":{"aquaculture"},"mixed":{"dairy","crops","poultry","pigs","aquaculture"},"other":set()}.get(farm_type, set())


def create_initial_admin(farm_name, location, name, email, password, phone="", farm_email="", farm_type="dairy"):
    if first_admin_exists(): raise ValueError("Initial administrator already exists.")
    from ..database import get_db
    with get_db() as db:
        farm = db.execute("INSERT INTO farms(name,location,phone,email,farm_type) VALUES(%s,%s,%s,%s,%s) RETURNING id", (farm_name,location or None,phone or None,farm_email or None,farm_type)).fetchone()
        user = db.execute("INSERT INTO users(farm_id,name,email,password_hash,role) VALUES(%s,%s,%s,%s,'owner') RETURNING id,farm_id,name,email,role", (farm["id"],name,email.strip().lower(),generate_password_hash(password))).fetchone()
        db.execute("INSERT INTO user_farms(user_id,farm_id,role,is_default) VALUES(%s,%s,'owner',TRUE)", (user["id"],farm["id"]))
        db.execute("INSERT INTO farm_modules(farm_id,module_key,enabled) VALUES(%s,'core',TRUE)", (farm["id"],))
        for module in _modules_for_type(farm_type): db.execute("INSERT INTO farm_modules(farm_id,module_key,enabled) VALUES(%s,%s,TRUE)", (farm["id"],module))
        db.commit()
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user(): return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user=get_current_user()
            if not user: return redirect(url_for("auth.login"))
            if user["role"] not in roles:
                flash("You do not have permission to perform that action.", "error")
                return redirect(url_for("dashboard.dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def module_required(module_key):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not get_current_user(): return redirect(url_for("auth.login"))
            if not farm_has_module(module_key): abort(404)
            return view(*args, **kwargs)
        return wrapped
    return decorator
