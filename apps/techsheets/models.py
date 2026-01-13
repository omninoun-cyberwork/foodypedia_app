from django.db import models
from apps.recipes.models import Recette
from apps.ingredients.models import Ingredient # Pour le lien Mercuriale

# -----------------------------------------------------
# 1. MERCURIALE (Prix des Ingrédients)
# -----------------------------------------------------

class IngredientPrice(models.Model):
    """
    Définit le coût standard d'un ingrédient pour les calculs de rentabilité.
    C'est la 'Mercuriale' du chef.
    """
    UNIT_CHOICES = [
        ('kg', 'Kilogramme'),
        ('l', 'Litre'),
        ('unit', 'Pièce/Unité'),
    ]

    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='price_info',
        verbose_name="Ingrédient"
    )
    average_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Prix Moyen HT (€)"
    )
    unit = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES, 
        default='kg', 
        verbose_name="Unité d'achat"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière MAJ")

    class Meta:
        verbose_name = "Prix Ingrédient (Mercuriale)"
        verbose_name_plural = "Mercuriale des Prix"
        ordering = ['ingredient__name']

    def __str__(self):
        return f"{self.average_price}€ / {self.get_unit_display()} pour {self.ingredient.name}"

# -----------------------------------------------------
# 2. FICHE TECHNIQUE (Coûts Recette)
# -----------------------------------------------------

class FicheTechnique(models.Model):
    """
    Contient les données normalisées (Coûts, Grammages, Validation) 
    associées à une recette.
    """
    recette_fk = models.OneToOneField(
        Recette,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Recette Associée",
        related_name="fiche_technique"
    )

    # Données financières et de rendement
    nombre_portions = models.IntegerField(
        default=1,
        verbose_name="Nombre de portions standard"
    )
    cout_matiere_ht = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Coût Matière HT (€)"
    )
    marge_appliquee = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=70.00, # Marge standard restauration ~70%
        verbose_name="Marge Commerciale (%)"
    )
    
    # Validation Académique
    validation_admin = models.BooleanField(
        default=False,
        verbose_name="Validée par un Expert"
    )
    date_validation = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de validation"
    )
    
    # Données spécifiques
    materiel_requis_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Matériel requis (IDs)"
    )

    class Meta:
        verbose_name = "Fiche Technique"
        verbose_name_plural = "Fiches Techniques"

    def __str__(self):
        return f"FT: {self.recette_fk.titre}"

    @property
    def cout_par_portion(self):
        if self.nombre_portions > 0:
            return self.cout_matiere_ht / self.nombre_portions
        return 0

    @property
    def prix_vente_suggere(self):
        """Calcul : Coût matière / (1 - Marge%)"""
        # Ex: Coût 3€, Marge 70% (0.7) -> 3 / (1 - 0.7) = 3 / 0.3 = 10€
        if self.marge_appliquee >= 100: return 0
        coeff = 1 - (self.marge_appliquee / 100)
        if coeff > 0:
            return self.cout_matiere_ht / coeff
        return 0

# -----------------------------------------------------
# 3. DICTIONNAIRE TECHNIQUE (Encyclopédie)
# -----------------------------------------------------

class Technique(models.Model):
    """
    Définit un terme ou une technique culinaire (ex: 'Blanchir', 'Abaisser').
    Source: Dictionnaire JSON importé.
    """
    DOMAINE_CHOICES = [
        ('Cuisine', 'Cuisine'),
        ('Pâtisserie', 'Pâtisserie'),
        ('Boulangerie', 'Boulangerie'),
        ('Autre', 'Autre'),
    ]

    nom = models.CharField(max_length=200, unique=True, verbose_name="Terme / Technique")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    domaine = models.CharField(max_length=50, choices=DOMAINE_CHOICES, default='Cuisine')
    
    definition = models.TextField(verbose_name="Définition")
    
    # Champs riches (Listes stockées en JSON)
    objectif = models.JSONField(default=list, blank=True, verbose_name="Objectifs")
    principe = models.TextField(blank=True, verbose_name="Principe scientifique/technique")
    exemples = models.JSONField(default=dict, blank=True, verbose_name="Exemples d'application")
    erreurs_frequentes = models.JSONField(default=list, blank=True, verbose_name="Erreurs fréquentes")
    niveau = models.JSONField(default=list, blank=True, verbose_name="Niveaux (CAP, Bac Pro...)")
    
    # Média
    image = models.ImageField(upload_to="techniques/", null=True, blank=True, verbose_name="Illustration")

    class Meta:
        verbose_name = "Technique Culinaire"
        verbose_name_plural = "Dictionnaire Technique"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)