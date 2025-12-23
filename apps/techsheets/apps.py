# C:\Foodypedia\apps\techsheets\apps.py (APRÈS CORRECTION)

from django.apps import AppConfig

# Renommer la classe pour la cohérence
class TechsheetsConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    # Le nom doit refléter le chemin complet :
    name = 'apps.techsheets' 
    # Le label est l'ancien nom court (ou un nouveau)
    label = 'techsheets'