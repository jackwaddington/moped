from django.core.management.base import BaseCommand

from moped.services import GoogleSheetsService


class Command(BaseCommand):
    help = "Sync fuel entries from Google Sheets"

    def handle(self, *args, **options):
        service = GoogleSheetsService()
        count = service.sync_from_sheets()
        self.stdout.write(self.style.SUCCESS(f"Synced {count} entries"))
