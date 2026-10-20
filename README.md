<<<<<<< HEAD
# FarmOS — The operating system for your farm

FarmOS is a mobile-first farm management PWA built for different kinds of farmers instead of assuming every farm is dairy.
=======
# Intercity Dairy Farm — Farm Management PWA

A production-oriented, mobile-first dairy farm management system built with **Flask + Jinja2 + PostgreSQL + vanilla HTML/CSS/JavaScript + Apache ECharts**, configured for Intercity Dairy Farm.
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a

## Stack

<<<<<<< HEAD
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
=======
- Flask application factory
- PostgreSQL via `psycopg` / `psycopg_pool`
- Plain SQL migrations in `app/database/migrations/`
- Native HTML forms and server-rendered Jinja templates
- Responsive PWA shell with service worker and manifest
- Gunicorn production server
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a

## First run

1. Copy `.env.example` to `.env` if your environment provides that example; otherwise set the variables directly in your environment.
2. Set a strong `SECRET_KEY`.
3. Set `APP_NAME=Intercity Dairy Farm` and a PostgreSQL `DATABASE_URL`.
4. Install dependencies with `python -m pip install -r requirements.txt`.
5. Start with `python run.py`.
6. Open `http://127.0.0.1:7070` and create the first administrator and farm.

<<<<<<< HEAD
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
=======
The app initializes its PostgreSQL schema automatically and redirects to `/setup` until an owner account exists. There is no default password.

## Production deployment
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a

Use HTTPS behind a TLS reverse proxy, set `SESSION_COOKIE_SECURE=true`, configure a unique `SECRET_KEY`, and do not expose PostgreSQL publicly. Configure Dokploy's exposed container port to match the start command (7070 for the supplied Nixpacks command).

## Cow photo storage (Neon Object Storage)

Cow photos are validated and converted to optimized JPEG images, then uploaded to the configured S3-compatible object-storage bucket. PostgreSQL stores only the image URL and object key. Configure these environment variables in Dokploy before enabling uploads:

- `AWS_ENDPOINT_URL_S3`: the Neon Object Storage S3-compatible endpoint
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: storage credentials
- `AWS_REGION`: region required by your Neon storage setup (default is `auto`)
- `STORAGE_BUCKET`: bucket name
- `STORAGE_PUBLIC_BASE_URL`: public URL root that serves the bucket; the app appends the bucket name and object key

The bucket must allow public reads for these image URLs, or be served through a configured public/CDN base URL. Do not commit credentials to GitHub. Image uploads accept JPG, PNG and WEBP up to 5 MB; stored images are normalized to JPEG. Migration `002_animal_images.sql` adds the two image-reference columns automatically on startup.

## Testing

```bash
python -m compileall -q app run.py wsgi.py
pytest -q
```
<<<<<<< HEAD

The repository does not contain a seed script or default credentials.
=======
>>>>>>> 1c174ce8dd3bd45f1ee03ccaaea6c57fe2fda01a
