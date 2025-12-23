# C:\Foodypedia\apps\techsheets\serializers.py

from rest_framework import serializers
from .models import FicheTechnique
from apps.recipes.models import Recette


class RecetteSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour afficher les informations de base d'une recette.
    Utilisé en nested dans FicheTechniqueSerializer.
    """
    class Meta:
        model = Recette
        fields = ['id', 'titre', 'description', 'temps_preparation', 'temps_cuisson']
        read_only_fields = ['id', 'titre', 'description', 'temps_preparation', 'temps_cuisson']


class FicheTechniqueSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle FicheTechnique.
    Gère la relation OneToOne avec Recette et inclut le calcul du coût TTC.
    """
    # Nested serialization de la recette pour la lecture
    recette_detail = RecetteSimpleSerializer(source='recette_fk', read_only=True)
    
    # Champ calculé pour le coût total TTC
    cout_total_ttc = serializers.SerializerMethodField()
    
    class Meta:
        model = FicheTechnique
        fields = [
            'recette_fk',
            'recette_detail',
            'nombre_portions',
            'cout_matiere_ht',
            'marge_appliquee',
            'cout_total_ttc',
            'validation_admin',
            'date_validation',
            'materiel_requis_json',
        ]
        read_only_fields = ['recette_detail', 'cout_total_ttc']
    
    def get_cout_total_ttc(self, obj):
        """
        Retourne le coût total TTC calculé.
        """
        return float(obj.cout_total_ttc) if obj.cout_total_ttc else 0.0
    
    def validate_recette_fk(self, value):
        """
        Validation pour s'assurer qu'une recette n'a pas déjà une fiche technique.
        """
        # Si c'est une création (pas d'instance)
        if not self.instance:
            if FicheTechnique.objects.filter(recette_fk=value).exists():
                raise serializers.ValidationError(
                    "Cette recette possède déjà une fiche technique."
                )
        return value
    
    def validate_nombre_portions(self, value):
        """
        Validation du nombre de portions (doit être positif).
        """
        if value <= 0:
            raise serializers.ValidationError("Le nombre de portions doit être supérieur à 0.")
        return value
    
    def validate_cout_matiere_ht(self, value):
        """
        Validation du coût matière (doit être positif ou nul).
        """
        if value < 0:
            raise serializers.ValidationError("Le coût matière ne peut pas être négatif.")
        return value
    
    def validate_marge_appliquee(self, value):
        """
        Validation de la marge (doit être entre 0 et 100%).
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("La marge doit être comprise entre 0 et 100%.")
        return value
    
    def validate(self, data):
        """
        Validation au niveau de l'objet.
        """
        # Si validation_admin est True, date_validation doit être fournie
        if data.get('validation_admin') and not data.get('date_validation'):
            raise serializers.ValidationError({
                'date_validation': "La date de validation est requise pour une fiche validée."
            })
        
        return data
