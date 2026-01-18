# Foodypedia 🍳

**Foodypedia** est une application web gastronomique complète conçue pour être une plateforme de référence culinaire ("Wiki Culinaire"). Elle combine une base de données exhaustive d'ingrédients, un dictionnaire de techniques culinaires, et des fonctionnalités innovantes pour les chefs et amateurs de cuisine.

## 🌟 Fonctionnalités Clés

- **Bibliothèque d'Ingrédients** : Une base de données riche de plus de 500 ingrédients (Fruits, Légumes, Viandes, Poissons, etc.) avec fiches détaillées (saisonnalité, guide d'achat, conseils de préparation, valeurs nutritionnelles).
- **Dictionnaire Culinaire** : Un glossaire interactif regroupant des centaines de termes et techniques de cuisine.
- **Interface Wiki** : Une navigation fluide et intuitive par catégories, conçue pour une expérience utilisateur "premium".
- **Chefs & Recettes** : (En cours de développement) Gestion des fiches techniques et des recettes.
- **AI Chef** : Intégration de l'intelligence artificielle pour l'assistance culinaire.

## 🛠️ Stack Technique

### Backend
- **Django** (Python) : Framework robuste pour la gestion des données et de l'API.
- **Django REST Framework** : Pour une communication fluide entre le front et le back.
- **SQLite** : Base de données locale (environnement de développement).
- **Gestion des Images** : Traitement et stockage optimisé des visuels ingrédients.

### Frontend
- **Next.js** (React) : Framework moderne pour une application web rapide et optimisée (SSR/ISR).
- **TypeScript** : Pour un code robuste et typé.
- **Vanilla CSS / Tailwind** : Design épuré, responsive et moderne.
- **Lucide React** : Bibliothèque d'icônes élégante.

## 🚀 Installation & Développement

### Prérequis
- Python 3.x
- Node.js & npm

### Backend (Django)
1. Activer l'environnement virtuel :
   ```powershell
   .\fenv\Scripts\Activate.ps1
   ```
2. Lancer le serveur :
   ```powershell
   python manage.py runserver
   ```

### Frontend (Next.js)
1. Se rendre dans le dossier :
   ```bash
   cd frontend
   ```
2. Installer les dépendances (si nécessaire) :
   ```bash
   npm install
   ```
3. Lancer le serveur de développement :
   ```bash
   npm run dev
   ```

## 📂 Organisation du Projet

- `apps/` : Applications Django (Ingredients, Atlas, Techsheets, etc.)
- `frontend/` : Application Next.js.
- `static/` : Médias et fichiers statiques (images d'ingrédients).
- `project_management/` : Documentation interne et suivi du développement.
- `archives_donnees/` : Fichiers sources JSON, CSV et archives.

---
*Projet développé avec passion pour la gastronomie.*
