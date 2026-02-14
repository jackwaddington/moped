from django.contrib import admin

from .models import FuelEntry


@admin.register(FuelEntry)
class FuelEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "odometer_km", "fuel_liters", "cost_per_liter", "total_spend")
    list_filter = ("timestamp",)
    ordering = ("-timestamp",)
