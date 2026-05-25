# Deployment Guide for Campus Thoughts

This repository is a Django server-rendered app with REST API endpoints. The recommended production deployment is to host the backend on Render and keep the frontend as a separate static/API client if you want to use Vercel.

## 1. Backend on Render

### 1.1 Prepare the Backend
1. Update environment variables in Render:
   - `DJANGO_SECRET_KEY`: a strong secret string
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: your Render hostname (e.g. `my-app.onrender.com`)
   - `DATABASE_URL`: Render Postgres URL if using Postgres
   - `CSRF_TRUSTED_ORIGINS`: Render URL, plus Vercel origin if you use a separate frontend
   - `CORS_ALLOWED_ORIGINS`: Vercel origin(s) if using a separate frontend
   - `EMAIL_BACKEND`: optional SMTP backend for password reset
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
   - `PYTHON_VERSION`: `3.10.15` when using Render (optional, but matches `runtime.txt`)

2. Use the following commands in Render:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn campusThoughts.wsgi:application`

3. Static files are served by WhiteNoise. Before deployment, collect static files:
   - `python manage.py collectstatic --noinput`

### 1.2 Use a Persistent Media Storage
Render web services do not preserve uploaded files across deploys unless you configure a persistent disk or external storage.

Options:
- Mount a Render Persistent Disk and set `MEDIA_ROOT` accordingly
- Use S3 / Cloud Storage with `django-storages`

## 2. Frontend on Vercel

This repository does not contain a separate frontend app. To deploy frontend on Vercel, you must create a separate static or JavaScript frontend (React, Next.js, Astro, plain HTML/JS) that consumes the backend API.

### 2.1 Recommended approach
1. Create a new frontend repo or folder.
2. Build UI pages that call Render backend API endpoints at `https://<your-render-app>.onrender.com/api/...`.
3. Host the frontend on Vercel as a Static Site or Next.js app.
4. Set the frontend environment variable(s) in Vercel for the backend API base URL.

### 2.2 Required backend support
The backend already exposes API endpoints under `/api/` and supports JWT authentication.

You should also configure these environment values in Render:
- `CORS_ALLOWED_ORIGINS`: `https://<your-vercel-app>.vercel.app`
- `CSRF_TRUSTED_ORIGINS`: `https://<your-vercel-app>.vercel.app`

## 3. Key configuration changes added
- Added `dj-database-url`, `whitenoise`, and `django-cors-headers`
- Added a `Procfile` for Render
- Added environment-driven `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`
- Added `STATIC_ROOT` and WhiteNoise static serving

## 4. If you prefer a single deployment
If you do not want to build a separate frontend, deploy the full Django app on Render only. Render is the best host for this Django application.

---

If you need, I can also help you convert the existing templates into a separate React/Next.js frontend for Vercel.
