# C:\Foodypedia\apps\chefs\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChefViewSet

# Créer un routeur DRF
router = DefaultRouter()

# Enregistrement du ViewSet avec basename explicite
router.register(r'', ChefViewSet, basename='chef')

# La variable 'urlpatterns' doit contenir le résultat du routeur
urlpatterns = [
    path('', include(router.urls)),
]
