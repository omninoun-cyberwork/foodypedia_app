# foodypedia_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Endpoint pour se connecter et obtenir token ACCESS + REFRESH
    TokenRefreshView,    # Endpoint pour obtenir un nouveau token ACCESS avec le REFRESH
)

from django.http import JsonResponse

def index_view(request):
    return JsonResponse({
        "message": "Bienvenue sur l'API Foodypedia 2.0 🥕",
        "version": "v1",
        "docs": "/api/v1/",
        "admin": "/admin/"
    })

urlpatterns = [
    path('', index_view, name='api-root'),
    path('admin/', admin.site.urls),
    
    # --- JWT & AUTHENTICATION ENDPOINTS ---
    # CORRECTION: Utiliser le chemin modulaire complet 'apps.users.urls'
    path('api/v1/auth/', include('apps.users.urls')), 
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # --- Autres APIs ---
    # CORRECTION: Utiliser le chemin modulaire complet 'apps.recipes.urls'
    path('api/v1/recipes/', include('apps.recipes.urls')),
    # Chef API
    path('api/v1/chefs/', include('apps.chefs.urls')),
    # Atlas API (Données de référence)
    path('api/v1/atlas/', include('apps.atlas.urls')),
    # TechSheets API (Fiches techniques)
    path('api/v1/techsheets/', include('apps.techsheets.urls')),
    # CORRECTION: Utiliser le chemin modulaire complet 'apps.ia.urls'
    path('api/v1/ia/', include('apps.ia.urls')),
    # Ingredients API (Nouveau système 2.0)
    # Ingredients API (Nouveau système 2.0)
    path('api/v1/ingredients/', include('apps.ingredients.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)