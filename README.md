# FarmOS — The operating system for your farm

FarmOS is a mobile-first farm management PWA built for different kinds of farmers instead of assuming every farm is dairy.

## Stack

- Flask + Jinja2
- PostgreSQL only
- psycopg / psycopg_pool
- Vanilla HTML/CSS/JavaScript
- Apache ECharts
- Explicit SQL migrations
- Flask sessions + custom CSRF protection
- Gunicorn + Docker Compose
- PWA manifest + service worker

No SQLAlchemy, Flask-WTF, NiceGUI, SQLite fallback, or seed script.

## Farm model

A FarmOS account can belong to multiple farms. Each farm has its own:

- farm type: dairy, crop, poultry, pig, fish/aquaculture, mixed, or other
- users and per-farm roles
- enabled operational modules
- farm-scoped records and reports

Core modules are shared across farm types: dashboard, inventory, sales, expenses, reports and settings.

Specialized modules currently include the dairy workspace and an initial crop workspace. The architecture is ready for poultry, pigs and aquaculture modules to be added without changing the core data model.

## First run

1. Copy `.env.example` to `.env`.
2. Set a strong `SECRET_KEY`.
3. Set `DATABASE_URL` to PostgreSQL.
4. Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

5. Make sure PostgreSQL is running.
6. Start:

```powershell
python run.py
```

7. Open `http://127.0.0.1:8080`.
8. FarmOS opens `/setup` only when no owner exists.
9. Create the first farm and administrator, including the farm type.

## Multi-farm workflow

Owners can use **Settings → My farms** to create additional farms. A user can belong to more than one farm and can have a different role on each farm.

Owners can use **Settings → Farm users** to add accounts, assign roles, and activate/deactivate a membership for the current farm.

## Database migrations

Migrations live in `app/database/migrations/` and are applied automatically at startup. Migration execution uses a PostgreSQL advisory lock so multiple Gunicorn workers do not race while changing the schema.

Current migrations:

- `001_initial.sql` — core farm management schema
- `002_farm_types_multi_user.sql` — farm types, farm modules, multi-farm memberships, crop foundation

## Production

Put NGINX or another TLS reverse proxy in front of Gunicorn. Do not expose PostgreSQL publicly. Use a unique database password and application secret. Set `DEBUG=false` and `SESSION_COOKIE_SECURE=true` when HTTPS is active.

## Testing

```bash
python -m compileall -q app run.py wsgi.py
pytest -q
```

The repository does not contain a seed script or default credentials.
