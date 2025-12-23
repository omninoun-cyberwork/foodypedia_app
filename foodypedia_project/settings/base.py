

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- Applications Tiers ---
    'rest_framework',
    'corsheaders',
    'django_filters', # Nécessaire pour les filtres API
    
# --- Applications Locales Foodypedia ---
    'apps.core',
    'apps.users',
    'apps.techsheets',
    'apps.ia',

    # Les nouvelles applications !
    'apps.recipes',
    'apps.chefs',
    'apps.atlas',
    'apps.ingredients',

    # Configuration pour les tokens JWT
    'rest_framework_simplejwt',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS en premier
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodypedia_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodypedia_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#               PARTIE AUTHENTIFICATION

# Configuration Globale de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # Utilisation de JWT comme méthode principale d'authentification
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # Permet l'authentification par session pour l'Admin Site et les tests
        'rest_framework.authentication.SessionAuthentication', 
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # Sécurité par défaut : interdire tout accès non authentifié (sauf si spécifié)
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Pagination globale
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Filtres backend
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Configuration de JWT pour les Tokens (Durée de vie, etc.)
from datetime import timedelta

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Token d'accès valide 60 minutes
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Token de rafraîchissement valide 7 jours
#     'ROTATE_REFRESH_TOKENS': True,
#     'ALGORITHM': 'HS256',
#     'SIGNING_KEY': SECRET_KEY, # Utilise la clé secrète de Django pour la signature
#     'USER_ID_FIELD': 'id',
#     'USER_ID_CLAIM': 'user_id',
# }


# Configuration du modèle utilisateur personnalisé
AUTH_USER_MODEL = 'users.CustomUser'

# --- Configuration CORS (Frontend Next.js) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# --- Configuration MEDIA (Images Ingrédients) ---
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')