import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MopedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moped"

    def ready(self):
        from django.utils import timezone

        from .calculations import cost_per_km
        from .metrics import cost_per_km_gauge, current_odometer, days_since_last_fueling

        try:
            from .models import FuelEntry

            last_entry = FuelEntry.objects.first()
            if last_entry:
                current_odometer.set(last_entry.odometer_km)
                days = (timezone.now() - last_entry.timestamp).days
                days_since_last_fueling.set(days)

            qs = FuelEntry.objects.all()
            cost = cost_per_km(qs)
            if cost is not None:
                cost_per_km_gauge.set(cost)
        except Exception as e:
            logger.warning(f"Could not set initial metrics: {e}")
