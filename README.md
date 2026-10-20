# Intercity Dairy Farm — Farm Management PWA

A production-oriented, mobile-first dairy farm management system built with **Flask + Jinja2 + PostgreSQL + vanilla HTML/CSS/JavaScript + Apache ECharts**, configured for Intercity Dairy Farm.

## Architecture

- Flask application factory
- PostgreSQL via `psycopg` / `psycopg_pool`
- Plain SQL migrations in `app/database/migrations/`
- Native HTML forms and server-rendered Jinja templates
- Responsive PWA shell with service worker and manifest
- Gunicorn production server

## First run

1. Copy `.env.example` to `.env` if your environment provides that example; otherwise set the variables directly in your environment.
2. Set a strong `SECRET_KEY`.
3. Set `APP_NAME=Intercity Dairy Farm` and a PostgreSQL `DATABASE_URL`.
4. Install dependencies with `python -m pip install -r requirements.txt`.
5. Start with `python run.py`.
6. Open `http://127.0.0.1:7070` and create the first administrator and farm.

The app initializes its PostgreSQL schema automatically and redirects to `/setup` until an owner account exists. There is no default password.

## Production deployment

Use HTTPS behind a TLS reverse proxy, set `SESSION_COOKIE_SECURE=true`, configure a unique `SECRET_KEY`, and do not expose PostgreSQL publicly. Configure Dokploy's exposed container port to match the start command (7070 for the supplied Nixpacks command).

## Testing

```bash
pytest -q
```
