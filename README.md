# Moped Fuel Tracker

Django REST API that pulls fuel data from Google Sheets (fed by Google Forms) and exposes efficiency calculations, cost analysis, and service reminders.

## What it does

I record every fuel stop on my moped via a Google Form (date, odometer, litres, cost). This service syncs that data and calculates:

- **Fuel efficiency** in l/100km and km/L
- **Cost per km** driven
- **Per-fillup analysis** with distance, efficiency, and cost between stops
- **Monthly summaries** of distance, fuel, and cost
- **Service reminders** based on odometer intervals (oil change every 1000km, warranty service every 3000km)

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/moped-entries/` | GET | List all fuel entries |
| `/api/moped-entries/{id}/` | GET | Single entry |
| `/api/moped-entries/sync/` | POST | Sync from Google Sheets |
| `/api/moped-entries/last-fillup/` | GET | Most recent fuel entry |
| `/api/moped-entries/efficiency/` | GET | l/100km, km/L, cost/km |
| `/api/moped-entries/fillups/` | GET | Per-segment analysis |
| `/api/moped-entries/monthly/` | GET | Monthly summaries |
| `/api/moped-entries/service-status/` | GET | Service reminders |
| `/api/docs/` | GET | Swagger UI |
| `/api/metrics` | GET | Prometheus metrics |

## Architecture

Google Forms -> Google Sheets -> **sync_sheets** -> SQLite (cache) -> Django REST API -> Prometheus -> Grafana

The SQLite database is an ephemeral cache of the Google Sheets data. All calculations are performed on request. The sync runs on container startup and weekly via a k8s CronJob.

## Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `moped_sync_operations_total` | Counter | Sync operations by status (success/error) |
| `moped_entries_synced_last` | Gauge | Entries synced in last operation |
| `moped_km_until_service` | Gauge | km remaining until next service (by type) |
| `moped_current_odometer_km` | Gauge | Current odometer reading |
| `moped_days_since_last_fueling` | Gauge | Days since last fuel entry |
| `moped_cost_per_km` | Gauge | Cost per km in euros |

Plus standard django-prometheus metrics (request counts, latencies, DB queries).

## Deployment

Runs on a [k3s cluster](https://github.com/jackwaddington/k3s) via [ArgoCD](https://github.com/jackwaddington/homelab-gitops). CI/CD pipeline:

1. Push to `main` triggers GitHub Actions
2. Docker image built and pushed to `ghcr.io/jackwaddington/moped-service:latest`
3. ArgoCD detects the change and deploys to k3s
4. CronJob re-syncs from Google Sheets weekly (Mondays 3am)

## Local Development

```bash
cd moped_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in values
python manage.py migrate
python manage.py runserver
```

## Commands

```bash
ruff check .                   # lint
ruff format .                  # format
python manage.py test          # 15 tests
python manage.py sync_sheets   # manual sync from Google Sheets
```

## Tech Stack

- Python 3.11, Django 4.2, Django REST Framework
- Google Sheets API (service account)
- django-prometheus for metrics
- gunicorn for production serving
- Docker, GitHub Actions, k3s, ArgoCD