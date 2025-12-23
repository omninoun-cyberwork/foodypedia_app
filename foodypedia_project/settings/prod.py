# foodypedia_project/settings/prod.py

from .base import *
import dj_database_url
import os

# Sécurité: La clé secrète DOIT être lue depuis l'environnement de production
SECRET_KEY = os.environ['SECRET_KEY']

# Sécurité: Liste des hôtes autorisés (votre nom de domaine)
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# Mode debug désactivé en production
DEBUG = False

# Configuration de la base de données PostgreSQL de production
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Paramètres de sécurité HTTP (essentiels en prod)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True