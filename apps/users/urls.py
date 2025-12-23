# accounts/urls.py

from django.urls import path
from .views import RegisterView

urlpatterns = [
    # Endpoint pour l'inscription
    path('register/', RegisterView.as_view(), name='user_register'),
    
    # Nous pourrions ajouter ici 'profile/', 'password_reset/', etc.
]