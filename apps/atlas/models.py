# C:\Foodypedia\apps\atlas\models.py (Source de Vérité pour les Références)

from django.db import models

# --- Modèle 1 : Pays (Atlas Mondial) ---
class Pays(models.Model):
    """
    Représente un pays ou une région géographique pour l'Atlas Mondial de la Cuisine.
    Sera utilisé comme clé étrangère dans d'autres modèles (ex: Chef, Recette).
    """
    nom_fr = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du Pays (français)"
    )
    continent = models.CharField(
        max_length=50,
        verbose_name="Continent"
    )
    plats_phares_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Plats emblématiques (JSON)"
    )

    class Meta:
        verbose_name = "Pays (Atlas)"
        verbose_name_plural = "Pays (Atlas)"
        ordering = ['nom_fr']

    def __str__(self):
        return self.nom_fr

# --- Modèle 2 : Materiel & Équipement ---
class Materiel(models.Model):
    """
    Catalogue descriptif de l'équipement professionnel (ustensiles, machines).
    """
    CATEGORIES = [
        ('U', 'Ustensile/Petit Matériel'),
        ('M', 'Machine de Cuisson/Froid'),
        ('P', 'Préparation Spécifique'),
    ]

    nom_fr = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Nom de l'équipement"
    )
    description_courte = models.TextField(
        verbose_name="Fonction principale"
    )
    categorie = models.CharField(
        max_length=1,
        choices=CATEGORIES,
        default='U',
        verbose_name="Catégorie"
    )
    maintenance_checklist = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Checklist d'entretien"
    )

    class Meta:
        verbose_name = "Matériel/Équipement"
        verbose_name_plural = "Catalogue Matériel"
        ordering = ['nom_fr']

    def __str__(self):
        return f"{self.nom_fr} ({self.get_categorie_display()})"

# --- Modèle 3 : Glossaire & Terminologie ---
class Glossaire(models.Model):
    """
    Index alphabétique de tous les termes techniques et définitions.
    """
    TYPES = [
        ('V', 'Verbe d\'Action'),
        ('N', 'Nom de Produit/Ustensile'),
        ('A', 'Adjectif/Terme d\'État'),
    ]

    terme = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Terme technique"
    )
    definition = models.TextField(
        verbose_name="Définition académique"
    )
    type_terme = models.CharField(
        max_length=1,
        choices=TYPES,
        default='N',
        verbose_name="Type de terme"
    )
    
    class Meta:
        verbose_name = "Terme de Glossaire"
        verbose_name_plural = "Glossaire Terminologique"
        ordering = ['terme']

    def __str__(self):
        return f"[{self.get_type_terme_display()}] {self.terme}"