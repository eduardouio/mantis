# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mantis** is a Django 4.2 project management system for equipment rental, technician management, and work order tracking. It serves a field services company (Ecuador) managing physical equipment, service resources, technicians, and client projects.

## Development Commands

All Django commands run from `app/src/`:

```bash
cd app/src

# Run development server
./manage.py runserver 0.0.0.0:8000

# Migrations
./manage.py makemigrations <app_name>
./manage.py migrate

# Seed database
./manage.py sowseed
./manage.py populate_history --auto

# Export/import data
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude auth.permission --exclude contenttypes --exclude admin.logentry \
  > data.json
./manage.py loaddata data.json -v 3
```

## Testing

```bash
cd app/src

# Run all tests
pytest -v

# Run a single test file
pytest tests/api/test_AddResourceProjectAPI.py -v

# Run a single test method
pytest tests/api/test_AddResourceProjectAPI.py::TestAddResourceProjectAPI::test_add_resource_success -v

# With coverage
pytest --cov=api --cov-report=html
```

- Config: `app/src/pytest.ini`, `DJANGO_SETTINGS_MODULE = peisol.settings`
- Uses SQLite for tests (overridden in conftest.py), PostgreSQL in development/production
- Fixtures in `app/src/conftest.py`

## Frontend (Vue 3 + Vite)

```bash
cd app/client/mantis
npm install
npm run dev    # dev server
npm run build  # outputs to /static/js/app/
```

## Production Deployment

```bash
sudo systemctl restart mantis.service
sudo systemctl restart nginx
```

## Architecture

### Django Project Structure

- **Django project name**: `peisol` — settings and root URLs are in `app/src/peisol/`
- **Apps**: `accounts`, `equipment`, `projects`, `api`, `common`, `filemanager`, `reports`
- **Admin theme**: django-grappelli at `/grappelli/`
- **Database credentials**: `common/secrets.py` (not in version control)

### URL Layout

- `/` — standard Django views (accounts, equipment, projects, reports, filemanager)
- `/api/` — REST API (DRF)
- `/admin/` — Django admin

### BaseModel Pattern

All models inherit from `common/BaseModel.py` which provides:
- `created_at`, `updated_at`, `is_active`, `is_deleted` (soft delete — never hard-delete data)
- `id_user_created`, `id_user_updated` via `django-crum` (current request user)
- SimpleHistory integration for full audit trail
- Class methods: `get_all()`, `get_by_id()`, `get_ignore_deleted()`, `get_by_id_user()`

### Authentication

- Custom email-based user model (`accounts.CustomUserModel`) — email is USERNAME_FIELD
- Roles: `ADMINISTRATIVO` / `TECNICO`
- Sessions stored in database (`user_sessions` app)
- JWT available via `djangorestframework-simplejwt`

### Key Domain Concepts

**Equipment vs Service Resources** (`equipment/models/ResourceItem`):
- `is_service=False` (Equipment): Physical item — can only be assigned to **one project at a time**
- `is_service=True` (Service): Can be in **multiple projects simultaneously**
- `physical_equipment_code` on `ProjectResourceItem` links a service item to its physical equipment counterpart

**Resource Lifecycle**:
1. Resource is `DISPONIBLE` → added to project via `ProjectResourceItem`
2. While active: `RENTADO`, tracked with `operation_start_date`
3. Retired: `is_retired=True`, `retirement_date` set, cost calculated by days active

**ProjectResourceItem** (`projects/models/`) is the central join table linking `ResourceItem` ↔ `Project` with rental cost, maintenance intervals, and retirement tracking.

### File Uploads

Centralized via `/api/load_files/`. Key paths in `media/`:
- `technicals/profile_images/`, `technicals/vaccine_certificates/`, `technicals/dni/`, `technicals/licenses/`
- Vehicles: separate paths per document type
- Projects: project-specific document trees

### PDF Generation

WeasyPrint (HTML→PDF) and ReportLab are used for custody chains, technician reports, and equipment reports. The base URL is dynamically determined (production vs development) for WeasyPrint asset resolution.

### Frontend

Vue 3 SPA compiled to `static/js/app/`. Templates in `templates/` use a hybrid approach — Django templates render the initial page, with Vue components mounted for interactive sections.

## Key Dependencies

| Package | Purpose |
|---|---|
| `django-simple-history` | Audit trail on all models |
| `django-crum` | Auto-populate created_by/updated_by |
| `WeasyPrint` | HTML→PDF report generation |
| `reportlab` | PDF creation |
| `openpyxl` | Excel export |
| `pypdf` | PDF merge |
| `django-grappelli` | Admin UI theme |
| `django-import-export` | Admin bulk import/export |
