# accounts/serializers.py

from rest_framework import serializers
from ..models import CustomUser

# --- 1. Serializer pour l'enregistrement/inscription ---
class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé pour créer un nouvel utilisateur. 
    Gère la validation des données d'inscription.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True) # Champ de confirmation

    class Meta:
        model = CustomUser
        # Champs que l'utilisateur peut envoyer pour s'inscrire
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        """Vérifie que les deux mots de passe correspondent."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        """Méthode pour créer et sauvegarder l'utilisateur avec un mot de passe haché."""
        # Retire le champ de confirmation pour ne pas l'enregistrer
        validated_data.pop('password2') 
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            # Définir le rôle par défaut si non fourni, ou utiliser la valeur validée
            role=validated_data.get('role', 'CONTRIB'), 
            password=validated_data['password']
        )
        return user

# --- 2. Serializer pour le profil (lecture seule) ---
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer standard pour afficher les données de profil.
    """
    class Meta:
        model = CustomUser
        # Champs que l'API renverra au Frontend
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'is_staff', 'date_joined')
        read_only_fields = ('username', 'email', 'date_joined')