# C:\Foodypedia\apps\chefs\serializers.py

from rest_framework import serializers
from .models import Chef
from apps.atlas.models import Pays


class PaysSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Pays (utilisé en nested dans ChefSerializer).
    """
    class Meta:
        model = Pays
        fields = ['id', 'nom_fr', 'continent']
        read_only_fields = ['id']


class ChefSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour le modèle Chef.
    Inclut la sérialisation nested du pays d'origine.
    """
    # Nested serialization pour la lecture (GET)
    pays_d_origine_detail = PaysSerializer(source='pays_d_origine', read_only=True)
    
    # Champ pour l'écriture (POST/PUT/PATCH) - accepte l'ID du pays
    pays_d_origine = serializers.PrimaryKeyRelatedField(
        queryset=Pays.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Affichage lisible de la catégorie
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    
    class Meta:
        model = Chef
        fields = [
            'id',
            'nom',
            'pays_d_origine',
            'pays_d_origine_detail',
            'email',
            'website',
            'categorie',
            'categorie_display',
            'restaurant',
            'date_de_naissance',
            'date_de_deces',
        ]
        read_only_fields = ['id', 'categorie_display', 'pays_d_origine_detail']
    
    def validate_email(self, value):
        """
        Validation personnalisée pour l'email.
        """
        if value:
            # Vérifier l'unicité de l'email (sauf pour l'instance actuelle en cas d'update)
            queryset = Chef.objects.filter(email=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Un chef avec cet email existe déjà.")
        return value
    
    def validate(self, data):
        """
        Validation au niveau de l'objet.
        """
        # Vérifier que la date de décès est postérieure à la date de naissance
        date_naissance = data.get('date_de_naissance')
        date_deces = data.get('date_de_deces')
        
        if date_naissance and date_deces:
            if date_deces < date_naissance:
                raise serializers.ValidationError({
                    'date_de_deces': "La date de décès ne peut pas être antérieure à la date de naissance."
                })
        
        return data
