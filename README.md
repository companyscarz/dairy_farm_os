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
pytest -q
```
