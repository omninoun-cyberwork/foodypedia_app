from rest_framework import serializers
from .models import (
    Ingredient, IngredientCategory, FunctionalCategory, 
    IngredientFamily, Label, CulinaryUse, IngredientImage
)
from apps.atlas.models import Pays
from apps.atlas.serializers import PaysSerializer, GlossaireSerializer

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
    # --- Champs Nested spécifiques ---
    glossary_term_details = GlossaireSerializer(source='glossary_term', read_only=True)
    origins_countries_details = serializers.SerializerMethodField()
    images = IngredientImageSerializer(many=True, read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'slug', 'scientific_name', 'description', 
            'glossary_term', 'glossary_term_details',
            'category', 
            'functional_categories', 
            'family', 
            'origins_countries', 'origins_countries_details',
            'labels', 
            'seasonality', 'flavor_profile', 'texture',
            'buying_guide', 'storage_guide', 'prep_guide', 'nutrition_info', 'allergens',
            'culinary_uses', 
            'specific_data', 'tags',
            'main_image', 'images', 'image_filename',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Nesting pour le front-end (Conversion des IDs en objets complets pour la lecture)
        if instance.category:
            representation['category'] = IngredientCategorySerializer(instance.category).data
        
        representation['functional_categories'] = FunctionalCategorySerializer(
            instance.functional_categories.all(), many=True
        ).data
        
        representation['family'] = IngredientFamilySerializer(instance.family).data if instance.family else None
        
        representation['labels'] = LabelSerializer(
            instance.labels.all(), many=True
        ).data
        
        representation['culinary_uses'] = CulinaryUseSerializer(
            instance.culinary_uses.all(), many=True
        ).data
            
        return representation

    def get_origins_countries_details(self, obj):
        # Utilisation d'un serializer simple pour les pays (id + nom)
        # Si apps.atlas.serializers n'existe pas encore, on fait un mini-custom ici
        return [{'id': p.id, 'nom': p.nom_fr, 'continent': p.continent} for p in obj.origins_countries.all()]
