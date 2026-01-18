import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.core.files import File
from apps.ingredients.models import Ingredient, IngredientCategory, FunctionalCategory
from apps.atlas.models import Glossaire

class Command(BaseCommand):
    help = 'Importe les poissons et fruits de mer depuis les fichiers JSON spécifiques'

    def handle(self, *args, **options):
        # 1. Configuration des catégories
        # On s'assure que les catégories demandées par l'utilisateur existent
        CATEGORY_MAPPING = {
            'poissons.json': {
                'slug': 'poisson',
                'name': 'Poissons',
                'description': 'Une large sélection de poissons d’eau douce et de mer, entiers ou en filets.',
            },
            'seafood.json': {
                'slug': 'fruits-de-mer',
                'name': 'Fruits de mer',
                'description': 'Crustacés, coquillages et mollusques : la richesse des océans dans votre assiette.',
            }
        }

        # Nettoyage / Harmonisation des catégories existantes si nécessaire
        # Si la catégorie 'poisson' (singulier) existe, on peut la renommer ou fusionner.
        # L'utilisateur a demandé "poissons" (pluriel).
        
        for file_name, cat_info in CATEGORY_MAPPING.items():
            category, created = IngredientCategory.objects.get_or_create(
                slug=cat_info['slug'],
                defaults={'name': cat_info['name'], 'description': cat_info['description']}
            )
            if not created:
                category.name = cat_info['name']
                category.description = cat_info['description']
                category.save()
            
            self.stdout.write(f"Catégorie prête : {category.name} ({cat_info['slug']})")

        # 2. Chemins des fichiers
        # Utilisation des chemins fournis par l'utilisateur
        JSON_FILES = [
            (r"C:\Foodypedia\Jsons ingredients\poissons.json", 'poisson'),
            (r"C:\Foodypedia\Jsons ingredients\seafood.json", 'fruits-de-mer')
        ]

        for json_path, cat_slug in JSON_FILES:
            if not os.path.exists(json_path):
                self.stdout.write(self.style.ERROR(f"Fichier introuvable : {json_path}"))
                continue

            category = IngredientCategory.objects.get(slug=cat_slug)
            self.stdout.write(f"\n--- Importation depuis {os.path.basename(json_path)} dans {category.name} ---")

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    name = item.get('name')
                    if not name or name == "Non spécifié":
                        continue

                    # Gestion du glossaire
                    glossary_term = None
                    glossary_name = item.get('glossary_term')
                    if glossary_name and glossary_name != "Non spécifié":
                        glossary_term, _ = Glossaire.objects.get_or_create(
                            terme=glossary_name,
                            defaults={'definition': f"Définition pour {glossary_name}.", 'type_terme': 'N'}
                        )

                    # Création ou mise à jour de l'ingrédient
                    ingredient, created = Ingredient.objects.update_or_create(
                        name=name,
                        defaults={
                            'slug': slugify(name),
                            'scientific_name': item.get('scientific_name', '') if item.get('scientific_name') != "Non spécifié" else '',
                            'description': item.get('description', '') if item.get('description') != "Non spécifié" else '',
                            'category': category,
                            'glossary_term': glossary_term,
                            'seasonality': item.get('seasonality', '') if item.get('seasonality') != "Non spécifié" else '',
                            'buying_guide': item.get('buying_guide', '') if item.get('buying_guide') != "Non spécifié" else '',
                            'storage_guide': item.get('storage_guide', '') if item.get('storage_guide') != "Non spécifié" else '',
                            'prep_guide': item.get('prep_guide', '') if item.get('prep_guide') != "Non spécifié" else '',
                            'nutrition_info': item.get('nutrition_info', '') if item.get('nutrition_info') != "Non spécifié" else '',
                            'texture': item.get('texture', '') if item.get('texture') != "Non spécifié" else '',
                            'specific_data': item.get('specific_data', {}),
                            'tags': item.get('tags', []),
                        }
                    )

                    # Catégories fonctionnelles
                    func_cats = item.get('functional_categories', [])
                    for fc_name in func_cats:
                        fc_slug = slugify(fc_name)
                        fc, _ = FunctionalCategory.objects.get_or_create(slug=fc_slug, defaults={'name': fc_name})
                        ingredient.functional_categories.add(fc)

                    # Gestion de l'image
                    image_filename = item.get('image_filename')
                    if not image_filename or '{{' in image_filename:
                        # Fallback sur le nom de l'ingrédient
                        image_filename = f"{name}.jpg"

                    # On ne recharge l'image que si elle n'est pas déjà présente
                    if not ingredient.main_image:
                        img_path = self.find_image(image_filename)
                        if not img_path: # Tentative avec .png
                             img_path = self.find_image(image_filename.replace('.jpg', '.png'))
                        if not img_path: # Tentative en minuscules
                             img_path = self.find_image(image_filename.lower())
                        
                        if img_path:
                            try:
                                with open(img_path, 'rb') as f_img:
                                    ingredient.main_image.save(os.path.basename(img_path), File(f_img), save=True)
                                    self.stdout.write(f"  [OK] {ingredient.name} (Image: {os.path.basename(img_path)})")
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"  [!] Erreur image pour {ingredient.name} : {e}"))
                        else:
                            self.stdout.write(f"  [OK] {ingredient.name} (Sans image)")
                    else:
                        self.stdout.write(f"  [OK] {ingredient.name} (Déjà importé)")

        self.stdout.write(self.style.SUCCESS("\nImportation terminée avec succès !"))

    def find_image(self, filename):
        """Recherche récursive de l'image dans le dossier static/ingredients_pics"""
        root_dir = settings.BASE_DIR.parent
        search_root = os.path.join(root_dir, 'static', 'ingredients_pics')
        
        # 1. Recherche exacte
        for root, dirs, files in os.walk(search_root):
            if filename in files:
                return os.path.join(root, filename)
        
        # 2. Recherche insensible à la casse
        for root, dirs, files in os.walk(search_root):
            for f in files:
                if f.lower() == filename.lower():
                    return os.path.join(root, f)
        
        return None
