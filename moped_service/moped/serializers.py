from rest_framework import serializers
from .models import FuelEntry

class FuelEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelEntry
        fields = ['id', 'timestamp', 'odometer_km', 'fuel_liters', 'cost_per_liter', 'total_spend', 'notes']


class MPGStatsSerializer(serializers.Serializer):
    """Serializer for MPG statistics response"""
    period = serializers.CharField()
    total_km = serializers.FloatField()
    total_liters = serializers.FloatField()
    km_per_liter = serializers.FloatField()
    miles_per_gallon = serializers.FloatField()
    average_cost_per_liter = serializers.DecimalField(max_digits=10, decimal_places=2)

