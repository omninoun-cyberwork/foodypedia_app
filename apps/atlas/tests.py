# C:\Foodypedia\apps\atlas\tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Pays, Materiel, Glossaire

User = get_user_model()


class PaysAPITestCase(TestCase):
    """
    Tests pour l'API REST Pays.
    """
    
    def setUp(self):
        """
        Configuration initiale pour chaque test.
        """
        # Créer un utilisateur pour les opérations d'écriture
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer deux clients: un authentifié et un non authentifié
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        # URL de base
        self.url_list = '/api/v1/atlas/pays/'
        
        # Créer des données de test
        self.pays_france = Pays.objects.create(
            nom_fr='France',
            continent='Europe'
        )
    
    def test_list_pays_public_access(self):
        """
        Test: GET /api/v1/atlas/pays/ accessible sans authentification.
        """
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_pays_public_access(self):
        """
        Test: GET /api/v1/atlas/pays/{id}/ accessible sans authentification.
        """
        url_detail = f'{self.url_list}{self.pays_france.id}/'
        response = self.client_public.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom_fr'], 'France')
    
    def test_create_pays_requires_auth(self):
        """
        Test: POST /api/v1/atlas/pays/ requiert l'authentification.
        """
        data = {'nom_fr': 'Italie', 'continent': 'Europe'}
        
        # Sans authentification
        response = self.client_public.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Avec authentification
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pays.objects.count(), 2)
    
    def test_update_pays_requires_auth(self):
        """
        Test: PUT /api/v1/atlas/pays/{id}/ requiert l'authentification.
        """
        url_detail = f'{self.url_list}{self.pays_france.id}/'
        data = {'nom_fr': 'France', 'continent': 'Europe Occidentale'}
        
        # Sans authentification
        response = self.client_public.put(url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Avec authentification
        response = self.client_auth.put(url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_pays_requires_auth(self):
        """
        Test: DELETE /api/v1/atlas/pays/{id}/ requiert l'authentification.
        """
        url_detail = f'{self.url_list}{self.pays_france.id}/'
        
        # Sans authentification
        response = self.client_public.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Avec authentification
        response = self.client_auth.delete(url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Pays.objects.count(), 0)
    
    def test_filter_by_continent(self):
        """
        Test: Filtrage par continent fonctionne.
        """
        Pays.objects.create(nom_fr='Japon', continent='Asie')
        
        response = self.client_public.get(f'{self.url_list}?continent=Europe')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['continent'], 'Europe')
    
    def test_search_pays(self):
        """
        Test: Recherche par nom fonctionne.
        """
        Pays.objects.create(nom_fr='Espagne', continent='Europe')
        
        response = self.client_public.get(f'{self.url_list}?search=France')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom_fr'], 'France')
    
    def test_continents_endpoint(self):
        """
        Test: Endpoint /continents/ retourne les continents uniques.
        """
        Pays.objects.create(nom_fr='Japon', continent='Asie')
        
        response = self.client_public.get(f'{self.url_list}continents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Europe', response.data)
        self.assertIn('Asie', response.data)


class MaterielAPITestCase(TestCase):
    """
    Tests pour l'API REST Materiel.
    """
    
    def setUp(self):
        """
        Configuration initiale.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        self.url_list = '/api/v1/atlas/materiel/'
        
        self.materiel = Materiel.objects.create(
            nom_fr='Couteau de chef',
            description_courte='Couteau polyvalent pour la cuisine',
            categorie='U'
        )
    
    def test_list_materiel_public_access(self):
        """
        Test: Liste du matériel accessible publiquement.
        """
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_materiel_requires_auth(self):
        """
        Test: Création de matériel requiert l'authentification.
        """
        data = {
            'nom_fr': 'Four à convection',
            'description_courte': 'Four professionnel',
            'categorie': 'M'
        }
        
        # Sans authentification
        response = self.client_public.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Avec authentification
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_by_category(self):
        """
        Test: Filtrage par catégorie fonctionne.
        """
        Materiel.objects.create(
            nom_fr='Four',
            description_courte='Four professionnel',
            categorie='M'
        )
        
        response = self.client_public.get(f'{self.url_list}?categorie=U')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['categorie'], 'U')
    
    def test_categories_endpoint(self):
        """
        Test: Endpoint /categories/ retourne les catégories.
        """
        response = self.client_public.get(f'{self.url_list}categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)


class GlossaireAPITestCase(TestCase):
    """
    Tests pour l'API REST Glossaire.
    """
    
    def setUp(self):
        """
        Configuration initiale.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client_auth = APIClient()
        self.client_auth.force_authenticate(user=self.user)
        
        self.client_public = APIClient()
        
        self.url_list = '/api/v1/atlas/glossaire/'
        
        self.terme = Glossaire.objects.create(
            terme='Blanchir',
            definition='Plonger un aliment dans l\'eau bouillante',
            type_terme='V'
        )
    
    def test_list_glossaire_public_access(self):
        """
        Test: Liste du glossaire accessible publiquement.
        """
        response = self.client_public.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_terme_requires_auth(self):
        """
        Test: Création de terme requiert l'authentification.
        """
        data = {
            'terme': 'Ciseler',
            'definition': 'Couper finement',
            'type_terme': 'V'
        }
        
        # Sans authentification
        response = self.client_public.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Avec authentification
        response = self.client_auth.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_by_type(self):
        """
        Test: Filtrage par type de terme fonctionne.
        """
        Glossaire.objects.create(
            terme='Couteau',
            definition='Ustensile de coupe',
            type_terme='N'
        )
        
        response = self.client_public.get(f'{self.url_list}?type_terme=V')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type_terme'], 'V')
    
    def test_search_glossaire(self):
        """
        Test: Recherche dans le glossaire fonctionne.
        """
        response = self.client_public.get(f'{self.url_list}?search=Blanchir')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['terme'], 'Blanchir')
    
    def test_types_endpoint(self):
        """
        Test: Endpoint /types/ retourne les types de termes.
        """
        response = self.client_public.get(f'{self.url_list}types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
