# C:\Foodypedia\apps\recipes\tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Technique, Ingredient, QuantiteIngredient, Recette

User = get_user_model()


class TechniqueAPITestCase(TestCase):
    """
    Tests pour l'API REST Technique.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        self.url_list = '/api/v1/recipes/techniques/'
        
        self.technique = Technique.objects.create(
            nom='Blanchir',
            description='Plonger dans l\'eau bouillante'
        )
    
    def test_list_techniques_public_access(self):
        """Test: Liste des techniques accessible publiquement."""
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_technique_requires_auth(self):
        """Test: Création de technique requiert l'authentification."""
        data = {'nom': 'Ciseler', 'description': 'Couper finement'}
        
        response = self.client_public.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_search_technique(self):
        """Test: Recherche de technique fonctionne."""
        response = self.client_public.get(f'{self.url_list}?search=Blanchir')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class IngredientAPITestCase(TestCase):
    """
    Tests pour l'API REST Ingredient.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        self.url_list = '/api/v1/recipes/ingredients/'
        
        self.ingredient = Ingredient.objects.create(nom='Tomate')
    
    def test_list_ingredients_public_access(self):
        """Test: Liste des ingrédients accessible publiquement."""
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_ingredient_requires_auth(self):
        """Test: Création d'ingrédient requiert l'authentification."""
        data = {'nom': 'Oignon'}
        
        response = self.client_public.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RecetteAPITestCase(TestCase):
    """
    Tests pour l'API REST Recette avec relations M2M complexes.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        self.url_list = '/api/v1/recipes/recettes/'
        
        # Créer des données de test
        self.technique1 = Technique.objects.create(nom='Blanchir')
        self.technique2 = Technique.objects.create(nom='Ciseler')
        
        self.ingredient1 = Ingredient.objects.create(nom='Tomate')
        self.ingredient2 = Ingredient.objects.create(nom='Oignon')
        
        # Créer une recette de test
        self.recette = Recette.objects.create(
            titre='Ratatouille',
            description='Plat provençal'
        )
        self.recette.auteurs.add(self.user)
        self.recette.techniques_cles.add(self.technique1)
        
        QuantiteIngredient.objects.create(
            recette=self.recette,
            ingredient=self.ingredient1,
            quantite=500,
            unite='g'
        )
    
    def test_list_recettes_public_access(self):
        """Test: Liste des recettes accessible publiquement."""
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_recette_with_nested_data(self):
        """Test: Récupération d'une recette avec données nested."""
        url_detail = f'{self.url_list}{self.recette.id}/'
        response = self.client_public.get(url_detail)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titre'], 'Ratatouille')
        
        # Vérifier les données nested
        self.assertIn('auteurs_detail', response.data)
        self.assertIn('ingredients_detail', response.data)
        self.assertIn('techniques_cles_detail', response.data)
        
        # Vérifier que les auteurs sont présents
        self.assertEqual(len(response.data['auteurs_detail']), 1)
        self.assertEqual(response.data['auteurs_detail'][0]['username'], 'testuser')
        
        # Vérifier que les ingrédients avec quantités sont présents
        self.assertEqual(len(response.data['ingredients_detail']), 1)
        self.assertEqual(response.data['ingredients_detail'][0]['quantite'], 500)
        self.assertEqual(response.data['ingredients_detail'][0]['unite'], 'g')
    
    def test_create_recette_with_ingredients(self):
        """Test: Création d'une recette avec ingrédients et quantités."""
        data = {
            'titre': 'Soupe à l\'oignon',
            'description': 'Soupe française classique',
            'temps_preparation': '00:15:00',
            'temps_cuisson': '00:45:00',
            'auteurs': [self.user.id],
            'techniques_cles': [self.technique2.id],
            'ingredients_data': [
                {
                    'ingredient_id': self.ingredient2.id,
                    'quantite': 4,
                    'unite': 'unités'
                }
            ]
        }
        
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que la recette a été créée
        recette = Recette.objects.get(titre='Soupe à l\'oignon')
        self.assertEqual(recette.auteurs.count(), 1)
        self.assertEqual(recette.techniques_cles.count(), 1)
        
        # Vérifier que les quantités ont été créées
        quantites = QuantiteIngredient.objects.filter(recette=recette)
        self.assertEqual(quantites.count(), 1)
        self.assertEqual(quantites.first().quantite, 4)
    
    def test_update_recette_ingredients(self):
        """Test: Mise à jour des ingrédients d'une recette."""
        url_detail = f'{self.url_list}{self.recette.id}/'
        
        data = {
            'titre': 'Ratatouille',
            'description': 'Plat provençal aux légumes',
            'temps_preparation': '00:30:00',
            'temps_cuisson': '01:00:00',
            'auteurs': [self.user.id],
            'techniques_cles': [self.technique1.id, self.technique2.id],
            'ingredients_data': [
                {
                    'ingredient_id': self.ingredient1.id,
                    'quantite': 600,
                    'unite': 'g'
                },
                {
                    'ingredient_id': self.ingredient2.id,
                    'quantite': 2,
                    'unite': 'unités'
                }
            ]
        }
        
        response = self.client_auth.put(url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les ingrédients ont été mis à jour
        quantites = QuantiteIngredient.objects.filter(recette=self.recette)
        self.assertEqual(quantites.count(), 2)
    
    def test_filter_by_ingredient(self):
        """Test: Filtrage des recettes par ingrédient."""
        response = self.client_public.get(f'{self.url_list}?ingredient={self.ingredient1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filter_by_technique(self):
        """Test: Filtrage des recettes par technique."""
        response = self.client_public.get(f'{self.url_list}?technique={self.technique1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filter_by_auteur(self):
        """Test: Filtrage des recettes par auteur."""
        response = self.client_public.get(f'{self.url_list}?auteur={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_search_recette(self):
        """Test: Recherche de recette fonctionne."""
        response = self.client_public.get(f'{self.url_list}?search=Ratatouille')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_recentes_endpoint(self):
        """Test: Endpoint des recettes récentes."""
        response = self.client_public.get(f'{self.url_list}recentes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_statistiques_endpoint(self):
        """Test: Endpoint des statistiques."""
        response = self.client_public.get(f'{self.url_list}statistiques/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('top_auteurs', response.data)
