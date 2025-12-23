# C:\Foodypedia\apps\atlas\views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Pays, Materiel, Glossaire
from .serializers import PaysSerializer, MaterielSerializer, GlossaireSerializer


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour le modèle Wiki:
    - Lecture (GET, HEAD, OPTIONS): Accessible à tous
    - Écriture (POST, PUT, PATCH, DELETE): Authentification requise
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class PaysViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Pays.
    
    Endpoints disponibles:
    - GET /api/v1/atlas/pays/ - Liste tous les pays (public)
    - POST /api/v1/atlas/pays/ - Crée un nouveau pays (authentifié)
    - GET /api/v1/atlas/pays/{id}/ - Récupère un pays spécifique (public)
    - PUT/PATCH /api/v1/atlas/pays/{id}/ - Met à jour un pays (authentifié)
    - DELETE /api/v1/atlas/pays/{id}/ - Supprime un pays (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Filtrage et recherche
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_fr', 'continent']
    ordering_fields = ['nom_fr', 'continent']
    ordering = ['nom_fr']
    
    def get_queryset(self):
        """
        Personnalisation du queryset avec filtres optionnels.
        """
        queryset = super().get_queryset()
        
        # Filtre par continent (ex: ?continent=Europe)
        continent = self.request.query_params.get('continent', None)
        if continent:
            queryset = queryset.filter(continent__icontains=continent)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def continents(self, request):
        """
        Endpoint personnalisé pour obtenir la liste des continents uniques.
        GET /api/v1/atlas/pays/continents/
        """
        continents = Pays.objects.values_list('continent', flat=True).distinct().order_by('continent')
        return Response(list(continents))
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les pays.
        GET /api/v1/atlas/pays/statistiques/
        """
        total = self.get_queryset().count()
        par_continent = {}
        
        continents = Pays.objects.values_list('continent', flat=True).distinct()
        for continent in continents:
            count = self.get_queryset().filter(continent=continent).count()
            par_continent[continent] = count
        
        return Response({
            'total': total,
            'par_continent': par_continent,
        })


class MaterielViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Materiel.
    
    Endpoints disponibles:
    - GET /api/v1/atlas/materiel/ - Liste tout le matériel (public)
    - POST /api/v1/atlas/materiel/ - Crée un nouvel équipement (authentifié)
    - GET /api/v1/atlas/materiel/{id}/ - Récupère un équipement (public)
    - PUT/PATCH /api/v1/atlas/materiel/{id}/ - Met à jour un équipement (authentifié)
    - DELETE /api/v1/atlas/materiel/{id}/ - Supprime un équipement (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = Materiel.objects.all()
    serializer_class = MaterielSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Filtrage et recherche
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_fr', 'description_courte']
    ordering_fields = ['nom_fr', 'categorie']
    ordering = ['nom_fr']
    
    def get_queryset(self):
        """
        Personnalisation du queryset avec filtres optionnels.
        """
        queryset = super().get_queryset()
        
        # Filtre par catégorie (ex: ?categorie=U)
        categorie = self.request.query_params.get('categorie', None)
        if categorie:
            queryset = queryset.filter(categorie=categorie)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Endpoint personnalisé pour obtenir la liste des catégories disponibles.
        GET /api/v1/atlas/materiel/categories/
        """
        categories = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Materiel.CATEGORIES
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur le matériel.
        GET /api/v1/atlas/materiel/statistiques/
        """
        total = self.get_queryset().count()
        par_categorie = {}
        
        for code, label in Materiel.CATEGORIES:
            count = self.get_queryset().filter(categorie=code).count()
            par_categorie[label] = count
        
        return Response({
            'total': total,
            'par_categorie': par_categorie,
        })


class GlossaireViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Glossaire.
    
    Endpoints disponibles:
    - GET /api/v1/atlas/glossaire/ - Liste tous les termes (public)
    - POST /api/v1/atlas/glossaire/ - Crée un nouveau terme (authentifié)
    - GET /api/v1/atlas/glossaire/{id}/ - Récupère un terme (public)
    - PUT/PATCH /api/v1/atlas/glossaire/{id}/ - Met à jour un terme (authentifié)
    - DELETE /api/v1/atlas/glossaire/{id}/ - Supprime un terme (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = Glossaire.objects.all()
    serializer_class = GlossaireSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Filtrage et recherche
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['terme', 'definition']
    ordering_fields = ['terme', 'type_terme']
    ordering = ['terme']
    
    def get_queryset(self):
        """
        Personnalisation du queryset avec filtres optionnels.
        """
        queryset = super().get_queryset()
        
        # Filtre par type de terme (ex: ?type_terme=V)
        type_terme = self.request.query_params.get('type_terme', None)
        if type_terme:
            queryset = queryset.filter(type_terme=type_terme)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """
        Endpoint personnalisé pour obtenir la liste des types de termes disponibles.
        GET /api/v1/atlas/glossaire/types/
        """
        types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Glossaire.TYPES
        ]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur le glossaire.
        GET /api/v1/atlas/glossaire/statistiques/
        """
        total = self.get_queryset().count()
        par_type = {}
        
        for code, label in Glossaire.TYPES:
            count = self.get_queryset().filter(type_terme=code).count()
            par_type[label] = count
        
        return Response({
            'total': total,
            'par_type': par_type,
        })
