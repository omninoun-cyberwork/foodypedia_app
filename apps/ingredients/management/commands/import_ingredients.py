import json
import os
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.core.files import File
from apps.ingredients.models import Ingredient, IngredientCategory, FunctionalCategory
from apps.atlas.models import Glossaire

class Command(BaseCommand):
    help = 'Importe les ingrédients et catégories avec gestion des images'

    def handle(self, *args, **options):
        # 1. Définir les catégories principales
        CATEGORY_CONFIG = {
            'legume': {
                'name': 'Légumes',
                'description': 'Une exploration complète des légumes : des racines aux feuilles, découvrez leurs saveurs et textures uniques.',
                'image_search': 'courgette.jpg'
            },
            'fruit': {
                'name': 'Fruits',
                'description': 'Découvrez la richesse des fruits du monde entier, leurs bienfaits et leurs utilisations culinaires.',
                'image_search': 'Pomme.jpg'
            },
            'epice': {
                'name': 'Épices & Herbes',
                'description': 'Le secret de toute grande cuisine : apprenez à maîtriser les épices, aromates et herbes fraîches.',
                'image_search': 'Curry.jpg'
            },
            'poisson': {
                'name': 'Poissons & Fruits de Mer',
                'description': 'Produits de la mer et d’eau douce : guides d’achat, fraîcheur et techniques de préparation.',
            },
            'viande': {
                'name': 'Viandes & Volailles',
                'description': 'Connaître les morceaux, les maturations et les meilleures méthodes de cuisson pour chaque viande.',
            }
        }

        self.stdout.write("--- Création des catégories principales ---")
        for slug, info in CATEGORY_CONFIG.items():
            cat, created = IngredientCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': info['name'],
                    'description': info.get('description', '')
                }
            )
            if not cat.description:
                cat.description = info.get('description', '')
                cat.save()

            # Assign category image if not set
            if not cat.image and info.get('image_search'):
                img_path = self.find_image(info['image_search'])
                if img_path:
                    with open(img_path, 'rb') as f:
                        cat.image.save(info['image_search'], File(f), save=True)
            
            self.stdout.write(f"Category: {cat.name} ({'Created' if created else 'Updated'})")

        # 2. Importer les JSON
        JSON_FILES = [
            r"C:\Foodypedia\Jsons ingredients\ingredients_data_epices.json",
            r"C:\Foodypedia\Jsons ingredients\ingredients_data_suitelegumes.json",
            r"C:\Foodypedia\Jsons ingredients\ingredients_fruits.json"
        ]

        for json_path in JSON_FILES:
            if not os.path.exists(json_path):
                self.stdout.write(self.style.WARNING(f"File not found: {json_path}"))
                continue

            self.stdout.write(f"\n--- Importing from {os.path.basename(json_path)} ---")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if 'error' in item: continue
                    name = item.get('name')
                    if not name or name == "Non spécifié": continue

                    # Category matching
                    raw_cat = item.get('category', '').lower()
                    cat_slug = 'legume' if 'legume' in raw_cat or 'légume' in raw_cat else \
                               'fruit' if 'fruit' in raw_cat else \
                               'epice' if 'épice' in raw_cat or 'epice' in raw_cat else \
                               'poisson' if 'poisson' in raw_cat else \
                               'viande' if 'viande' in raw_cat else None
                    
                    if not cat_slug:
                        # Fallback create a slug
                        cat_slug = slugify(raw_cat) if raw_cat else 'divers'
                    
                    category, _ = IngredientCategory.objects.get_or_create(
                        slug=cat_slug,
                        defaults={'name': raw_cat.capitalize() or 'Divers'}
                    )

                    # Glossary
                    glossary_term = None
                    glossary_name = item.get('glossary_term')
                    if glossary_name and glossary_name != "Non spécifié":
                        glossary_term, _ = Glossaire.objects.get_or_create(
                            terme=glossary_name,
                            defaults={'definition': f"Définition pour {glossary_name}.", 'type_terme': 'N'}
                        )

                    # Ingredient
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

                    # Functional Categories
                    func_cats = item.get('functional_categories', [])
                    for fc_name in func_cats:
                        fc_slug = slugify(fc_name)
                        fc, _ = FunctionalCategory.objects.get_or_create(slug=fc_slug, defaults={'name': fc_name})
                        ingredient.functional_categories.add(fc)

                    # Image handling
                    image_filename = item.get('image_filename')
                    if not image_filename or '{{' in image_filename:
                        # Try to find an image matching the name
                        image_filename = f"{name}.jpg"
                    
                    if not ingredient.main_image:
                        img_path = self.find_image(image_filename)
                        if not img_path: # try png
                             img_path = self.find_image(image_filename.replace('.jpg', '.png'))
                        if not img_path: # try lowercase
                             img_path = self.find_image(image_filename.lower())
                        
                        if img_path:
                            with open(img_path, 'rb') as f_img:
                                ingredient.main_image.save(os.path.basename(img_path), File(f_img), save=True)

                    self.stdout.write(f"  [OK] {ingredient.name}")

    def find_image(self, filename):
        root_dir = settings.BASE_DIR.parent
        search_root = os.path.join(root_dir, 'static', 'ingredients_pics')
        for root, dirs, files in os.walk(search_root):
            if filename in files:
                return os.path.join(root, filename)
        
        # Case insensitive check
        for root, dirs, files in os.walk(search_root):
            for f in files:
                if f.lower() == filename.lower():
                    return os.path.join(root, f)
        return None
