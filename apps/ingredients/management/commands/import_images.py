import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.utils.text import slugify
from apps.ingredients.models import Ingredient

class Command(BaseCommand):
    help = 'Import images from static/ingredients_pics to Ingredient models matches by filename'

    def handle(self, *args, **options):
        # Chemin source
        # NOTE: settings.BASE_DIR pointe vers la racine du PROJET DJANGO (là où est manage.py normalement)
        # Mais dans certains setups, BASE_DIR est le dossier interne.
        # Ici, manage.py est à C:\Foodypedia\manage.py
        # Donc la racine est settings.BASE_DIR (si configuré correctement comme Path)
        
        # On assume que settings.BASE_DIR est C:\Foodypedia\foodypedia_project (d'après le fichier settings)
        # Donc on remonte d'un cran.
        root_dir = settings.BASE_DIR.parent
        source_dir = os.path.join(root_dir, 'static', 'ingredients_pics')
        
        if not os.path.exists(source_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {source_dir}"))
            return

        self.stdout.write(f"Scanning {source_dir}...")
        
        count_success = 0
        count_skipped = 0
        count_not_found = 0

        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # 1. Identifier le nom de l'ingrédient
                    name_part = os.path.splitext(filename)[0]
                    # Nettoyer le nom (ex: "Carotte_Bio" -> "carotte-bio")
                    candidate_slug = slugify(name_part)
                    
                    # 2. Chercher l'ingrédient
                    # On essaie par slug exact, ou par nom contenant le terme
                    ingredient = None
                    try:
                        ingredient = Ingredient.objects.get(slug=candidate_slug)
                    except Ingredient.DoesNotExist:
                        # Fallback: recherche approximative (dangereux si homonymes, mais utile)
                        # On cherche un ingrédient dont le slug COMMENCE par ce nom
                        matches = Ingredient.objects.filter(slug__startswith=candidate_slug)
                        if matches.count() == 1:
                            ingredient = matches.first()
                    
                    if ingredient:
                        if not ingredient.main_image:
                            file_path = os.path.join(root, filename)
                            with open(file_path, 'rb') as f:
                                ingredient.main_image.save(filename, File(f), save=True)
                                self.stdout.write(self.style.SUCCESS(f" [OK] Linked {filename} to {ingredient.name}"))
                                count_success += 1
                        else:
                            self.stdout.write(f" [SKIP] {ingredient.name} already has an image")
                            count_skipped += 1
                    else:
                        self.stdout.write(self.style.WARNING(f" [?] No match for {filename} (slug: {candidate_slug})"))
                        count_not_found += 1

        self.stdout.write(self.style.SUCCESS(f"\nImport finished! Linked: {count_success}, Skipped: {count_skipped}, Not Found: {count_not_found}"))
