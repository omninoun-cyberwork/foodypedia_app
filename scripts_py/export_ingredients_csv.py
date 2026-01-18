import csv
import os
import sys

# Setup Django environment
import django
sys.path.append('C:\\Foodypedia')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodypedia_project.settings.dev')
django.setup()

from apps.ingredients.models import Ingredient

def export_ingredients():
    ingredients = Ingredient.objects.select_related('category').all().order_by('category__name', 'name')
    output_path = 'C:\\Foodypedia\\liste_ingredients_verif.csv'
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['ID', 'Nom', 'Catégorie'])
        for i in ingredients:
            writer.writerow([i.id, i.name, i.category.name if i.category else 'Sans catégorie'])
            
    print(f"Export réussi : {len(ingredients)} ingrédients exportés dans {output_path}")

if __name__ == "__main__":
    export_ingredients()
