# C:\Foodypedia\apps\atlas\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaysViewSet, MaterielViewSet, GlossaireViewSet

# Créer un routeur DRF
router = DefaultRouter()

# Enregistrement des ViewSets avec basename explicite
router.register(r'pays', PaysViewSet, basename='pays')
router.register(r'materiel', MaterielViewSet, basename='materiel')
router.register(r'glossaire', GlossaireViewSet, basename='glossaire')

# La variable 'urlpatterns' doit contenir le résultat du routeur
urlpatterns = [
    path('', include(router.urls)),
]
