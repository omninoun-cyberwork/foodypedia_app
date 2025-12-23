# C:\Foodypedia\apps\recipes\admin.py

from django.contrib import admin
from .models import Recette, Technique, QuantiteIngredient, RecipeCategory

# -----------------------------------------------------
# Enregistrement des modèles de RECIPES
# -----------------------------------------------------

class QuantiteIngredientInline(admin.TabularInline):
    """
    Permet d'ajouter les ingrédients directement dans la fiche recette.
    Gère Ingrédients Bruts OU Sous-Recettes.
    """
    model = QuantiteIngredient
    extra = 1
    fk_name = 'recette' # Nécessaire car il y a deux FKs vers Recette
    autocomplete_fields = ['ingredient', 'sub_recipe']

@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'category', 'temps_preparation', 'temps_cuisson', 'date_creation')
    search_fields = ('titre', 'description')
    list_filter = ('category', 'auteurs')
    filter_horizontal = ('auteurs', 'techniques_cles')
    inlines = [QuantiteIngredientInline]
    prepopulated_fields = {"slug": ("titre",)}

@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(QuantiteIngredient)
class QuantiteIngredientAdmin(admin.ModelAdmin):
    list_display = ('recette', 'display_content', 'quantite', 'unite')
    list_filter = ('unite',)
    search_fields = ('recette__titre', 'ingredient__name', 'sub_recipe__titre')
    autocomplete_fields = ['recette', 'ingredient', 'sub_recipe']

    def display_content(self, obj):
        if obj.ingredient:
            return f"Ingrédient: {obj.ingredient.name}"
        elif obj.sub_recipe:
            return f"Sous-recette: {obj.sub_recipe.titre}"
        return "-"
    display_content.short_description = "Contenu"