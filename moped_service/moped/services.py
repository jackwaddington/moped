import logging
from datetime import datetime

from decouple import config
from google.oauth2 import service_account
from googleapiclient.discovery import build

from .models import FuelEntry

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service to interact with Google Sheets"""

    def __init__(self):
        self.spreadsheet_id = config("GOOGLE_SHEET_ID")
        self.range_name = config("GOOGLE_SHEET_RANGE", default="Form Responses 1!A2:E")

        # Load credentials from service account JSON
        credentials = service_account.Credentials.from_service_account_file(
            config("GOOGLE_SERVICE_ACCOUNT_FILE"), scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )

        self.service = build("sheets", "v4", credentials=credentials)

    def sync_from_sheets(self):
        """Fetch data from Google Sheets and sync to database"""
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()

        values = result.get("values", [])

        # Clear existing data (or implement smarter sync logic)
        FuelEntry.objects.all().delete()

        # Parse and save entries
        entries = []
        for row in values:
            if len(row) >= 3:  # At minimum: timestamp, km, liters
                try:
                    entry = FuelEntry(
                        timestamp=datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S"),
                        odometer_km=float(row[1]),
                        fuel_liters=float(row[2]),
                        cost_per_liter=float(row[3]) if len(row) > 3 and row[3] else None,
                        total_spend=float(row[4]) if len(row) > 4 and row[4] else None,
                        notes=row[5] if len(row) > 5 else "",
                    )
                    entries.append(entry)
                except (ValueError, IndexError) as e:
                    # Log error and skip malformed rows
                    logger.warning("Skipping row due to error: %s", e)
                    continue

        FuelEntry.objects.bulk_create(entries)
        return len(entries)
