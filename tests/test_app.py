import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-1234567890")
os.environ.setdefault("DATABASE_URL", "postgresql://invalid:invalid@localhost:59999/invalid")
os.environ.setdefault("DEBUG", "true")


def test_config_requires_postgresql():
    from app.config import settings
    assert settings.database_url.startswith("postgresql")


def test_security_token_roundtrip(monkeypatch):
    from flask import Flask, session
    from app.security import csrf_token
    app = Flask(__name__)
    app.secret_key = "test-secret"
    with app.test_request_context("/"):
        first = csrf_token()
        second = csrf_token()
        assert first == second
        assert session["csrf_token"] == first
