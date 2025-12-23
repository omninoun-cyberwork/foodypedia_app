from django.contrib import admin
from .models import FicheTechnique, IngredientPrice
from .services import CostCalculatorService

# -----------------------------------------------------
# 1. MERCURIALE (Prix)
# -----------------------------------------------------

@admin.register(IngredientPrice)
class IngredientPriceAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'average_price', 'unit', 'updated_at')
    search_fields = ('ingredient__name',)
    list_filter = ('unit',)
    list_editable = ('average_price', 'unit') # Modification rapide en liste
    autocomplete_fields = ['ingredient']

# -----------------------------------------------------
# 2. FICHE TECHNIQUE
# -----------------------------------------------------

@admin.register(FicheTechnique)
class FicheTechniqueAdmin(admin.ModelAdmin):
    list_display = ('get_recette_titre', 'nombre_portions', 'cout_matiere_ht', 'cout_par_portion', 'prix_vente_suggere')
    readonly_fields = ('cout_par_portion', 'prix_vente_suggere') # Champs calculés
    actions = ['recalculate_costs']

    fieldsets = (
        ('Liaison', {
            'fields': ('recette_fk', 'validation_admin', 'date_validation') 
        }),
        ('Paramètres', {
            'fields': ('nombre_portions', 'marge_appliquee'),
        }),
        ('Résultats Financiers', {
            'fields': ('cout_matiere_ht', 'cout_par_portion', 'prix_vente_suggere'),
            'description': "Le coût matière est calculé automatiquement via l'action 'Recalculer'."
        }),
    )

    @admin.display(description='Recette')
    def get_recette_titre(self, obj):
        return obj.recette_fk.titre 

    @admin.action(description='Recalculer le Coût Matière (via Mercuriale)')
    def recalculate_costs(self, request, queryset):
        service = CostCalculatorService()
        count = 0
        for ft in queryset:
            # 1. Calcul du coût total
            new_cost = service.calculate_recipe_cost(ft.recette_fk)
            # 2. Mise à jour de la fiche
            ft.cout_matiere_ht = new_cost
            ft.save()
            count += 1
        
        self.message_user(request, f"{count} fiches techniques recalculées avec succès.")