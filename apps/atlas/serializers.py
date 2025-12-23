# C:\Foodypedia\apps\atlas\serializers.py

from rest_framework import serializers
from .models import Pays, Materiel, Glossaire


class PaysSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Pays (Atlas Mondial).
    Utilisé pour classer les recettes et chefs par origine géographique.
    """
    # Compteur de chefs et recettes liés (read-only)
    nombre_chefs = serializers.SerializerMethodField()
    
    class Meta:
        model = Pays
        fields = [
            'id',
            'nom_fr',
            'continent',
            'plats_phares_json',
            'nombre_chefs',
        ]
        read_only_fields = ['id', 'nombre_chefs']
    
    def get_nombre_chefs(self, obj):
        """
        Retourne le nombre de chefs associés à ce pays.
        """
        return obj.chef_set.count() if hasattr(obj, 'chef_set') else 0
    
    def validate_nom_fr(self, value):
        """
        Validation de l'unicité du nom de pays.
        """
        queryset = Pays.objects.filter(nom_fr=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Un pays avec ce nom existe déjà.")
        return value


class MaterielSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Materiel (Catalogue d'équipement).
    Accessible en lecture publique pour consultation.
    """
    # Affichage lisible de la catégorie
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    
    class Meta:
        model = Materiel
        fields = [
            'id',
            'nom_fr',
            'description_courte',
            'categorie',
            'categorie_display',
            'maintenance_checklist',
        ]
        read_only_fields = ['id', 'categorie_display']
    
    def validate_nom_fr(self, value):
        """
        Validation de l'unicité du nom d'équipement.
        """
        queryset = Materiel.objects.filter(nom_fr=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Un équipement avec ce nom existe déjà.")
        return value


class GlossaireSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Glossaire (Terminologie culinaire).
    Accessible en lecture publique pour consultation.
    """
    # Affichage lisible du type de terme
    type_terme_display = serializers.CharField(source='get_type_terme_display', read_only=True)
    
    class Meta:
        model = Glossaire
        fields = [
            'id',
            'terme',
            'definition',
            'type_terme',
            'type_terme_display',
        ]
        read_only_fields = ['id', 'type_terme_display']
    
    def validate_terme(self, value):
        """
        Validation de l'unicité du terme.
        """
        queryset = Glossaire.objects.filter(terme=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ce terme existe déjà dans le glossaire.")
        return value
