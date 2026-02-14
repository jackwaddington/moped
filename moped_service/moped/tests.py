from datetime import datetime

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import FuelEntry


class FuelEntryModelTest(TestCase):
    """Tests for the FuelEntry model"""

    def setUp(self):
        """Runs before each test — creates test data"""
        self.entry = FuelEntry.objects.create(
            timestamp=datetime(2025, 1, 15, 10, 0),
            odometer_km=1500.0,
            fuel_liters=3.2,
            cost_per_liter=1.85,
            total_spend=5.92,
        )

    def test_str_representation(self):
        """__str__ should return 'date - km'"""
        self.assertEqual(str(self.entry), "2025-01-15 - 1500.0km")

    def test_default_ordering(self):
        """Entries should be ordered by -timestamp (newest first)"""
        older = FuelEntry.objects.create(
            timestamp=datetime(2025, 1, 10, 10, 0),
            odometer_km=1400.0,
            fuel_liters=2.8,
        )
        entries = list(FuelEntry.objects.all())
        self.assertEqual(entries[0], self.entry)  # newer first
        self.assertEqual(entries[1], older)


class FuelEntryAPITest(APITestCase):
    """Tests for the API endpoints"""

    def setUp(self):
        """Create test entries for API tests"""
        self.entry1 = FuelEntry.objects.create(
            timestamp=datetime(2025, 1, 10, 10, 0),
            odometer_km=1000.0,
            fuel_liters=3.0,
            cost_per_liter=1.80,
            total_spend=5.40,
        )
        self.entry2 = FuelEntry.objects.create(
            timestamp=datetime(2025, 1, 15, 10, 0),
            odometer_km=1050.0,
            fuel_liters=2.5,
            cost_per_liter=1.85,
            total_spend=4.63,
        )
        self.entry3 = FuelEntry.objects.create(
            timestamp=datetime(2025, 1, 20, 10, 0),
            odometer_km=1120.0,
            fuel_liters=3.5,
            cost_per_liter=1.90,
            total_spend=6.65,
        )

    def test_list_entries(self):
        """GET /api/moped-entries/ should return all entries"""
        response = self.client.get("/api/moped-entries/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)

    def test_last_fillup(self):
        """GET /api/moped-entries/last-fillup/ should return newest entry"""
        response = self.client.get("/api/moped-entries/last-fillup/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["odometer_km"], 1120.0)

    def test_last_fillup_empty(self):
        """last-fillup should return 404 when no entries exist"""
        FuelEntry.objects.all().delete()
        response = self.client.get("/api/moped-entries/last-fillup/")
        self.assertEqual(response.status_code, 404)

    def test_mpg_excludes_first_fillup_fuel(self):
        """MPG calculation should exclude the first entry's fuel.

        The first fillup's fuel was burned BEFORE that odometer reading,
        so it doesn't belong in the distance/fuel calculation.

        Distance: 1120 - 1000 = 120 km
        Fuel (excluding first): 2.5 + 3.5 = 6.0 L
        km_per_liter: 120 / 6.0 = 20.0
        """
        response = self.client.get("/api/moped-entries/mpg/?month=2025-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_km"], 120.0)
        self.assertEqual(response.data["total_liters"], 6.0)  # NOT 9.0
        self.assertEqual(response.data["km_per_liter"], 20.0)  # NOT 13.33
