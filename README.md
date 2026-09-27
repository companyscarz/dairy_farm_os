# FarmOS — Dairy Farm Management PWA

A production-oriented, mobile-first dairy farm management system built with **Flask + Jinja2 + PostgreSQL + vanilla HTML/CSS/JavaScript + Apache ECharts**.

## Architecture

- Flask application factory
- PostgreSQL via `psycopg` / `psycopg_pool`
- Plain SQL migrations in `app/database/migrations/`
- No SQLAlchemy
- No Flask-WTF
- No NiceGUI
- Native HTML forms and server-rendered Jinja templates
- Apache ECharts receives JSON data directly from Flask templates
- First-run administrator creation; no seed script and no default password
- Responsive PWA shell with service worker and manifest
- Gunicorn production server
- Docker Compose PostgreSQL deployment

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
8. You will be redirected to `/setup` if no owner exists.
9. Create the first administrator and farm.
10. Configure the farm in Settings.

## Docker

Create `.env` with at least:

```env
POSTGRES_DB=farmos
POSTGRES_USER=farmos
POSTGRES_PASSWORD=use-a-long-random-password
SECRET_KEY=use-a-long-random-application-secret
APP_PORT=8080
SESSION_COOKIE_SECURE=false
```

Then:

```bash
docker compose up --build -d
```

For HTTPS behind NGINX, set `SESSION_COOKIE_SECURE=true`.

## Database

The application uses explicit SQL. The database is initialized automatically when Flask starts.

Initial schema:

`app/database/migrations/001_initial.sql`

Future schema changes should be added as new numbered migration files, for example:

`002_add_animal_health.sql`

The application records applied migration names in `schema_migrations`.

## Production deployment

Put NGINX or another TLS reverse proxy in front of Gunicorn. Do not expose PostgreSQL publicly. Use a unique database password and application secret. Set `DEBUG=false` and `SESSION_COOKIE_SECURE=true` when HTTPS is active.

## Testing

```bash
pytest -q
```

The test suite includes application-level checks that do not require SQLAlchemy or NiceGUI.
# dairy_farm_os
