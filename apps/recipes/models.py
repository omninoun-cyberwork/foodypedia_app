# C:\Foodypedia\apps\recipes\models.py (REFONTE 2.0)

from django.db import models
from django.conf import settings # Importation pour settings.AUTH_USER_MODEL
from apps.ingredients.models import Ingredient # Le nouveau modèle Riche

# -----------------------------------------------------
# 1. CATÉGORIES DE RECETTES (Classification)
# -----------------------------------------------------

class RecipeCategory(models.Model):
    """
    Catégories hierarchiques pour les recettes.
    Niveau 1 : Cuisine / Pâtisserie / Boulangerie
    Niveau 2 : Sauces / Entrées / Viandes / Bases
    """
    name = models.CharField(max_length=100, verbose_name="Nom")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name="Catégorie Parente")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Catégorie de Recette"
        verbose_name_plural = "Catégories de Recettes"
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

# -----------------------------------------------------
# 2. TECHNIQUES
# -----------------------------------------------------

class Technique(models.Model):
    """Représente une technique de cuisine (ex: 'ciseler', 'déglacer')."""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Technique"
        verbose_name_plural = "Techniques"

# -----------------------------------------------------
# 3. RECETTE (Modèle principal)
# -----------------------------------------------------

class Recette(models.Model):
    """Modèle principal d'une recette."""
    titre = models.CharField(max_length=200)
    slug = models.SlugField(blank=True) # Pour SEO futur
    description = models.TextField()
    
    # Classification
    category = models.ForeignKey(
        RecipeCategory, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        verbose_name="Catégorie",
        related_name="recettes"
    )
    
    # Temps
    temps_preparation = models.DurationField(null=True, blank=True)
    temps_cuisson = models.DurationField(null=True, blank=True)

    # Auteurs (Contribution)
    auteurs = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='recettes_contribuees', 
        verbose_name="Auteurs / Contributeurs"
    )

    # Ingrédients (via le modèle intermédiaire QuantiteIngredient)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='QuantiteIngredient',
        through_fields=('recette', 'ingredient'),
        related_name='recettes_utilisees', 
        verbose_name="Ingrédients requis"
    )

    # Sous-recettes (Recettes utilisées comme ingrédients)
    sub_recipes = models.ManyToManyField(
        'self',
        through='QuantiteIngredient',
        through_fields=('recette', 'sub_recipe'),
        symmetrical=False,
        related_name='super_recipes', 
        verbose_name="Sous-recettes requises"
    )

    # Techniques
    techniques_cles = models.ManyToManyField(
        Technique,
        related_name='recettes_utilisant_technique', 
        verbose_name="Techniques clés"
    )
    
    instructions = models.TextField(blank=True, verbose_name="Instructions de préparation")
    notes_chef = models.TextField(blank=True, verbose_name="Notes du Chef / Astuces")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ('titre',)


# -----------------------------------------------------
# 4. QUANTITE INGRÉDIENT (Liaison & Récursion)
# -----------------------------------------------------

class QuantiteIngredient(models.Model):
    """
    Modèle pivot 'Ligne de Recette'.
    Permet de lier une Recette parente à :
    - SOIT un Ingrédient Brut (ex: oeuf, farine)
    - SOIT une Sous-Recette (ex: Pâte Feuilletée, Bouillon de Volaille)
    """
    
    # La Recette "Contenant" (Qui contient cet ingrédient)
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name='lignes_ingredients')
    
    # Option A : Ingrédient Brut
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.PROTECT, 
        null=True, blank=True,
        verbose_name="Ingrédient Brut"
    )
    
    # Option B : Sous-Recette (Récursion)
    sub_recipe = models.ForeignKey(
        Recette, 
        on_delete=models.PROTECT, 
        null=True, blank=True,
        related_name='utilisations_comme_ingredient',
        verbose_name="Sous-Recette (ex: Sauce, Pâte)"
    )
    
    quantite = models.FloatField(null=True, blank=True) # Null autorisé pour "QS" (Quantité Suffisante)
    unite = models.CharField(max_length=50, blank=True) # Ex: 'g', 'ml', 'cl', 'pièce'
    note = models.CharField(max_length=200, blank=True, verbose_name="Note (ex: coupé en dés)")
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.ingredient and not self.sub_recipe:
            raise ValidationError("Une ligne de recette doit contenir un Ingrédient OU une Sous-Recette.")
        if self.ingredient and self.sub_recipe:
            raise ValidationError("Impossible de sélectionner à la fois un Ingrédient et une Sous-Recette.")

    def __str__(self):
        nom = self.ingredient.name if self.ingredient else f"Recette: {self.sub_recipe.titre}"
        return f"{self.quantite or '?'} {self.unite} de {nom}"

    class Meta:
        verbose_name = "Ligne d'ingrédient"
        verbose_name_plural = "Lignes d'ingrédients"
        ordering = ['id']