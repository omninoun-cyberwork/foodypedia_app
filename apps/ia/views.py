# ia/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from apps.recipes.models import Recette

# URL du Microservice IA (à adapter pour votre déploiement Docker)
IA_SERVICE_URL = "http://localhost:8001/generate-fiche-technique/"

class GenererFicheIA(APIView):
    """
    API Gateway : Reçoit une requête et l'envoie au Microservice IA pour traitement.
    """
    def post(self, request, format=None):
        recette_id = request.data.get('recette_id')
        
        try:
            recette = Recette.objects.get(pk=recette_id)
        except Recette.DoesNotExist:
            return Response({"error": "Recette non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Préparation des données pour l'IA
        # Récupération des ingrédients bruts (nécessite une fonction d'extraction)
        ingredients_list = [
            f"{q.quantite} {q.unite_mesure} de {q.ingredient_fk.nom_fr}" 
            for q in recette.quantiteingredient_set.all()
        ]

        # Structure du payload envoyé au Microservice FastAPI
        payload_ia = {
            "recette_id": recette.id,
            "titre": recette.titre,
            "ingredients_bruts": ingredients_list,
            # On peut ajouter ici les étapes brutes si elles sont disponibles
        }

        # 2. Appel du Microservice externe
        try:
            response_ia = requests.post(IA_SERVICE_URL, json=payload_ia, timeout=30)
            response_ia.raise_for_status() # Lève une exception si le statut est 4xx ou 5xx
            
            # Le Microservice retourne la Fiche Technique normalisée
            fiche_normale = response_ia.json()

            # NOTE: Dans la réalité, Django recevrait un statut "OK" et une tâche asynchrone (Celery)
            # mettrait à jour la DB. Ici, nous faisons un appel synchrone simple.
            
            return Response(fiche_normale, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            # Gérer les erreurs de connexion ou de l'IA elle-même
            return Response({"error": f"Erreur d'appel au service IA: {str(e)}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
#### 2. Création de `ia/urls.py`

#Permet d'atteindre cette vue depuis l'extérieur.

#```python
# ia/urls.py
from django.urls import path
from .views import GenererFicheIA

urlpatterns = [
    # Endpoint appelé par le Frontend ou n8n
    path('generer-fiche/', GenererFicheIA.as_view(), name='generer-fiche-ia'),
]