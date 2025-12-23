# C:\Foodypedia\apps\techsheets\views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from .models import FicheTechnique
from .serializers import FicheTechniqueSerializer


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


class FicheTechniqueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle FicheTechnique.
    
    Endpoints disponibles:
    - GET /api/v1/techsheets/fiches-techniques/ - Liste toutes les fiches (public)
    - POST /api/v1/techsheets/fiches-techniques/ - Crée une fiche (authentifié)
    - GET /api/v1/techsheets/fiches-techniques/{id}/ - Récupère une fiche (public)
    - PUT/PATCH /api/v1/techsheets/fiches-techniques/{id}/ - Met à jour (authentifié)
    - DELETE /api/v1/techsheets/fiches-techniques/{id}/ - Supprime (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    serializer_class = FicheTechniqueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['recette_fk__titre', 'recette_fk__description']
    ordering_fields = ['nombre_portions', 'cout_matiere_ht', 'marge_appliquee', 'validation_admin']
    ordering = ['-validation_admin', 'recette_fk__titre']
    
    def get_queryset(self):
        """
        Queryset optimisé avec select_related pour éviter N+1 queries.
        """
        queryset = FicheTechnique.objects.select_related('recette_fk').all()
        
        # Filtre par statut de validation
        validation = self.request.query_params.get('validation_admin', None)
        if validation is not None:
            validation_bool = validation.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(validation_admin=validation_bool)
        
        # Filtre par recette
        recette_id = self.request.query_params.get('recette', None)
        if recette_id:
            queryset = queryset.filter(recette_fk_id=recette_id)
        
        # Filtre par coût minimum
        cout_min = self.request.query_params.get('cout_min', None)
        if cout_min:
            queryset = queryset.filter(cout_matiere_ht__gte=cout_min)
        
        # Filtre par coût maximum
        cout_max = self.request.query_params.get('cout_max', None)
        if cout_max:
            queryset = queryset.filter(cout_matiere_ht__lte=cout_max)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def validees(self, request):
        """
        Endpoint personnalisé pour obtenir uniquement les fiches validées.
        GET /api/v1/techsheets/fiches-techniques/validees/
        """
        fiches = self.get_queryset().filter(validation_admin=True)
        serializer = self.get_serializer(fiches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les fiches techniques.
        GET /api/v1/techsheets/fiches-techniques/statistiques/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        validees = queryset.filter(validation_admin=True).count()
        non_validees = queryset.filter(validation_admin=False).count()
        
        # Coûts moyens
        cout_moyen = queryset.aggregate(Avg('cout_matiere_ht'))['cout_matiere_ht__avg']
        marge_moyenne = queryset.aggregate(Avg('marge_appliquee'))['marge_appliquee__avg']
        
        # Portions moyennes
        portions_moyennes = queryset.aggregate(Avg('nombre_portions'))['nombre_portions__avg']
        
        return Response({
            'total': total,
            'validees': validees,
            'non_validees': non_validees,
            'taux_validation': round((validees / total * 100) if total > 0 else 0, 2),
            'cout_moyen_ht': float(cout_moyen) if cout_moyen else 0.0,
            'marge_moyenne': float(marge_moyenne) if marge_moyenne else 0.0,
            'portions_moyennes': float(portions_moyennes) if portions_moyennes else 0.0,
        })
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """
        Endpoint personnalisé pour valider une fiche technique.
        POST /api/v1/techsheets/fiches-techniques/{id}/valider/
        """
        from datetime import date
        
        fiche = self.get_object()
        fiche.validation_admin = True
        fiche.date_validation = date.today()
        fiche.save()
        
        serializer = self.get_serializer(fiche)
        return Response(serializer.data)
