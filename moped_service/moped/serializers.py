from rest_framework import serializers

from .models import FuelEntry


class FuelEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelEntry
        fields = ["id", "timestamp", "odometer_km", "fuel_liters", "cost_per_liter", "total_spend", "notes"]
