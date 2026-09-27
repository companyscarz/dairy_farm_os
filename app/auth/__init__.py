from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash

from ..database import fetch_one, execute_returning


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = fetch_one("""
        SELECT u.*, f.name AS farm_name, f.currency, f.timezone
        FROM users u JOIN farms f ON f.id = u.farm_id
        WHERE u.id = %s AND u.active = TRUE
    """, (user_id,))
    if not user:
        session.clear()
    return user


def login_user(user):
    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["farm_id"] = user["farm_id"]
    session["role"] = user["role"]


def logout_user():
    session.clear()


def authenticate(email, password):
    user = fetch_one("SELECT * FROM users WHERE LOWER(email) = LOWER(%s) LIMIT 1", (email.strip(),))
    if not user or not user["active"]:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def first_admin_exists():
    row = fetch_one("SELECT EXISTS(SELECT 1 FROM users WHERE role = 'owner') AS exists")
    return bool(row["exists"])


def create_initial_admin(farm_name, location, name, email, password, phone="", farm_email=""):
    if first_admin_exists():
        raise ValueError("Initial administrator already exists.")
    password_hash = generate_password_hash(password)
    from ..database import get_db
    with get_db() as db:
        farm = db.execute("""
            INSERT INTO farms(name, location, phone, email)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (farm_name, location or None, phone or None, farm_email or None)).fetchone()
        user = db.execute("""
            INSERT INTO users(farm_id, name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, 'owner')
            RETURNING id, farm_id, name, email, role
        """, (farm["id"], name, email.strip().lower(), password_hash)).fetchone()
        db.commit()
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for("auth.login"))
            if user["role"] not in roles:
                flash("You do not have permission to perform that action.", "error")
                return redirect(url_for("dashboard.dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator
