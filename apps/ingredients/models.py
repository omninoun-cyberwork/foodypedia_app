from django.db import models
from apps.atlas.models import Pays, Glossaire  # Intégration Atlas

# -------------------------------------------------------------------------
# 1. Catégories & Classifications
# -------------------------------------------------------------------------

class IngredientCategory(models.Model):
    """
    Catégorie principale (Nature du produit).
    Ex: Épice, Viande bovine, Poisson, Légume, Céréale...
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône (classe CSS/SVG)")

    class Meta:
        verbose_name = "Catégorie Principale"
        verbose_name_plural = "Catégories Principales"
        ordering = ['name']

    def __str__(self):
        return self.name


class FunctionalCategory(models.Model):
    """
    Catégorie fonctionnelle (Usage/Rôle).
    Ex: Pâtisserie, Féculent, Aromatique, Liant, Texturant...
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Catégorie Fonctionnelle"
        verbose_name_plural = "Catégories Fonctionnelles"
        ordering = ['name']

    def __str__(self):
        return self.name


class IngredientFamily(models.Model):
    """
    Famille scientifique ou culinaire.
    Ex: Solanacées (Tomate), Citriques (Citron), Poissons bleus...
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")

    class Meta:
        verbose_name = "Famille d'ingrédient"
        verbose_name_plural = "Familles d'ingrédients"

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------
# 2. Métadonnées (Labels, Usages, Origines spécifiques)
# -------------------------------------------------------------------------

class Label(models.Model):
    """Labels qualité : Bio, AOP, IGP, Halal, Label Rouge..."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    icon = models.ImageField(upload_to="labels/", blank=True, null=True, verbose_name="Logo")

    class Meta:
        verbose_name = "Label / Certification"
        verbose_name_plural = "Labels / Certifications"

    def __str__(self):
        return self.name


class CulinaryUse(models.Model):
    """Usages culinaires types : Marinade, Infusion, Rôti, Poché..."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Usage")

    class Meta:
        verbose_name = "Usage Culinaire"
        verbose_name_plural = "Usages Culinaires"

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------
# 3. Modèle Principal : INGRÉDIENT
# -------------------------------------------------------------------------

class Ingredient(models.Model):
    """
    Modèle central pour tous les ingrédients (Vision Wiki).
    """
    # --- Identification ---
    name = models.CharField(max_length=200, unique=True, verbose_name="Nom principal")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    scientific_name = models.CharField(max_length=200, blank=True, verbose_name="Nom scientifique")
    
    # --- Référence Académique (Fusion Gemini) ---
    glossary_term = models.ForeignKey(
        Glossaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingredients_lies",
        verbose_name="Terme du Glossaire (Atlas)"
    )
    
    description = models.TextField(verbose_name="Description générale")

    # --- Catégorisation ---
    category = models.ForeignKey(
        IngredientCategory, 
        on_delete=models.PROTECT, 
        related_name="ingredients",
        verbose_name="Catégorie Principale"
    )
    functional_categories = models.ManyToManyField(
        FunctionalCategory, 
        blank=True,
        verbose_name="Catégories Fonctionnelles",
        related_name="ingredients"
    )
    family = models.ForeignKey(
        IngredientFamily, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        verbose_name="Famille"
    )

    # --- Origine & Qualité ---
    # Liaison avec l'Atlas pour les pays producteurs majeurs
    origins_countries = models.ManyToManyField(
        Pays,
        blank=True,
        verbose_name="Pays d'origine majeurs",
        related_name="ingredients_originaires"
    )
    labels = models.ManyToManyField(Label, blank=True, verbose_name="Labels compatibles")
    seasonality = models.CharField(max_length=100, blank=True, verbose_name="Saisonnalité")

    # --- Profil Sensoriel & Technique ---
    flavor_profile = models.TextField(blank=True, verbose_name="Profil aromatique/Saveur")
    texture = models.TextField(blank=True, verbose_name="Texture")
    
    # --- Données Riches (Sections Wiki) ---
    buying_guide = models.TextField(blank=True, verbose_name="Guide d'achat")
    storage_guide = models.TextField(blank=True, verbose_name="Guide de conservation")
    prep_guide = models.TextField(blank=True, verbose_name="Conseils de préparation")
    nutrition_info = models.TextField(blank=True, verbose_name="Infos nutritionnelles")
    allergens = models.TextField(blank=True, verbose_name="Allergènes")
    
    culinary_uses = models.ManyToManyField(CulinaryUse, blank=True, verbose_name="Usages recommandés")

    # --- MAGIE : Données Spécifiques (JSON) ---
    # Permet de stocker : morceaux (viande), zone pêche (poisson), variété (légume)...
    specific_data = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name="Données spécifiques (JSON)"
    )
    
    # Tags flexibles pour n8n/IA
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tags n8n/IA"
    )

    # --- Média ---
    main_image = models.ImageField(upload_to="ingredients/main/", blank=True, null=True, verbose_name="Image principale")
    image_filename = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Nom du fichier image (Référence)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ingrédient"
        verbose_name_plural = "Ingrédients"
        ordering = ['name']

    def __str__(self):
        return self.name


# -------------------------------------------------------------------------
# 4. Images Supplémentaires (Variations)
# -------------------------------------------------------------------------

class IngredientImage(models.Model):
    """
    Images additionnelles pour un ingrédient.
    Ex: Anis (Graine) vs Anis (Poudre), Poisson (Entier) vs Poisson (Filet)
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="ingredients/variations/")
    caption = models.CharField(max_length=100, blank=True, verbose_name="Légende (ex: Moulu, Entier)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['order']
        verbose_name = "Image additionnelle"
        verbose_name_plural = "Galerie Images"

    def __str__(self):
        return f"Image de {self.ingredient.name} ({self.caption})"
