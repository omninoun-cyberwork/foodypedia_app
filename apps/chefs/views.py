# C:\Foodypedia\apps\chefs\views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Chef
from .serializers import ChefSerializer


class ChefViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Chef.
    
    Endpoints disponibles:
    - GET /api/v1/chefs/ - Liste tous les chefs
    - POST /api/v1/chefs/ - Crée un nouveau chef
    - GET /api/v1/chefs/{id}/ - Récupère un chef spécifique
    - PUT /api/v1/chefs/{id}/ - Met à jour un chef (complet)
    - PATCH /api/v1/chefs/{id}/ - Met à jour un chef (partiel)
    - DELETE /api/v1/chefs/{id}/ - Supprime un chef
    
    Authentification requise: JWT Token
    """
    queryset = Chef.objects.select_related('pays_d_origine').all()
    serializer_class = ChefSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filtrage et recherche
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'restaurant', 'email']
    ordering_fields = ['nom', 'date_de_naissance', 'categorie']
    ordering = ['nom']  # Tri par défaut
    
    def get_queryset(self):
        """
        Personnalisation du queryset avec filtres optionnels.
        """
        queryset = super().get_queryset()
        
        # Filtre par catégorie (ex: ?categorie=CUISINE)
        categorie = self.request.query_params.get('categorie', None)
        if categorie:
            queryset = queryset.filter(categorie=categorie)
        
        # Filtre par pays (ex: ?pays=1)
        pays_id = self.request.query_params.get('pays', None)
        if pays_id:
            queryset = queryset.filter(pays_d_origine_id=pays_id)
        
        # Filtre pour les chefs vivants ou décédés
        statut = self.request.query_params.get('statut', None)
        if statut == 'vivant':
            queryset = queryset.filter(date_de_deces__isnull=True)
        elif statut == 'decede':
            queryset = queryset.filter(date_de_deces__isnull=False)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Endpoint personnalisé pour obtenir la liste des catégories disponibles.
        GET /api/v1/chefs/categories/
        """
        categories = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Chef.CATEGORIE_CHOICES
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les chefs.
        GET /api/v1/chefs/statistiques/
        """
        total = self.get_queryset().count()
        par_categorie = {}
        
        for code, label in Chef.CATEGORIE_CHOICES:
            count = self.get_queryset().filter(categorie=code).count()
            par_categorie[label] = count
        
        vivants = self.get_queryset().filter(date_de_deces__isnull=True).count()
        decedes = self.get_queryset().filter(date_de_deces__isnull=False).count()
        
        return Response({
            'total': total,
            'par_categorie': par_categorie,
            'vivants': vivants,
            'decedes': decedes,
        })
