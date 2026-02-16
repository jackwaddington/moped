from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FuelEntryViewSet

router = DefaultRouter()
router.register(r"moped-entries", FuelEntryViewSet, basename="moped-entry")

urlpatterns = [
    path("", include("django_prometheus.urls")),  # Prometheus metrics endpoint
    path("", include(router.urls)),
]
