import secrets
from flask import session, request, abort


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def validate_csrf():
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return
    expected = session.get("csrf_token")
    supplied = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if not expected or not supplied or not secrets.compare_digest(expected, supplied):
        abort(400, description="Invalid CSRF token")
