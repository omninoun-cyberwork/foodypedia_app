
import os
import sys
import django

# Setup path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodypedia_project.settings.dev')
django.setup()

from apps.ingredients.models import Ingredient, IngredientCategory
import json

def run_cleanup():
    # 1. Identify category
    try:
        category = IngredientCategory.objects.get(name='Fromages')
    except IngredientCategory.DoesNotExist:
        print("Category 'Fromages' not found")
        # Fallback to check if name is slightly different
        category = IngredientCategory.objects.filter(name__icontains='Fromage').first()
        if not category:
            return
        print(f"Found category: {category.name}")

    # 2. Deletions
    to_delete = [
        "Boursin",
        "Boursin Ail et Fines Herbes",
        "Fromage fondu type process",
        "Halloumi à la Menthe",
        "Skyr",
        "Labneh",
        "Quark",
        "Queso Blanco",
        "Chaubier",
        "Tomme aux Fleurs",
        "Tomme de Corse",
        "Bondon",
        "Boulette d'Avesnes",
        "Boursault",
        "Fromage de Herve",
        "Graviera",
        "Langres",
        "Leicester Rouge",
        "Manouri",
        "Picodon",
        "Pouligny-Saint-Pierre",
        "Selles-sur-Cher",
        "Livarot" # Also not in initial list based on comparison
    ]
    
    deleted_count = 0
    for name in to_delete:
        qs = Ingredient.objects.filter(category=category, name=name)
        if qs.exists():
            deleted_count += qs.count()
            qs.delete()
            print(f"Deleted: {name}")

    # 3. Merges (Updated with extras found)
    merges = [
        ("Cantal Entre-deux", "Cantal"),
        ("Cantal Jeune", "Cantal"),
        ("Gorgonzola Dolce", "Gorgonzola Piccante"),
        ("Gorgonzola Cremoso", "Gorgonzola Piccante"),
        ("Gorgonzola", "Gorgonzola Piccante"), # Extra
        ("Gouda", "Gouda Vieux"),
        ("Manchego", "Manchego Viejo"),
        ("Manchego Curado", "Manchego Viejo"),
        ("Mimolette", "Mimolette Vieille"),
        ("Morbier Jeune", "Morbier"),
        ("Morbier Vieux", "Morbier"),
        ("Ossau-Iraty Vieux", "Ossau-Iraty"),
        ("Sainte-Maure de Touraine", "Sainte-Maure de Touraine Affiné"), # Fixed name
        ("Sainte-Maure de Touraine (non affinée)", "Sainte-Maure de Touraine Affiné"),
        ("Saint-Nectaire Laitier", "Saint-Nectaire"),
        ("Reblochon Laitier", "Reblochon"),
        ("Mascarpone (2)", "Mascarpone"), # Extra
        ("Valençay (2)", "Valençay"), # Extra
        ("Provolone Dolce", "Provolone"), # Rule 3: 1 type = 1 entry
        ("Brie de Meaux Truffé", "Brie de Meaux"), # Variants aromatisées
        ("Saint-Félicien Tentation", "Saint-Félicien"),
    ]

    for variant_name, reference_name in merges:
        variant = Ingredient.objects.filter(category=category, name=variant_name).first()
        reference = Ingredient.objects.filter(category=category, name=reference_name).first()

        if variant:
            if reference:
                print(f"Merging {variant_name} into {reference_name} (deleting variant)")
                variant.delete()
            else:
                print(f"Renaming {variant_name} to {reference_name}")
                variant.name = reference_name
                variant.save()
    
    # 4. Final list and CSV tracking
    output_path = os.path.join('scripts_py', 'final_cheese_list.txt')
    csv_path = os.path.join('scripts_py', 'liste_fromages_photos.csv')
    
    country_map = {
        "Appenzeller": "Suisse", "Burrata": "Italie", "Cabrales": "Espagne", 
        "Edam": "Pays-Bas", "Emmental": "Suisse/France", "Feta AOP": "Grèce", 
        "Gorgonzola Piccante": "Italie", "Gouda Vieux": "Pays-Bas", 
        "Grana Padano": "Italie", "Graviera": "Grèce", "Gruyère Suisse": "Suisse", 
        "Halloumi": "Chypre", "Havarti": "Danemark", "Labneh": "Moyen-Orient", 
        "Leicester Rouge": "Royaume-Uni", "Maasdam": "Pays-Bas", 
        "Manchego Viejo": "Espagne", "Manouri": "Grèce", "Mascarpone": "Italie", 
        "Parmigiano Reggiano 24 mois": "Italie", "Pecorino Romano": "Italie", 
        "Pecorino Toscano": "Italie", "Provolone": "Italie", "Quark": "Allemagne", 
        "Queso Blanco": "Amérique Latine", "Ricotta di Bufala": "Italie", 
        "Stilton": "Royaume-Uni", "Taleggio": "Italie", "Tête de Moine": "Suisse", 
        "Vacherin Fribourgeois": "Suisse"
    }

    import csv
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['Article', 'Pays_Origine', 'Image_Trouvee']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        # 4. Load JSON image names for mapping
        json_path = os.path.join('JSON des ingredients', 'Fromages.json')
        json_image_map = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as jf:
                    json_data = json.load(jf)
                    for item in json_data:
                        if 'name' in item and 'image_filename' in item:
                            json_image_map[item['name']] = item['image_filename']
            except Exception as e:
                print(f"Error loading JSON: {e}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("--- LISTE DES FROMAGES PAR PAYS ---\n")
            all_cheeses = Ingredient.objects.filter(category=category).order_by('name')
            
            # Map for reverse lookup (Reference -> Original JSON name) if needed
            reverse_merges = {}
            for variant, reference in merges:
                if reference not in reverse_merges:
                    reverse_merges[reference] = []
                reverse_merges[reference].append(variant)

            for cheese in all_cheeses:
                # 1. Check database for countries
                db_countries = [p.nom_fr for p in cheese.origins_countries.all()]
                
                # 2. Heuristic for country determination
                if db_countries:
                    country = ", ".join(db_countries)
                elif cheese.name in country_map:
                    country = country_map[cheese.name]
                else:
                    # Check for keywords in name if still no country
                    known_origins = {
                        "Italie": ["Mozzarella", "Parmesan", "Ricotta"],
                        "Grèce": ["Feta"],
                        "Suisse": ["Gruyère"],
                        "Pays-Bas": ["Gouda", "Edam"],
                        "Espagne": ["Manchego"]
                    }
                    country = "France" # Default for this dataset
                    for c_name, keywords in known_origins.items():
                        if any(k in cheese.name for k in keywords):
                            country = c_name
                            break
                
                # 3. Retrieve image filename
                image_name = ""
                
                # Priority 1: Check database (ManyToMany images)
                first_image = cheese.images.first()
                if first_image and first_image.file:
                    image_name = os.path.basename(first_image.file.name)
                
                # Priority 2: Check JSON by Exact Name
                if not image_name:
                    image_name = json_image_map.get(cheese.name, "")
                
                # Priority 3: Check JSON by Original Merged Name
                if not image_name and cheese.name in reverse_merges:
                    for original_name in reverse_merges[cheese.name]:
                        if original_name in json_image_map:
                            image_name = json_image_map[original_name]
                            break
                
                f.write(f"[{country}] {cheese.name}\n")
                writer.writerow({
                    'Article': cheese.name, 
                    'Pays_Origine': country, 
                    'Image_Trouvee': image_name
                })
    
    print(f"Final list written to {output_path}")
    print(f"CSV list written to {csv_path}")

if __name__ == "__main__":
    run_cleanup()
