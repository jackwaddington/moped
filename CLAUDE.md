# Moped Fuel Tracker

## Quick Start

```bash
cd moped_service
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

## Environment

- Python 3.11
- Django 4.2 + Django REST Framework
- Requires `.env` file in `moped_service/` (see `.env.example`)

## Commands

```bash
ruff check .          # lint
ruff format .         # format
python manage.py test # tests
```

## Conventions

- Linting/formatting: ruff (config in pyproject.toml)
- Import order enforced by ruff (stdlib, third-party, local)
- Secrets via environment variables (python-decouple), never hardcoded
- Double quotes for strings (ruff default)
