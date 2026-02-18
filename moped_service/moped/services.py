import logging
from datetime import datetime

from decouple import config
from django.db import transaction
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

    def _parse_timestamp(self, value):
        """Parse timestamp, trying multiple date formats"""
        for fmt in ("%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse timestamp: {value}")

    def _parse_row(self, row):
        """Parse a single spreadsheet row into field values.
        Returns a dict of fields, or None if the row is malformed."""
        if len(row) < 3:
            return None
        try:
            return {
                "timestamp": self._parse_timestamp(row[0]),
                "odometer_km": float(row[1]),
                "fuel_liters": float(row[2]),
                "cost_per_liter": float(row[3]) if len(row) > 3 and row[3] else None,
                "total_spend": float(row[4]) if len(row) > 4 and row[4] else None,
                "notes": row[5] if len(row) > 5 else "",
            }
        except (ValueError, IndexError) as e:
            logger.warning("Skipping row due to error: %s", e)
            return None

    @transaction.atomic
    def sync_from_sheets(self):
        """Fetch data from Google Sheets and sync to database"""
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()

        values = result.get("values", [])

        count = 0
        for row in values:
            parsed = self._parse_row(row)
            if parsed is None:
                continue

            FuelEntry.objects.update_or_create(
                timestamp=parsed["timestamp"],
                odometer_km=parsed["odometer_km"],
                defaults={
                    "fuel_liters": parsed["fuel_liters"],
                    "cost_per_liter": parsed["cost_per_liter"],
                    "total_spend": parsed["total_spend"],
                    "notes": parsed["notes"],
                },
            )
            count += 1

        return count

