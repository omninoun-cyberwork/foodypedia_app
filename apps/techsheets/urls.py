# C:\Foodypedia\apps\techsheets\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FicheTechniqueViewSet

# Créer un routeur DRF
router = DefaultRouter()

# Enregistrement du ViewSet avec basename explicite
router.register(r'fiches-techniques', FicheTechniqueViewSet, basename='fiche-technique')

# La variable 'urlpatterns' doit contenir le résultat du routeur
urlpatterns = [
    path('', include(router.urls)),
]
