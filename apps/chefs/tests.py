# C:\Foodypedia\apps\chefs\tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Chef
from apps.atlas.models import Pays

User = get_user_model()


class ChefAPITestCase(TestCase):
    """
    Tests pour l'API REST Chef.
    """
    
    def setUp(self):
        """
        Configuration initiale pour chaque test.
        """
        # Créer un utilisateur pour l'authentification
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un pays pour les relations
        self.pays_france = Pays.objects.create(
            nom_fr='France',
            continent='Europe'
        )
        
        # Créer un client API
        self.client = APIClient()
        
        # Authentifier le client
        self.client.force_authenticate(user=self.user)
        
        # URL de base
        self.url_list = '/api/v1/chefs/'
    
    def test_list_chefs_empty(self):
        """
        Test: GET /api/v1/chefs/ retourne une liste vide au départ.
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF retourne une liste directe si la pagination n'est pas configurée
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)
    
    def test_create_chef(self):
        """
        Test: POST /api/v1/chefs/ crée un chef avec succès.
        """
        data = {
            'nom': 'Gordon Ramsay',
            'pays_d_origine': self.pays_france.id,
            'categorie': 'CUISINE',
            'restaurant': 'Restaurant Gordon Ramsay',
            'email': 'gordon@example.com'
        }
        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chef.objects.count(), 1)
        self.assertEqual(Chef.objects.first().nom, 'Gordon Ramsay')
    
    def test_retrieve_chef(self):
        """
        Test: GET /api/v1/chefs/{id}/ récupère les détails d'un chef.
        """
        chef = Chef.objects.create(
            nom='Julia Child',
            pays_d_origine=self.pays_france,
            categorie='CUISINE'
        )
        url_detail = f'{self.url_list}{chef.id}/'
        response = self.client.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], 'Julia Child')
        # Vérifier la sérialisation nested du pays
        self.assertIn('pays_d_origine_detail', response.data)
        self.assertEqual(response.data['pays_d_origine_detail']['nom_fr'], 'France')
    
    def test_update_chef(self):
        """
        Test: PUT /api/v1/chefs/{id}/ met à jour un chef.
        """
        chef = Chef.objects.create(
            nom='Jamie Oliver',
            pays_d_origine=self.pays_france,
            categorie='CUISINE'
        )
        url_detail = f'{self.url_list}{chef.id}/'
        data = {
            'nom': 'Jamie Oliver',
            'pays_d_origine': self.pays_france.id,
            'categorie': 'CUISINE',
            'restaurant': 'Fifteen London'
        }
        response = self.client.put(url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chef.refresh_from_db()
        self.assertEqual(chef.restaurant, 'Fifteen London')
    
    def test_delete_chef(self):
        """
        Test: DELETE /api/v1/chefs/{id}/ supprime un chef.
        """
        chef = Chef.objects.create(
            nom='Anthony Bourdain',
            pays_d_origine=self.pays_france,
            categorie='CUISINE'
        )
        url_detail = f'{self.url_list}{chef.id}/'
        response = self.client.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Chef.objects.count(), 0)
    
    def test_filter_by_category(self):
        """
        Test: Filtrage par catégorie fonctionne.
        """
        Chef.objects.create(nom='Chef 1', categorie='CUISINE', pays_d_origine=self.pays_france)
        Chef.objects.create(nom='Chef 2', categorie='PATISSERIE', pays_d_origine=self.pays_france)
        
        response = self.client.get(f'{self.url_list}?categorie=CUISINE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['categorie'], 'CUISINE')
    
    def test_search_chef(self):
        """
        Test: Recherche par nom fonctionne.
        """
        Chef.objects.create(nom='Gordon Ramsay', categorie='CUISINE', pays_d_origine=self.pays_france)
        Chef.objects.create(nom='Jamie Oliver', categorie='CUISINE', pays_d_origine=self.pays_france)
        
        response = self.client.get(f'{self.url_list}?search=Gordon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Gordon Ramsay')
    
    def test_categories_endpoint(self):
        """
        Test: Endpoint personnalisé /categories/ retourne les catégories.
        """
        response = self.client.get(f'{self.url_list}categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
    
    def test_statistiques_endpoint(self):
        """
        Test: Endpoint personnalisé /statistiques/ retourne les stats.
        """
        Chef.objects.create(nom='Chef 1', categorie='CUISINE', pays_d_origine=self.pays_france)
        Chef.objects.create(nom='Chef 2', categorie='PATISSERIE', pays_d_origine=self.pays_france)
        
        response = self.client.get(f'{self.url_list}statistiques/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertIn('par_categorie', response.data)
    
    def test_authentication_required(self):
        """
        Test: L'authentification est requise pour accéder à l'API.
        """
        # Créer un client non authentifié
        client_non_auth = APIClient()
        response = client_non_auth.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_email_uniqueness_validation(self):
        """
        Test: Validation de l'unicité de l'email.
        """
        Chef.objects.create(
            nom='Chef 1',
            email='unique@example.com',
            categorie='CUISINE',
            pays_d_origine=self.pays_france
        )
        
        data = {
            'nom': 'Chef 2',
            'email': 'unique@example.com',
            'categorie': 'CUISINE',
            'pays_d_origine': self.pays_france.id
        }
        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
