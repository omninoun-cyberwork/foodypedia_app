# microservice_ia/schemas.py
from pydantic import BaseModel
from typing import List, Optional

# Schéma d'entrée (ce que Django envoie)
class FicheInput(BaseModel):
    recette_id: int
    titre: str
    ingredients_bruts: List[str]
    # Les contraintes pour le LLM
    contraintes_json: Optional[dict] = None

# Schéma des données générées par l'IA (le coeur de la Fiche Technique)
class FicheData(BaseModel):
    nombre_portions: int
    cout_matiere_ht: float
    marge_appliquee: float
    materiel_requis_json: List[int]

# Schéma de sortie (la réponse finale du service IA)
class FicheOutput(BaseModel):
    recette_id: int
    statut_generation: str
    message: str
    donnees_fiche: FicheData