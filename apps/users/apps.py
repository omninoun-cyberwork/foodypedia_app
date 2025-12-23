# C:\Foodypedia\apps\users\apps.py (APRÈS CORRECTION)

from django.apps import AppConfig

class UsersConfig(AppConfig): # <-- Renommer la classe pour la cohérence
    default_auto_field = 'django.db.models.BigAutoField'
    # Le nom doit être le chemin complet que Django essaie d'importer :
    name = 'apps.users' 
    # Le label est souvent utilisé pour les migrations/références :
    label = 'users'