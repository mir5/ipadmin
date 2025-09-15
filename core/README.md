IP Admin
========

A Django-based IP management and request workflow application.

Project Status: MVP
-------------------

This is the first MVP release of IP Admin. It covers the essential user and admin flows (requests, approvals, VLAN/IP pool management, and dashboard). Additional features, integrations, and production hardening will roll out in subsequent versions.

Features
--------

- IP request workflow: users request IPs by VLAN; admins review/approve.
- IP pool management: VLANs and IPv4 pools with usage metrics.
- Dashboard: key counts, recent requests, and pool stats.
- Custom auth: email-based login with a custom `accounts.User` model.
- Optional 2FA: `django-two-factor-auth` and `django-otp` installed (see below).

Tech Stack
----------

- Python 3.12, Django 5.2
- PostgreSQL (via Docker)
- Bootstrap-based UI assets under `core/static`

Project Layout
--------------

- `core/` Django project root (manage.py, settings, apps)
  - `accounts/` custom user model, admin user management
  - `ipm/` VLAN and IP Pool management
  - `requestflow/` request/approval + IP assignment
  - `dashboard/` home dashboard
  - `templates/`, `static/` app assets

Quick Start (Docker)
--------------------

1. Ensure Docker and Docker Compose are installed.
2. Copy or set environment variables (see Env Vars) for development.
3. Start services:
   docker compose up --build
4. Apply migrations inside the backend container (first run only):
   docker compose exec backend python manage.py migrate
5. Create a superuser:
   docker compose exec backend python manage.py createsuperuser
6. Open the app at http://localhost:8000

Quick Start (Manual)
--------------------

1. Python 3.12+ and PostgreSQL 13+.
2. Create and activate a virtualenv.
3. Install deps:
   pip install -r requirements.txt
4. Set environment variables (see Env Vars), or adjust `DATABASES` in `core/core/settings.py`.
5. Migrate and create a superuser:
   python manage.py migrate
   python manage.py createsuperuser
6. Run the dev server:
   python manage.py runserver

Environment Variables
---------------------

- `DJANGO_SECRET_KEY`: Required in production; a strong random value.
- `DJANGO_DEBUG`: `true`/`false` (default should be `false` in prod).
- `DJANGO_ALLOWED_HOSTS`: Comma-separated hostnames for prod, e.g. `example.com,www.example.com`.
- Database (if not using Docker defaults):
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT`
- Email (optional, for password change notifications, etc.):
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`/`EMAIL_USE_SSL`

User Roles & Access
-------------------

- Regular users: submit IP requests, view their own requests and assigned IPs.
- Superusers: manage users, VLANs/IP pools, and approve/reject requests.

Two-Factor Authentication (Optional)
------------------------------------

The project includes `django-two-factor-auth` and `django-otp`. To enable 2FA login flows:

1. Include two-factor URLs in `core/core/urls.py` (example):
   path('account/', include('two_factor.urls', 'two_factor')),
2. Set the login URL to the 2FA login named route in `settings.py`:
   LOGIN_URL = 'two_factor:login'
3. Ensure `django_otp.middleware.OTPMiddleware` is in `MIDDLEWARE` (it is).
4. Visit `/account/two_factor/setup/` to enroll a device for a user.

Production Deployment
---------------------

- Set `DJANGO_DEBUG=false`, provide `DJANGO_SECRET_KEY`, and set `DJANGO_ALLOWED_HOSTS`.
- Run migrations and collect static:
  python manage.py migrate
  python manage.py collectstatic --noinput
- Serve Django with a production WSGI server (e.g., Gunicorn) behind a reverse proxy (Nginx/Traefik).
- Serve static files from `STATIC_ROOT` via the proxy, or add WhiteNoise in Django if preferred.
- Ensure HTTPS and security headers/cookies are enforced (see checklist).

Security Checklist
------------------

- DEBUG off in prod; `ALLOWED_HOSTS` set.
- Strong `SECRET_KEY` loaded from env/secret store.
- HTTPS enforced; set `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- Consider HSTS: `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`.
- Restrict `/admin/` at proxy and use 2FA for admins when possible.
- Database backups and access controls configured.

Troubleshooting
---------------

- DB connection errors in Docker: confirm `db` service is healthy and the backend depends_on is satisfied.
- Static not loading in prod: verify `collectstatic` ran and proxy serves from `STATIC_ROOT`.
- Login issues: ensure email-based auth backend is active and templates use email fields.
