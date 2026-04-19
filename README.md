# SmartSeason Field Monitoring System

A web application for tracking crop progress across multiple fields during a growing season. Built for agricultural coordinators (admins) and field agents to collaborate efficiently.

## Tech stack

- **Backend** — Django 4.2
- **Frontend** — HTMX + Tailwind CSS 
- **Database** — SQLite (development) / PostgreSQL (production)
- **Deployment** — Railway
- **Python** — 3.9+

---

## Local setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Shamba_records
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root

```
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

When prompted, use:
- Username: `admin`
- Password: your choice

### 7. Seed demo data

```bash
python manage.py seed_data
```

This creates:
- 2 demo field agents (`agent_john`, `agent_sara`)
- 4 sample fields at various stages
- Field update history for each field

### 8. Start the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000`

---

## Demo credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | (password you set with createsuperuser) |
| Agent | agent_john | agent123 |
| Agent | agent_sara | agent123 |

---

## Live deployment

Deployed on Railway: `<your-railway-url-here>`

Use the demo credentials above to log in.

---

## Design decisions

### 1. Django + HTMX instead of a SPA

HTMX allows dynamic UI updates — form submissions that swap page fragments without a full reload — without building a separate React or Vue frontend. The server renders HTML directly, meaning no JSON API layer, no build tooling and no JavaScript framework to maintain. This keeps the stack simple and the codebase readable for a project of this scope.

### 2. Custom User model from day one

Django's documentation explicitly recommends creating a custom User model at the start of every project even if no extra fields are needed initially. A single `role` field (`ADMIN` / `AGENT`) drives all access control logic via two helper properties (`user.is_admin`, `user.is_agent`), keeping views and templates readable.

### 3. FieldUpdate as a separate model

Rather than overwriting the stage directly on `Field`, every change is recorded as an immutable `FieldUpdate` row. This provides a full audit trail showing who changed what and when, and lets the status logic reason about the timestamp of the last update rather than the field's own `updated_at`.

### 4. Status as a computed property

Field status (Active / At Risk / Completed) is never stored in the database. It is computed on the fly from the field's current stage and the timestamp of the most recent `FieldUpdate`. This means it always reflects reality without needing background jobs, signals or manual updates. The trade-off is a small extra query per field — negligible at this scale.

### 5. Status logic rules

| Status | Rule |
|--------|------|
| Completed | Stage is `HARVESTED` |
| At Risk | Stage is `READY` with no update in 14+ days, or no update in 7+ days for any other active stage |
| Active | Everything else |

The at-risk timer is based on the last `FieldUpdate` timestamp, not the field's own `updated_at`. This prevents an admin editing the crop name from accidentally resetting the timer.

### 6. PostgreSQL in production, SQLite in development

SQLite requires zero configuration and is sufficient for local development. The `dj-database-url` and `python-decouple` packages mean the same codebase reads from `DATABASE_URL` in production (set automatically by Railway's PostgreSQL plugin) with no code changes.

---

## Project structure

```
Shamba_records/
├── config/                  # Django settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── fields/                  # Field management app
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Demo data command
│   ├── migrations/
│   ├── models.py            # Field and FieldUpdate models
│   ├── views.py             # Dashboard, CRUD and HTMX endpoints
│   ├── forms.py             # FieldForm and FieldUpdateForm
│   └── urls.py
├── users/                   # Authentication app
│   ├── migrations/
│   ├── models.py            # Custom User model with role
│   ├── views.py             # Login and logout
│   └── urls.py
├── templates/               # All HTML templates
│   ├── base.html            # Base layout with Sowphie.io palette
│   ├── users/
│   │   └── login.html
│   └── fields/
│       ├── dashboard.html
│       ├── field_list.html
│       ├── field_detail.html
│       ├── field_form.html
│       ├── field_confirm_delete.html
│       └── partials/
│           └── updates_list.html  # HTMX fragment
├── requirements.txt
├── Procfile                 # Railway start command
├── runtime.txt              # Python version for Railway
└── manage.py
```

---

## URL reference

| Path | Method | Purpose | Access |
|------|--------|---------|--------|
| `/` | GET | Dashboard | Login required |
| `/fields/` | GET | Field list | Login required |
| `/fields/create/` | GET/POST | Create field | Admin only |
| `/fields/<id>/` | GET | Field detail | Login required |
| `/fields/<id>/edit/` | GET/POST | Edit field | Admin only |
| `/fields/<id>/delete/` | GET/POST | Delete field | Admin only |
| `/fields/<id>/add-update/` | POST | Post field update | Assigned agent or admin |
| `/accounts/login/` | GET/POST | Login | Public |
| `/accounts/logout/` | GET | Logout | Login required |

---

## Manual testing checklist

- [ ] Login as `agent_john` — dashboard shows only North Block and South Plot
- [ ] Login as `admin` — dashboard shows all 4 fields with stats and charts
- [ ] Create a new field as admin and assign to an agent
- [ ] As agent, post an update — list swaps without page reload (HTMX)
- [ ] Visit a field not assigned to you as agent — returns 403
- [ ] Edit and delete a field as admin
- [ ] Verify "Needs attention" panel shows at-risk fields
- [ ] Verify status badges reflect Active / At Risk / Completed correctly

---

## Assumptions made

1. **One agent per field** — fields are assigned to a single agent; shared ownership is not supported
2. **Agents cannot create fields** — only admins create and assign fields; agents operate within their assignments
3. **Status is read-only** — status is computed automatically and cannot be manually overridden
4. **No field transfer restriction** — admins can reassign a field to a different agent at any time via the edit view

---

## Future enhancements

- REST API for a mobile companion app
- Email and SMS alerts when a field becomes at-risk
- Photo attachments on field updates
- CSV and PDF export of field history
- Weather data integration per field location
- Historical trend charts across growing seasons