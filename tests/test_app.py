import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-1234567890")
os.environ.setdefault("DATABASE_URL", "postgresql://invalid:invalid@localhost:59999/invalid")
os.environ.setdefault("DEBUG", "true")


def test_config_requires_postgresql():
    from app.config import settings
    assert settings.database_url.startswith("postgresql")


def test_security_token_roundtrip():
    from flask import Flask, session
    from app.security import csrf_token

    app = Flask(__name__)
    app.secret_key = "test-secret"
    with app.test_request_context("/"):
        first = csrf_token()
        second = csrf_token()
        assert first == second
        assert session["csrf_token"] == first


def test_login_redirect_accepts_local_path():
    from app.auth.routes import _safe_next_url

    assert _safe_next_url("/reports/?range=month") == "/reports/?range=month"


def test_login_redirect_rejects_external_and_protocol_relative_urls():
    from flask import Flask
    from app.auth.routes import _safe_next_url

    app = Flask(__name__)
    app.add_url_rule("/", endpoint="dashboard.dashboard", view_func=lambda: "")
    with app.test_request_context("/login"):
        assert _safe_next_url("https://evil.example") == "/"
        assert _safe_next_url("//evil.example/path") == "/"
        assert _safe_next_url("/\\\\evil.example") == "/"


def test_csv_export_sanitizes_spreadsheet_formulas():
    from app.reports.routes import _safe_csv_cell

    assert _safe_csv_cell("=HYPERLINK(\"https://example.com\")").startswith("'=")
    assert _safe_csv_cell("@SUM(A1:A2)") == "'@SUM(A1:A2)"
    assert _safe_csv_cell("Normal farm record") == "Normal farm record"
    assert _safe_csv_cell(-12.5) == -12.5
