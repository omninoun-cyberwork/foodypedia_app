from django.urls import path
from .views import GenererFicheIA

urlpatterns = [
    # Endpoint appelé par le Frontend ou n8n
    path('generer-fiche/', GenererFicheIA.as_view(), name='generer-fiche-ia'),
]