from datetime import datetime, timedelta

from django.db.models import Avg, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FuelEntry
from .serializers import FuelEntrySerializer, MPGStatsSerializer
from .services import GoogleSheetsService


class FuelEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for moped fuel tracking

    GET /api/moped-entries/ - List all entries
    GET /api/moped-entries/{id}/ - Get specific entry
    POST /api/moped-entries/sync/ - Sync from Google Sheets
    GET /api/moped-entries/mpg/?month=2025-10 - Get MPG stats
    GET /api/moped-entries/last-fillup/ - Get last fuel entry
    """

    queryset = FuelEntry.objects.all()
    serializer_class = FuelEntrySerializer

    @action(detail=False, methods=["post"])
    def sync(self, request):
        """Sync data from Google Sheets"""
        try:
            sheets_service = GoogleSheetsService()
            count = sheets_service.sync_from_sheets()
            return Response({"status": "success", "entries_synced": count})
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def mpg(self, request):
        """Calculate MPG for a given period"""
        month_str = request.query_params.get("month")  # Format: 2025-10

        if month_str:
            try:
                year, month = map(int, month_str.split("-"))
                entries = FuelEntry.objects.filter(timestamp__year=year, timestamp__month=month)
                period = f"{year}-{month:02d}"
            except ValueError:
                return Response({"error": "Invalid month format. Use YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to last 30 days
            since = datetime.now() - timedelta(days=30)
            entries = FuelEntry.objects.filter(timestamp__gte=since)
            period = "Last 30 days"

        if entries.count() < 2:
            return Response({"error": "Not enough data to calculate consumption"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate consumption
        first_entry = entries.order_by("odometer_km").first()
        last_entry = entries.order_by("odometer_km").last()

        total_km = last_entry.odometer_km - first_entry.odometer_km
        total_liters = entries.exclude(pk=first_entry.pk).aggregate(Sum("fuel_liters"))["fuel_liters__sum"]
        avg_cost_per_liter = entries.aggregate(Avg("cost_per_liter"))["cost_per_liter__avg"]
        km_per_liter = total_km / total_liters if total_liters > 0 else 0
        miles_per_gallon = km_per_liter * 2.352  # Convert to MPG (US gallons)

        data = {
            "period": period,
            "total_km": round(total_km, 2),
            "total_liters": round(total_liters, 2),
            "km_per_liter": round(km_per_liter, 2),
            "miles_per_gallon": round(miles_per_gallon, 2),
            "average_cost_per_liter": round(avg_cost_per_liter, 2) if avg_cost_per_liter else 0,
        }

        serializer = MPGStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="last-fillup")
    def last_fillup(self, request):
        """Get the most recent fuel entry"""
        last_entry = FuelEntry.objects.first()  # Already ordered by -timestamp
        if last_entry:
            serializer = self.get_serializer(last_entry)
            return Response(serializer.data)
        return Response({"message": "No fuel entries found"}, status=status.HTTP_404_NOT_FOUND)
