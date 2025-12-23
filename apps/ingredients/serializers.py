from rest_framework import serializers
from .models import (
    Ingredient, IngredientCategory, FunctionalCategory, 
    IngredientFamily, Label, CulinaryUse, IngredientImage
)
from apps.atlas.models import Pays
from apps.atlas.serializers import PaysSerializer  # Assurez-vous d'avoir ce serializer dans Atlas

# -------------------------------------------------------------------------
# Serializers pour les relations (Read-Only ou Simple)
# -------------------------------------------------------------------------

class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = ['id', 'name', 'slug', 'icon']

class FunctionalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionalCategory
        fields = ['id', 'name', 'slug']

class IngredientFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientFamily
        fields = ['id', 'name']

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'icon']

class CulinaryUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulinaryUse
        fields = ['id', 'name']

class IngredientImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientImage
        fields = ['id', 'image', 'caption', 'order']

# -------------------------------------------------------------------------
# Serializer Principal : INGRÉDIENT
# -------------------------------------------------------------------------

class IngredientSerializer(serializers.ModelSerializer):
    # --- Champs Nested pour la lecture (GET) ---
    category_details = IngredientCategorySerializer(source='category', read_only=True)
    functional_categories_details = FunctionalCategorySerializer(source='functional_categories', many=True, read_only=True)
    family_details = IngredientFamilySerializer(source='family', read_only=True)
    labels_details = LabelSerializer(source='labels', many=True, read_only=True)
    culinary_uses_details = CulinaryUseSerializer(source='culinary_uses', many=True, read_only=True)
    origins_countries_details = serializers.SerializerMethodField()
    images = IngredientImageSerializer(many=True, read_only=True)

    # --- Pour l'écriture (POST/PUT), on garde les IDs standards ---
    # category = ID
    # functional_categories = [ID, ID]
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'slug', 'scientific_name', 'description', 
            'category', 'category_details',
            'functional_categories', 'functional_categories_details',
            'family', 'family_details',
            'origins_countries', 'origins_countries_details',
            'labels', 'labels_details',
            'seasonality', 'flavor_profile', 'texture',
            'buying_guide', 'storage_guide', 'prep_guide', 'nutrition_info', 'allergens',
            'culinary_uses', 'culinary_uses_details',
            'specific_data', 
            'main_image', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_origins_countries_details(self, obj):
        # Utilisation d'un serializer simple pour les pays (id + nom)
        # Si apps.atlas.serializers n'existe pas encore, on fait un mini-custom ici
        return [{'id': p.id, 'nom': p.nom_fr, 'continent': p.continent} for p in obj.origins_countries.all()]
