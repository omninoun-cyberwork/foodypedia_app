# C:\Foodypedia\apps\recipes\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecetteViewSet,
    RecipeCategoryViewSet,
    TechniqueViewSet,
    IngredientViewSet,
    QuantiteIngredientViewSet,
)

# Créer un routeur DRF
router = DefaultRouter()

# Enregistrement des ViewSets avec basename explicite
# CORRECTION : Ajout de basename='...'
router.register(r'recettes', RecetteViewSet, basename='recette')
router.register(r'categories', RecipeCategoryViewSet, basename='recipe-category')
router.register(r'techniques', TechniqueViewSet, basename='technique')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'quantites-ingredients', QuantiteIngredientViewSet, basename='quantite-ingredient')

# La variable 'urlpatterns' doit contenir le résultat du routeur
urlpatterns = [
    path('', include(router.urls)), 
]