from django.apps import AppConfig

# Si la classe s'appelait IaConfig, vous n'avez pas besoin de la renommer.
class IaConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    # CORRECTION : Le nom doit refléter le chemin complet :
    name = 'apps.ia' 
    # Le label est souvent utilisé pour les migrations/références :
    label = 'ia_app'