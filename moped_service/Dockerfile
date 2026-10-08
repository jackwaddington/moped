FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Collect static files (if any) - this is a no-op if there are no static files
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose the port Django runs on
EXPOSE 8000

# Migrate, do an initial Sheets sync, then serve. A failed sync (Sheets API
# down, creds missing) must not stop the API from starting -- the data is
# re-synced on the weekly job anyway -- so it's allowed to fail here.
CMD python manage.py migrate --noinput && (python manage.py sync_sheets || echo "initial sheets sync failed, serving existing data") && exec gunicorn moped_service.wsgi:application --bind 0.0.0.0:8000 --workers 2
