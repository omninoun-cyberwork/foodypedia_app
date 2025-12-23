# microservice_ia/api.py (mise à jour)

from fastapi import FastAPI
from schemas import FicheInput, FicheOutput # Importer le Schéma
from logic import generer_fiche_normalisee # Importer la logique
import uvicorn

# Initialisation de l'API
app = FastAPI(title="Foodypedia AI Microservice")

@app.post("/generate-fiche-technique/", response_model=FicheOutput) # Spécifie le modèle de sortie
async def generate_fiche_technique(data: FicheInput):
    """
    Endpoint principal qui appelle la logique IA et retourne le résultat.
    """
    # L'appel direct à la fonction de logique
    resultat = generer_fiche_normalisee(data) 
    return resultat

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)