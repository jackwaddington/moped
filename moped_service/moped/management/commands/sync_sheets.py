from django.core.management.base import BaseCommand
from django.utils import timezone

from moped.calculations import cost_per_km
from moped.metrics import cost_per_km_gauge, current_odometer, days_since_last_fueling
from moped.models import FuelEntry
from moped.services import GoogleSheetsService


class Command(BaseCommand):
    help = "Sync fuel entries from Google Sheets"

    def handle(self, *args, **options):
        service = GoogleSheetsService()
        count = service.sync_from_sheets()
        self.stdout.write(self.style.SUCCESS(f"Synced {count} entries"))

        last_entry = FuelEntry.objects.first()
        if last_entry:
            current_odometer.set(last_entry.odometer_km)
            days = (timezone.now() - last_entry.timestamp).days
            days_since_last_fueling.set(days)

        qs = FuelEntry.objects.all()
        cost = cost_per_km(qs)
        if cost is not None:
            cost_per_km_gauge.set(cost)
