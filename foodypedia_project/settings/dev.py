# foodypedia_project/settings/dev.py

from .base import *
import os


# Sécurité: La clé secrète sera lue depuis le .env.dev local
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-dev')

# Sécurité: Autoriser l'accès depuis localhost
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Mode debug activé
DEBUG = True

# Base de données locale (SQLite pour la dev simple, si pas de PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# NOTE: Si vous utilisez PostgreSQL en dev, utilisez plutôt django-environ pour charger DATABASE_URL ici.