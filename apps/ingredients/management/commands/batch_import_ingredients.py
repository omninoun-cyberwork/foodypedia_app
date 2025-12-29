import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.conf import settings
from apps.ingredients.models import Ingredient, IngredientCategory, FunctionalCategory

class Command(BaseCommand):
    help = 'Importe des ingrédients depuis un fichier JSON (voir ingredients_import_template.json)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', 
            type=str, 
            help='Chemin vers un fichier JSON unique'
        )
        parser.add_argument(
            '--dir', 
            type=str, 
            help='Chemin vers un dossier contenant plusieurs fichiers JSON'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dir_path = options['dir']

        if not file_path and not dir_path:
            raise CommandError("Vous devez spécifier soit --file soit --dir.")

        files_to_import = []
        if file_path:
            if not os.path.exists(file_path):
                raise CommandError(f"Le fichier {file_path} n'existe pas.")
            files_to_import.append(file_path)
        
        if dir_path:
            if not os.path.exists(dir_path):
                raise CommandError(f"Le dossier {dir_path} n'existe pas.")
            for f in os.listdir(dir_path):
                if f.endswith('.json'):
                    files_to_import.append(os.path.join(dir_path, f))

        self.stdout.write(self.style.MIGRATE_HEADING(f"Traitement de {len(files_to_import)} fichier(s) JSON..."))

        for json_file in files_to_import:
            self.stdout.write(f"\n--- Importation de : {os.path.basename(json_file)} ---")
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    self.stdout.write(self.style.ERROR(f"Erreur de lecture dans {json_file}, ignoré."))
                    continue

                for item in data:
                    name = item.get('name')
                    if not name:
                        continue
                    
                    # Gestion Catégorie
                    cat_slug = item.get('category')
                    category = None
                    if cat_slug:
                        category, _ = IngredientCategory.objects.get_or_create(
                            slug=slugify(cat_slug),
                            defaults={'name': cat_slug.capitalize()}
                        )
                    
                    # Gestion Glossaire (Lien facultatif avec l'Atlas)
                    glossary_term = None
                    glossary_name = item.get('glossary_term')
                    if glossary_name:
                        from apps.atlas.models import Glossaire
                        glossary_term, _ = Glossaire.objects.get_or_create(
                            terme=glossary_name,
                            defaults={'definition': f"Définition automatique pour {glossary_name}. À compléter."}
                        )

                    # Création / Update Ingrédient
                    ingredient, created = Ingredient.objects.update_or_create(
                        name=name,
                        defaults={
                            'slug': slugify(name),
                            'scientific_name': item.get('scientific_name', ''),
                            'description': item.get('description', ''),
                            'category': category,
                            'glossary_term': glossary_term,
                            'seasonality': item.get('seasonality', ''),
                            'buying_guide': item.get('buying_guide', ''),
                            'storage_guide': item.get('storage_guide', ''),
                            'prep_guide': item.get('prep_guide', ''),
                            'nutrition_info': item.get('nutrition_info', ''),
                            'texture': item.get('texture', ''),
                            'specific_data': item.get('specific_data', {}),
                            'tags': item.get('tags', []),
                            'image_filename': item.get('image_filename', ''),
                        }
                    )

                    # Gestion ManyToMany (Functional Categories)
                    func_cats = item.get('functional_categories', [])
                    if func_cats:
                        for fc_name in func_cats:
                            slug = slugify(fc_name)
                            fc, _ = FunctionalCategory.objects.get_or_create(
                                slug=slug,
                                defaults={'name': fc_name.replace('-', ' ').capitalize()}
                            )
                            ingredient.functional_categories.add(fc)

                    # NOUVEAU : Gestion de l'image principale avec recherche récursive
                    image_filename = item.get('image_filename')
                    if image_filename and not ingredient.main_image:
                        from django.core.files import File
                        root_dir = settings.BASE_DIR.parent  # BASE_DIR est dans foodypedia_project/, static est à la racine
                        search_root = os.path.join(root_dir, 'static', 'ingredients_pics')
                        
                        # Recherche récursive du fichier
                        img_path = None
                        for root, dirs, files in os.walk(search_root):
                            if image_filename in files:
                                img_path = os.path.join(root, image_filename)
                                break
                        
                        if img_path and os.path.exists(img_path):
                            with open(img_path, 'rb') as f_img:
                                ingredient.main_image.save(image_filename, File(f_img), save=True)
                    
                    # NOUVEAU : Galerie d'images (variations)
                    images_list = item.get('images', []) # Liste de noms de fichiers
                    if images_list:
                        from django.core.files import File
                        from apps.ingredients.models import IngredientImage
                        root_dir = settings.BASE_DIR.parent
                        for idx, img_name in enumerate(images_list):
                            # On évite d'ajouter si déjà présent (basé sur le nom du fichier)
                            if not IngredientImage.objects.filter(ingredient=ingredient, image__icontains=img_name).exists():
                                img_path = os.path.join(root_dir, 'static', 'ingredients_pics', img_name)
                                if os.path.exists(img_path):
                                    with open(img_path, 'rb') as f_img:
                                        new_img = IngredientImage(ingredient=ingredient, caption=img_name.split('.')[0], order=idx)
                                        new_img.image.save(img_name, File(f_img), save=True)

                    verb = "Créé" if created else "Mis à jour"
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {verb} : {ingredient.name}"))

        self.stdout.write(self.style.SUCCESS("\nImportation globale terminée ! 🥕"))
