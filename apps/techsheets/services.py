from decimal import Decimal
from apps.recipes.models import Recette, QuantiteIngredient
from apps.techsheets.models import IngredientPrice, FicheTechnique

class CostCalculatorService:
    """
    Service dédié au calcul du coût matière des recettes.
    Gère la récursion (Recette -> Sous-Recette -> Ingrédient).
    """

    def calculate_recipe_cost(self, recipe: Recette) -> Decimal:
        """
        Calcule le coût total HT des ingrédients d'une recette.
        """
        total_cost = Decimal('0.00')

        # Récupérer toutes les lignes d'ingrédients de la recette
        # Optimisation : prefetch pour éviter N requêtes
        lignes = recipe.lignes_ingredients.select_related('ingredient__price_info', 'sub_recipe').all()

        for ligne in lignes:
            cost_line = self._calculate_line_cost(ligne)
            total_cost += cost_line

        return total_cost

    def _calculate_line_cost(self, ligne: QuantiteIngredient) -> Decimal:
        """Coût d'une ligne (Ingrédient OU Sous-recette)"""
        qty = Decimal(str(ligne.quantite)) if ligne.quantite else Decimal('0')
        
        # CAS 1 : C'est un Ingrédient Brut
        if ligne.ingredient:
            return self._get_ingredient_cost(ligne.ingredient, qty, ligne.unite)
        
        # CAS 2 : C'est une Sous-Recette
        elif ligne.sub_recipe:
            return self._get_sub_recipe_cost(ligne.sub_recipe, qty, ligne.unite)

        return Decimal('0.00')

    def _get_ingredient_cost(self, ingredient, qty: Decimal, unit: str) -> Decimal:
        """
        Récupère le prix dans la Mercuriale et calcule le montant.
        NOTE: Simplification des conversions d'unités pour cette version (1L = 1kg = 1000g).
        """
        try:
            price_info = ingredient.price_info
        except IngredientPrice.DoesNotExist:
            # Si pas de prix, on retourne 0 (ou on pourrait logguer un warning)
            return Decimal('0.00')

        base_price = price_info.average_price # Prix au kg ou à l'unité
        base_unit = price_info.unit # 'kg', 'l', 'unit'

        # Logique de conversion simple
        factor = Decimal('1')

        # Si achat au kg et utilisation en g -> /1000
        if base_unit in ['kg', 'l'] and unit.lower() in ['g', 'ml', 'gr']:
            factor = Decimal('0.001')
        
        # Si achat au kg et utilisation en kg -> 1
        # Si achat unité et utilisation unité -> 1

        cost = base_price * qty * factor
        return cost

    def _get_sub_recipe_cost(self, sub_recipe: Recette, qty: Decimal, unit: str) -> Decimal:
        """
        Calcule le coût d'une sous-recette utilisée.
        Il faut connaître le coût total de la sous-recette ET son rendement (nb portions ou poids total).
        Pour simplifier ici : on considère que la quantité demandée est un % du totals.
        MAIS pour être précis, il faudrait que FicheTechnique stocke le "Poids Total" de la recette.
        
        APPROCHE SIMPLIFIÉE V1 :
        On considère que 'qty' représente le nombre de portions si l'unité est 'portion' ou 'uni'.
        Ou on recalcule tout dynamiquement.
        """
        # 1. Calculer le coût total de fabrication de la sous-recette (Récursion)
        # Idéalement, on lit le cache dans FicheTechnique pour éviter boucle infinie si stocké
        # Mais pour être "temps réel", on recalcule.
        total_sub_cost = self.calculate_recipe_cost(sub_recipe)

        # 2. Ramener à la quantité utilisée
        # Pour faire simple : Si on utilise '1' unité, on prend le coût total / nb portions
        # Cette partie nécessiterait un champ "Poids Total" sur la Recette/FicheTechnique pour être exacte en grammes.
        
        try:
            ft = sub_recipe.fiche_technique
            nb_portions = ft.nombre_portions
        except FicheTechnique.DoesNotExist:
            nb_portions = 1
        
        if nb_portions == 0: nb_portions = 1
        
        cost_per_portion = total_sub_cost / Decimal(nb_portions)
        
        # Si on demande en "g", c'est complexe sans poids total.
        # On assume ici que qty = nombre de portions (ex: 1 Fond de tarte)
        
        return cost_per_portion * qty
