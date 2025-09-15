IP Admin
========

A Django-based IP address management (IPAM) and request workflow application that brings structure, visibility, and auditability to assigning IPv4 addresses across VLANs and pools.

Highlights
---------

- IP request workflow: users request IPs by VLAN; admins review/approve with comments.
- Auto assignment: approved requests receive unique IPs from defined pools.
- VLAN & pool management: define VLANs, IPv4 ranges, masks, gateways, and DNS.
- Usage insights: total, assigned, and percent utilization per pool.
- Role-aware dashboard: metrics, latest requests, and user counts.
- Authentication: email-based login; optional two-factor (django-otp + two-factor).
- Dockerized dev: PostgreSQL + smtp4dev for local testing.

Repository Structure
--------------------

- `core/` Django project and apps
  - `accounts/` custom user model and admin user management
  - `ipm/` VLAN and IP Pool models, forms, and views
  - `requestflow/` request/approval logic and IP assignment
  - `dashboard/` metrics and overview
  - `templates/` and `static/` UI assets
- `Dockerfiles/`, `docker-compose.yml` for local development

Screenshots
-----------

Add screenshots to showcase the UI (suggested):
- Dashboard overview with request counts and utilization
- VLAN/IP Pool list with usage bars
- IP request form and admin approval view

Quick Start (Docker)
--------------------

1) Requirements: Docker and Docker Compose

2) Start services

```
docker compose up --build -d
```

3) Initialize database and superuser

```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

4) Access the app

- App: http://localhost:8000
- Dev SMTP (smtp4dev): http://localhost:5000

Quick Start (Manual)
--------------------

1) Requirements: Python 3.12+, PostgreSQL 13+

2) Install dependencies

```
python -m venv .venv && . .venv/bin/activate  # or Windows equivalent
pip install -r requirements.txt
```

3) Configure environment

Set environment variables (see Environment Variables) and ensure your DB settings match.

4) Run migrations and create a superuser

```
python manage.py migrate
python manage.py createsuperuser
```

5) Start the dev server

```
python manage.py runserver
```

Environment Variables
---------------------

- `DJANGO_SECRET_KEY`: Strong secret; required in production.
- `DJANGO_DEBUG`: `true`/`false` (use `false` in production).
- `DJANGO_ALLOWED_HOSTS`: Comma-separated hostnames, e.g. `example.com,www.example.com`.
- Database (if not using Docker defaults):
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT`
- Email (optional):
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` or `EMAIL_USE_SSL`

Development
-----------

- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Collect static (prod): `python manage.py collectstatic --noinput`
- Run tests: `python manage.py test`

Production Deployment
---------------------

- Use a production WSGI server (e.g., Gunicorn) behind a reverse proxy (Nginx/Traefik).
- Run migrations and collect static during deployment.
- Serve static files from `STATIC_ROOT` via your proxy or add WhiteNoise.
- Configure HTTPS and security headers.

Example commands:

```
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Security Checklist
------------------

- `DJANGO_DEBUG=false` and `DJANGO_ALLOWED_HOSTS` set.
- Strong `DJANGO_SECRET_KEY` from env or secret store.
- HTTPS enforced: set `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- Consider HSTS: `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`.
- Restrict `/admin/` at the proxy and enable 2FA for admins where possible.

Roadmap (Examples)
------------------

- Extended audit logs and approvals
- Integrations with monitoring/CMDB
- Advanced RBAC and SSO

Contributing
------------

Contributions are welcome! Please open an issue to discuss proposed changes or feature requests. For larger contributions, consider creating a draft PR early for feedback.

License
-------

Select and add a LICENSE file appropriate for your goals (e.g., MIT, Apache-2.0, AGPL-3.0). This repository currently expects a `LICENSE` file at the root.

Links
-----

- GitHub: https://github.com/your-org/ipadmin
- Project docs: see `core/README.md`

