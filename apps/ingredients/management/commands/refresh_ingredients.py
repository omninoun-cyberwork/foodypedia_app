import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.core.files import File
from apps.ingredients.models import Ingredient, IngredientCategory, FunctionalCategory, IngredientImage
from apps.atlas.models import Glossaire

class Command(BaseCommand):
    help = 'Supprime tout et recharge les ingrédients depuis le dossier JSON des ingredients'

    def handle(self, *args, **options):
        json_dir = r"C:\Foodypedia\JSON des ingredients"
        pics_dir = r"C:\Foodypedia\static\ingredients_pics"

        if not os.path.exists(json_dir):
            self.stdout.write(self.style.ERROR(f"Dossier JSON introuvable : {json_dir}"))
            return

        # 1. Nettoyage TOTAL
        self.stdout.write(self.style.WARNING("--- NETTOYAGE COMPLET DES TABLES INGRÉDIENTS ---"))
        IngredientImage.objects.all().delete()
        Ingredient.objects.all().delete()
        IngredientCategory.objects.all().delete()
        FunctionalCategory.objects.all().delete()
        self.stdout.write("Tables vidées avec succès.")

        # 2. Itération sur les fichiers JSON
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        total_imported = 0
        processed_names = set()
        processed_slugs = set()

        for filename in json_files:
            category_name = os.path.splitext(filename)[0]
            category_slug = slugify(category_name)
            
            self.stdout.write(f"\n--- Traitement de la catégorie : {category_name} ---")
            
            # Création de la catégorie
            category, _ = IngredientCategory.objects.get_or_create(
                slug=category_slug,
                defaults={'name': category_name}
            )

            file_path = os.path.join(json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur de lecture {filename}: {e}"))
                continue

            if not isinstance(data, list):
                self.stdout.write(self.style.WARNING(f"Format invalide pour {filename} (liste attendue)"))
                continue

            first_img_path = None

            for item in data:
                if not isinstance(item, dict) or 'name' not in item:
                    continue

                name = item['name']
                
                # Gestion des doublons de noms
                base_name = name
                counter = 2
                while name.lower() in processed_names:
                    name = f"{base_name} ({counter})"
                    counter += 1
                processed_names.add(name.lower())

                # Gestion des doublons de slugs
                base_slug = slugify(name)
                if not base_slug: base_slug = "ingredient"
                slug = base_slug
                counter = 2
                while slug in processed_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                processed_slugs.add(slug)

                self.stdout.write(f"  Importation de : {name}")

                # Glossaire
                glossary_term = None
                g_name = item.get('glossary_term')
                if g_name and g_name != "Non spécifié":
                    glossary_term, _ = Glossaire.objects.get_or_create(
                        terme=g_name,
                        defaults={'definition': f"Définition pour {g_name}.", 'type_terme': 'N'}
                    )

                # Ingrédient
                ingredient = Ingredient.objects.create(
                    name=name,
                    slug=slug,
                    scientific_name=item.get('scientific_name', '') or '',
                    description=item.get('description', '') or '',
                    category=category,
                    glossary_term=glossary_term,
                    seasonality=item.get('seasonality', '') or '',
                    buying_guide=item.get('buying_guide', '') or '',
                    storage_guide=item.get('storage_guide', '') or '',
                    prep_guide=item.get('prep_guide', '') or '',
                    nutrition_info=item.get('nutrition_info', '') or '',
                    texture=item.get('texture', '') or '',
                    specific_data=item.get('specific_data', {}),
                    tags=item.get('tags', []),
                    image_filename=item.get('image_filename', '') or ''
                )

                # Categories fonctionnelles
                func_cats = item.get('functional_categories', [])
                for fc_name in func_cats:
                    fc_slug = slugify(fc_name)
                    fc, _ = FunctionalCategory.objects.get_or_create(slug=fc_slug, defaults={'name': fc_name})
                    ingredient.functional_categories.add(fc)

                # Image principale
                img_name = item.get('image_filename')
                if img_name:
                    img_path = self.find_image(img_name, pics_dir)
                    if img_path:
                        with open(img_path, 'rb') as f_img:
                            ingredient.main_image.save(os.path.basename(img_path), File(f_img), save=True)
                        if not first_img_path:
                            first_img_path = img_path

                # Images variantes
                variant_images = item.get('variant_images', [])
                for v_img_name in variant_images:
                    v_img_path = self.find_image(v_img_name, pics_dir)
                    if v_img_path:
                        with open(v_img_path, 'rb') as f_v:
                            v_img_obj = IngredientImage(ingredient=ingredient, caption=v_img_name)
                            v_img_obj.image.save(os.path.basename(v_img_path), File(f_v), save=True)

                total_imported += 1

            # Assigner une image à la catégorie si elle n'en a pas
            if first_img_path and not category.image:
                with open(first_img_path, 'rb') as f_cat:
                    category.image.save(os.path.basename(first_img_path), File(f_cat), save=True)

        self.stdout.write(self.style.SUCCESS(f"\nTerminé ! {total_imported} ingrédients importés."))

    def find_image(self, filename, search_root):
        if not filename: return None
        # Recherche directe
        target = os.path.join(search_root, filename)
        if os.path.exists(target):
            return target
            
        # Recherche insensible à la casse
        try:
            files = os.listdir(search_root)
            for f in files:
                if f.lower() == filename.lower():
                    return os.path.join(search_root, f)
        except:
            pass
            
        return None
