from rest_framework import serializers
from .models import IngredientPrice, FicheTechnique, Technique

class IngredientPriceSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    
    class Meta:
        model = IngredientPrice
        fields = ['id', 'ingredient', 'ingredient_name', 'average_price', 'unit', 'updated_at']

class FicheTechniqueSerializer(serializers.ModelSerializer):
    recette_titre = serializers.CharField(source='recette_fk.titre', read_only=True)
    cout_par_portion = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    prix_vente_suggere = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = FicheTechnique
        fields = [
            'recette_fk', 'recette_titre', 
            'nombre_portions', 'cout_matiere_ht', 'marge_appliquee', 'cout_par_portion', 'prix_vente_suggere',
            'validation_admin', 'date_validation', 'materiel_requis_json'
        ]

class TechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technique
        fields = '__all__'
