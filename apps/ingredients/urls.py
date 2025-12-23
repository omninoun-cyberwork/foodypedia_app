from rest_framework.routers import DefaultRouter
from .views import (
    IngredientViewSet, IngredientCategoryViewSet, 
    FunctionalCategoryViewSet, IngredientFamilyViewSet, 
    LabelViewSet, CulinaryUseViewSet
)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'categories', IngredientCategoryViewSet, basename='category')
router.register(r'functional-categories', FunctionalCategoryViewSet, basename='functional-category')
router.register(r'families', IngredientFamilyViewSet, basename='family')
router.register(r'labels', LabelViewSet, basename='label')
router.register(r'culinary-uses', CulinaryUseViewSet, basename='culinary-use')

urlpatterns = router.urls
