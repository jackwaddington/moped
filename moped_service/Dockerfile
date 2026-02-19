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

# Run the Django development server and set up the data
CMD python manage.py migrate --noinput && python manage.py sync_sheets && gunicorn moped_service.wsgi:application --bind 0.0.0.0:8000 --workers 2
