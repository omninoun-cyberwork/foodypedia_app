# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé héritant de AbstractUser.
    Permet d'ajouter des champs spécifiques au projet sans modifier 
    la base de données Django par défaut.
    """
    
    # Rôles spécifiques au projet
    ROLE_CHOICES = [
        ('CONTRIB', 'Contributeur (Saisie de Recettes)'),
        ('EXPERT', 'Expert (Validation Académique)'),
        ('ADMIN', 'Administrateur (Gestion du Site)'),
    ]

    # Champ pour définir le rôle du contributeur/utilisateur
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='CONTRIB',
        verbose_name="Rôle dans Foodypedia"
    )
    
    # Ajout d'un champ simple pour l'exemple
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Numéro de Téléphone"
    )

    class Meta:
        verbose_name = "Utilisateur Foodypedia"
        verbose_name_plural = "Utilisateurs Foodypedia"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"