from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import settings
from .database import initialize_database, init_pool, close_pool
from .security import csrf_token, validate_csrf


def create_app():
    settings.validate()
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=settings.session_cookie_secure,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    )

    init_pool()
    initialize_database()

    app.jinja_env.globals["csrf_token"] = csrf_token
    app.jinja_env.globals["app_name"] = settings.app_name

    @app.before_request
    def _csrf():
        validate_csrf()

    @app.context_processor
    def inject_globals():
        from .auth import get_current_user
        return {"current_user": get_current_user()}

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=()")
        return response

    @app.teardown_appcontext
    def _close(_exc):
        # Pool stays alive for the process; it is closed explicitly on shutdown.
        pass

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("error.html", code=400, message=getattr(error, "description", "Bad request")), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="The page you requested was not found."), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500

    from .auth.routes import bp as auth_bp
    from .dashboard.routes import bp as dashboard_bp
    from .animals.routes import bp as animals_bp
    from .milk.routes import bp as milk_bp
    from .inventory.routes import bp as inventory_bp
    from .sales.routes import bp as sales_bp
    from .expenses.routes import bp as expenses_bp
    from .reports.routes import bp as reports_bp
    from .settings.routes import bp as settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(animals_bp)
    app.register_blueprint(milk_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    @app.get("/healthz")
    def healthz():
        from .database import fetch_one
        try:
            fetch_one("SELECT 1 AS ok")
            return {"status": "ok"}, 200
        except Exception:
            return {"status": "unhealthy"}, 503

    @app.get("/sw.js")
    def service_worker():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")

    @app.get("/manifest.json")
    def manifest():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, "manifest.json", mimetype="application/manifest+json")

    return app
