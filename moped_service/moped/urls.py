from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FuelEntryViewSet

router = DefaultRouter()
router.register(r'moped-entries', FuelEntryViewSet, basename='moped-entry')

urlpatterns = [
    path('', include(router.urls)),
]