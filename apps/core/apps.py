# C:\Foodypedia\apps\core\apps.py

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # CORRECTION : Le nom doit refléter le chemin complet depuis la racine du projet
    name = 'apps.core' # <--- CORRIGÉ
    label = 'core_app' # Optionnel, pour éviter les conflits si vous aviez d'autres 'core'