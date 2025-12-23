from decimal import Decimal
from django.test import TestCase
from apps.ingredients.models import Ingredient, IngredientCategory
from apps.recipes.models import Recette, QuantiteIngredient, RecipeCategory
from apps.techsheets.models import IngredientPrice, FicheTechnique
from apps.techsheets.services import CostCalculatorService

class CostCalculatorTests(TestCase):
    def setUp(self):
        # 1. Catégories requises
        self.cat_ing = IngredientCategory.objects.create(name="TestCat", slug="test-cat")
        self.cat_rec = RecipeCategory.objects.create(name="TestRecCat", slug="test-rec-cat")
        
        # 2. Ingrédient : Beurre (10€ / kg)
        self.beurre = Ingredient.objects.create(name="Beurre", slug="beurre", category=self.cat_ing)
        self.price_beurre = IngredientPrice.objects.create(
            ingredient=self.beurre,
            average_price=Decimal('10.00'),
            unit='kg'
        )

        # 3. Ingrédient : Farine (2€ / kg)
        self.farine = Ingredient.objects.create(name="Farine", slug="farine", category=self.cat_ing)
        self.price_farine = IngredientPrice.objects.create(
            ingredient=self.farine,
            average_price=Decimal('2.00'),
            unit='kg'
        )

        # 4. Service
        self.service = CostCalculatorService()

    def test_simple_recipe_cost(self):
        """Test d'une recette simple (Pâte sablée)"""
        # Recette: 500g Farine + 250g Beurre
        pate = Recette.objects.create(titre="Pâte Sablée", category=self.cat_rec)
        QuantiteIngredient.objects.create(recette=pate, ingredient=self.farine, quantite=500, unite='g')
        QuantiteIngredient.objects.create(recette=pate, ingredient=self.beurre, quantite=250, unite='g')

        # Calcul attendu :
        # Farine: 0.5kg * 2€ = 1.00€
        # Beurre: 0.25kg * 10€ = 2.50€
        # Total = 3.50€
        
        cost = self.service.calculate_recipe_cost(pate)
        self.assertEqual(cost, Decimal('3.50'))

    def test_recursive_recipe_cost(self):
        """Test d'une recette utilisant une sous-recette"""
        # 1. Sous-Recette: Pâte (Coût 3.50€ pour 1 portion par défaut)
        pate_sub = Recette.objects.create(titre="Sous-Recette Pâte", category=self.cat_rec)
        QuantiteIngredient.objects.create(recette=pate_sub, ingredient=self.farine, quantite=500, unite='g')
        QuantiteIngredient.objects.create(recette=pate_sub, ingredient=self.beurre, quantite=250, unite='g')
        
        # Créer la fiche technique pour définir le rendement (1 portion = le tout)
        FicheTechnique.objects.create(recette_fk=pate_sub, nombre_portions=1)

        # 2. Recette Finale: Tarte (Utilise 1 portion de Pâte + 100g Beurre extra)
        tarte = Recette.objects.create(titre="Tarte au Beurre", category=self.cat_rec)
        
        # Ajout de la sous-recette (1 portion)
        QuantiteIngredient.objects.create(recette=tarte, sub_recipe=pate_sub, quantite=1, unite='port')
        
        # Ajout ingrédient extra (100g beurre = 1€)
        QuantiteIngredient.objects.create(recette=tarte, ingredient=self.beurre, quantite=100, unite='g')

        # Calcul attendu :
        # Sous-recette (3.50€) + Beurre (1.00€) = 4.50€
        cost = self.service.calculate_recipe_cost(tarte)
        self.assertEqual(cost, Decimal('4.50'))
