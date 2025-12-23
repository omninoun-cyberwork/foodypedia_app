# C:\Foodypedia\apps\recipes\views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Technique, Ingredient, QuantiteIngredient, Recette, RecipeCategory
from .serializers import (
    TechniqueSerializer,
    IngredientSerializer,
    QuantiteIngredientSerializer,
    RecetteSerializer,
    RecipeCategorySerializer
)


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


class TechniqueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Technique.
    
    Endpoints disponibles:
    - GET /api/v1/recipes/techniques/ - Liste toutes les techniques (public)
    - POST /api/v1/recipes/techniques/ - Crée une technique (authentifié)
    - GET /api/v1/recipes/techniques/{id}/ - Récupère une technique (public)
    - PUT/PATCH /api/v1/recipes/techniques/{id}/ - Met à jour (authentifié)
    - DELETE /api/v1/recipes/techniques/{id}/ - Supprime (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = Technique.objects.all()
    serializer_class = TechniqueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']
    ordering = ['nom']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les techniques.
        GET /api/v1/recipes/techniques/statistiques/
        """
        total = self.get_queryset().count()
        
        # Top 5 techniques les plus utilisées
        top_techniques = Technique.objects.annotate(
            usage_count=Count('recettes_utilisant_technique')
        ).order_by('-usage_count')[:5]
        
        top_list = [
            {
                'nom': tech.nom,
                'nombre_recettes': tech.usage_count
            }
            for tech in top_techniques
        ]
        
        return Response({
            'total': total,
            'top_techniques': top_list,
        })


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Ingredient.
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom']
    ordering_fields = ['nom']
    ordering = ['nom']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les ingrédients.
        GET /api/v1/recipes/ingredients/statistiques/
        """
        total = self.get_queryset().count()
        
        # Top 5 ingrédients les plus utilisés
        top_ingredients = Ingredient.objects.annotate(
            usage_count=Count('recettes_contenues')
        ).order_by('-usage_count')[:5]
        
        top_list = [
            {
                'nom': ing.nom,
                'nombre_recettes': ing.usage_count
            }
            for ing in top_ingredients
        ]
        
        return Response({
            'total': total,
            'top_ingredients': top_list,
        })


class QuantiteIngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle QuantiteIngredient.
    
    Note: Ce viewset est principalement utilisé en interne.
    Les recettes gèrent les quantités via la sérialisation nested.
    
    Permissions: Lecture publique, écriture authentifiée
    """
    queryset = QuantiteIngredient.objects.select_related('recette', 'ingredient').all()
    serializer_class = QuantiteIngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['recette', 'ingredient', 'quantite']
    ordering = ['recette']
    
    def get_queryset(self):
        """
        Personnalisation du queryset avec filtres optionnels.
        """
        queryset = super().get_queryset()
        
        # Filtre par recette
        recette_id = self.request.query_params.get('recette', None)
        if recette_id:
            queryset = queryset.filter(recette_id=recette_id)
        
        # Filtre par ingrédient
        ingredient_id = self.request.query_params.get('ingredient', None)
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)
        
        return queryset


class RecetteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur le modèle Recette.
    
    Endpoints disponibles:
    - GET /api/v1/recipes/recettes/ - Liste toutes les recettes (public)
    - POST /api/v1/recipes/recettes/ - Crée une recette (authentifié)
    - GET /api/v1/recipes/recettes/{id}/ - Récupère une recette (public)
    - PUT/PATCH /api/v1/recipes/recettes/{id}/ - Met à jour (authentifié)
    - DELETE /api/v1/recipes/recettes/{id}/ - Supprime (authentifié)
    
    Permissions: Lecture publique, écriture authentifiée
    """
    serializer_class = RecetteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titre', 'description']
    ordering_fields = ['titre', 'date_creation', 'temps_preparation', 'temps_cuisson']
    ordering = ['-date_creation']  # Par défaut, les plus récentes en premier
    
    def get_queryset(self):
        """
        Queryset optimisé avec prefetch_related pour éviter N+1 queries.
        Supporte le filtrage récursif par catégorie.
        """
        queryset = Recette.objects.prefetch_related(
            'auteurs',
            'techniques_cles',
            'lignes_ingredients__ingredient'
        ).all()
        
        # Filtrage par catégorie (récursif)
        # On regarde d'abord si on filtre par une sous-catégorie spécifique
        # sinon on regarde la catégorie racine (Cuisine/Pâtisserie)
        category_slug = self.request.query_params.get('category__slug') or \
                        self.request.query_params.get('category__root_slug')
        
        if category_slug:
            try:
                root_cat = RecipeCategory.objects.get(slug=category_slug)
                # Version robuste pour collecter les IDs
                ids_to_check = [root_cat.id]
                all_ids = set()
                while ids_to_check:
                    current_id = ids_to_check.pop()
                    if current_id not in all_ids:
                        all_ids.add(current_id)
                        children_ids = RecipeCategory.objects.filter(parent_id=current_id).values_list('id', flat=True)
                        ids_to_check.extend(list(children_ids))
                
                queryset = queryset.filter(category_id__in=all_ids)
            except RecipeCategory.DoesNotExist:
                queryset = queryset.filter(category__slug=category_slug)

        # Filtre par auteur
        auteur_id = self.request.query_params.get('auteur')
        if auteur_id:
            queryset = queryset.filter(auteurs__id=auteur_id)
        
        # Filtre par ingrédient
        ingredient_id = self.request.query_params.get('ingredient')
        if ingredient_id:
            queryset = queryset.filter(ingredients__id=ingredient_id)
        
        # Filtre par technique
        technique_id = self.request.query_params.get('technique')
        if technique_id:
            queryset = queryset.filter(techniques_cles__id=technique_id)
        
        return queryset.distinct()
    
    @action(detail=False, methods=['get'])
    def recentes(self, request):
        """
        Endpoint personnalisé pour obtenir les recettes les plus récentes.
        GET /api/v1/recipes/recettes/recentes/
        """
        limit = int(request.query_params.get('limit', 10))
        recettes = self.get_queryset().order_by('-date_creation')[:limit]
        serializer = self.get_serializer(recettes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint personnalisé pour obtenir des statistiques sur les recettes.
        GET /api/v1/recipes/recettes/statistiques/
        """
        total = self.get_queryset().count()
        
        # Nombre de recettes par auteur (top 5)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        top_auteurs = User.objects.annotate(
            recette_count=Count('recettes_contribuees')
        ).filter(recette_count__gt=0).order_by('-recette_count')[:5]
        
        auteurs_list = [
            {
                'username': user.username,
                'nombre_recettes': user.recette_count
            }
            for user in top_auteurs
        ]
        
        return Response({
            'total': total,
            'top_auteurs': auteurs_list,
        })


class RecipeCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les catégories de recettes.
    Lecture seule pour le public.
    """
    queryset = RecipeCategory.objects.all()
    serializer_class = RecipeCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Désactivation de la pagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
