from django.db import models


class FuelEntry(models.Model):
    """Model to cache fuel entries from Google Sheets"""

    timestamp = models.DateTimeField()
    odometer_km = models.FloatField()
    fuel_liters = models.FloatField()
    cost_per_liter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_spend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp.date()} - {self.odometer_km}km"
