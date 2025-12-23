from django.contrib import admin
from .models import (
    Ingredient, IngredientCategory, FunctionalCategory, 
    IngredientFamily, Label, CulinaryUse, IngredientImage
)

class IngredientImageInline(admin.TabularInline):
    model = IngredientImage
    extra = 1

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'scientific_name', 'created_at')
    list_filter = ('category', 'functional_categories', 'labels')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [IngredientImageInline]
    fieldsets = (
        ("Identification", {
            "fields": ("name", "slug", "scientific_name", "category", "functional_categories", "family")
        }),
        ("Origine & Labels", {
            "fields": ("origins_countries", "labels", "seasonality")
        }),
        ("Profil", {
            "fields": ("flavor_profile", "texture", "culinary_uses")
        }),
        ("Guides", {
            "classes": ("collapse",),
            "fields": ("buying_guide", "storage_guide", "prep_guide", "nutrition_info", "allergens")
        }),
        ("Données Spécifiques", {
            "fields": ("specific_data",)
        }),
        ("Media", {
            "fields": ("main_image",)
        }),
    )

@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(FunctionalCategory)
class FunctionalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(IngredientFamily)
class IngredientFamilyAdmin(admin.ModelAdmin):
    pass

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    pass

@admin.register(CulinaryUse)
class CulinaryUseAdmin(admin.ModelAdmin):
    pass
