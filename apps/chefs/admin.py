# C:\Foodypedia\apps\chefs\admin.py

from django.contrib import admin
from .models import Chef

@admin.register(Chef)
class ChefAdmin(admin.ModelAdmin):
    # Correction de list_display avec les noms de champs actuels
    list_display = (
        'nom',           # Corrigé de 'nom_complet'
        'categorie', 
        'pays_d_origine', 
        'date_de_naissance', # Corrigé de 'date_naissance'
        'restaurant'
    ) 
    
    # Correction de list_filter avec le nom de champ actuel
    list_filter = ('categorie', 'pays_d_origine',) # Corrigé de 'pays_fk'
    
    search_fields = ('nom', 'restaurant')
    
    # Correction de raw_id_fields avec le nom de champ actuel
    raw_id_fields = ('pays_d_origine',) # Corrigé de 'pays_fk'
    
    ordering = ('nom',)