from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .calculations import fillup_pairs, fuel_efficiency, monthly_summary
from .models import FuelEntry
from .serializers import FuelEntrySerializer
from .services import GoogleSheetsService


class FuelEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for moped fuel tracking

    GET /api/moped-entries/ - List all entries
    GET /api/moped-entries/{id}/ - Get specific entry
    POST /api/moped-entries/sync/ - Sync from Google Sheets
    GET /api/moped-entries/last-fillup/ - Get last fuel entry
    GET /api/moped-entries/efficiency/?month=2025-01 - Fuel efficiency
    GET /api/moped-entries/fillups/ - Per-segment analysis
    GET /api/moped-entries/monthly/ - Monthly summaries
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

    @action(detail=False, methods=["get"], url_path="last-fillup")
    def last_fillup(self, request):
        """Get the most recent fuel entry"""
        last_entry = FuelEntry.objects.first()  # Already ordered by -timestamp
        if last_entry:
            serializer = self.get_serializer(last_entry)
            return Response(serializer.data)
        return Response({"message": "No fuel entries found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def efficiency(self, request):
        """Get fuel efficiency stats"""
        qs = self.get_queryset()
        month_str = request.query_params.get("month")

        if month_str:
            try:
                year, month = map(int, month_str.split("-"))
                qs = qs.filter(timestamp__year=year, timestamp__month=month)
            except ValueError:
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        result = fuel_efficiency(qs)
        if result is None:
            return Response(
                {"error": "Not enough data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"l_per_100km": result, "km_per_liter": round(100 / result, 2)})

    @action(detail=False, methods=["get"])
    def fillups(self, request):
        """Get per-segment fillup analysis"""
        qs = self.get_queryset()
        pairs = fillup_pairs(qs)
        return Response(pairs)

    @action(detail=False, methods=["get"])
    def monthly(self, request):
        """Get monthly fuel summary"""
        qs = self.get_queryset()
        summary = monthly_summary(qs)
        return Response(summary)
