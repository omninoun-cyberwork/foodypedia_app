# C:\Foodypedia\apps\recipes\serializers.py

from rest_framework import serializers
from .models import Recette, Technique, QuantiteIngredient, RecipeCategory
from apps.ingredients.serializers import IngredientSerializer

# -----------------------------------------------------
# 1. Serializers Utilitaires
# -----------------------------------------------------

class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ['id', 'name', 'slug', 'parent']

class TechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technique
        fields = ['id', 'nom', 'description']

# -----------------------------------------------------
# 2. Ligne d'Ingrédient (Pivot)
# -----------------------------------------------------

class QuantiteIngredientSerializer(serializers.ModelSerializer):
    # Pour la lecture, on nested les objets complets
    ingredient_details = IngredientSerializer(source='ingredient', read_only=True)
    
    # Pour les sous-recettes (Recursive simple pour éviter l'infini)
    sub_recipe_name = serializers.CharField(source='sub_recipe.titre', read_only=True)
    
    class Meta:
        model = QuantiteIngredient
        fields = [
            'id', 
            'ingredient', 'ingredient_details', # Option A
            'sub_recipe', 'sub_recipe_name',    # Option B
            'quantite', 'unite', 'note'
        ]

# -----------------------------------------------------
# 3. Serializer Principal : RECETTE
# -----------------------------------------------------

class RecetteSerializer(serializers.ModelSerializer):
    # Relations Nested (Lecture)
    category_details = RecipeCategorySerializer(source='category', read_only=True)
    techniques_details = TechniqueSerializer(source='techniques_cles', many=True, read_only=True)
    lignes_ingredients = QuantiteIngredientSerializer(many=True, read_only=True)
    
    # Métadonnées Auteurs
    auteurs_names = serializers.StringRelatedField(source='auteurs', many=True, read_only=True)
    
    class Meta:
        model = Recette
        fields = [
            'id', 'titre', 'slug', 'description', 
            'category', 'category_details',
            'temps_preparation', 'temps_cuisson',
            'lignes_ingredients', # Liste technique (ingrédient OU sous-recette)
            'techniques_cles', 'techniques_details',
            'auteurs', 'auteurs_names',
            'date_creation'
        ]
