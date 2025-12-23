# microservice_ia/logic.py

from schemas import FicheInput, FicheData, FicheOutput
import time
import random

def generer_fiche_normalisee(data: FicheInput) -> FicheOutput:
    """
    Simule l'appel au LLM et le calcul de la Fiche Technique.
    """
    print(f"[{time.strftime('%H:%M:%S')}] Début du traitement IA pour {data.titre}...")
    
    # 1. Nettoyage et Normalisation des ingrédients (simulé)
    # Dans un vrai cas : ici, on normaliserait "cuillère à café" en 'cc', "farine T45" en 'Farine de blé', etc.
    normalisation_couts = random.uniform(8.0, 20.0) # Simulation de l'estimation de coût

    # 2. Simulation de la durée du LLM
    time.sleep(1.5) # Simule le temps de réponse d'une requête LLM

    # 3. Construction des données de sortie
    donnees_generes = FicheData(
        nombre_portions=random.choice([2, 4, 6]),
        cout_matiere_ht=round(normalisation_couts, 2), 
        marge_appliquee=random.choice([20.00, 25.00, 30.00]),
        # Liste d'IDs d'ustensiles (qui existent dans le catalogue 'core')
        materiel_requis_json=random.sample([1, 5, 12, 22, 30], 3)
    )

    return FicheOutput(
        recette_id=data.recette_id,
        statut_generation="SUCCES",
        message="Fiche technique normalisée et coûts estimés avec succès.",
        donnees_fiche=donnees_generes
    )