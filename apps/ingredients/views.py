from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Ingredient, IngredientCategory, FunctionalCategory, 
    IngredientFamily, Label, CulinaryUse
)
from .serializers import (
    IngredientSerializer, IngredientCategorySerializer, 
    FunctionalCategorySerializer, IngredientFamilySerializer, 
    LabelSerializer, CulinaryUseSerializer
)

# -------------------------------------------------------------------------
# ViewSets pour les Référentiels (Read-Only ou Admin Management)
# -------------------------------------------------------------------------

class IngredientCategoryViewSet(viewsets.ModelViewSet):
    """Gère les catégories principales (ex: Épice)."""
    queryset = IngredientCategory.objects.all()
    serializer_class = IngredientCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class FunctionalCategoryViewSet(viewsets.ModelViewSet):
    """Gère les catégories fonctionnelles (ex: Pâtisserie)."""
    queryset = FunctionalCategory.objects.all()
    serializer_class = FunctionalCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class IngredientFamilyViewSet(viewsets.ModelViewSet):
    queryset = IngredientFamily.objects.all()
    serializer_class = IngredientFamilySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CulinaryUseViewSet(viewsets.ModelViewSet):
    queryset = CulinaryUse.objects.all()
    serializer_class = CulinaryUseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# -------------------------------------------------------------------------
# ViewSet Principal : INGRÉDIENT
# -------------------------------------------------------------------------

class IngredientViewSet(viewsets.ModelViewSet):
    """
    API Principale pour les Ingrédients.
    Supporte filtres avancés :
    - ?category=Epice
    - ?functional_categories=Patisserie
    - ?search=Anis
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtres
    filterset_fields = {
        'category': ['exact'],
        'category__slug': ['exact'],
        'functional_categories__slug': ['exact'],
        'functional_categories': ['exact'],
        'family': ['exact'],
        'labels': ['exact'],
    }
    search_fields = ['name', 'scientific_name', 'description', 'flavor_profile']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Retourne les ingrédients groupés par catégorie principale.
        Utile pour les menus déroulants ou l'arborecence.
        """
        categories = IngredientCategory.objects.all()
        data = {}
        for cat in categories:
            data[cat.name] = IngredientSerializer(
                cat.ingredients.all(), 
                many=True,
                context={'request': request}
            ).data
        return Response(data)
