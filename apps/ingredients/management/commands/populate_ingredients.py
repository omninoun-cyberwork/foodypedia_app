from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.ingredients.models import IngredientCategory, FunctionalCategory, Label, CulinaryUse, IngredientFamily
from apps.recipes.models import RecipeCategory

class Command(BaseCommand):
    help = 'Peuple la base de données avec les catégories et référentiels initiaux pour Foodypedia'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Début du peuplement de la base de données...'))

        # ---------------------------------------------------------------------
        # 1. Catégories Principales (Nature du produit)
        # ---------------------------------------------------------------------
        categories_data = [
            # Viandes & Protéines Animales
            ("Viande Bovine", "fa-cow"),
            ("Viande Ovine", "fa-sheep"), # Mouton/Agneau
            ("Viande Porcine", "fa-piggy-bank"),
            ("Volaille", "fa-drumstick-bite"),
            ("Gibier", "fa-paw"),
            ("Charcuterie", "fa-bacon"),
            # Mer
            ("Poisson", "fa-fish"),
            ("Crustacé", "fa-crab"),
            ("Mollusque & Coquillage", "fa-water"),
            # Végétal
            ("Légume", "fa-carrot"),
            ("Fruit", "fa-apple-alt"),
            ("Herbe Aromatique", "fa-seedling"),
            ("Épice", "fa-pepper-hot"),
            ("Champignon", "fa-cloud"),
            ("Céréale & Grain", "fa-wheat"),
            ("Légumineuse", "fa-peas"), # Haricots, lentilles
            ("Fruit à coque & Graine", "fa-leaf"), # Noix, amandes
            # Crèmerie
            ("Produit Laitier", "fa-cheese"),
            ("Oeuf & Ovoproduit", "fa-egg"),
            # Épicerie / Autre
            ("Corps Gras", "fa-oil-can"), # Huiles, Beurre
            ("Condiment & Sauce", "fa-bottle-droplet"), # Vinaigre, moutarde
            ("Sucre & Produit Sucrant", "fa-cube"),
            ("Chocolat & Cacao", "fa-cookie"),
            ("Additif & Texturant", "fa-flask"),
            ("Boisson & Liquide", "fa-wine-bottle"), # Vins pour cuisine, bouillons
        ]

        self.stdout.write("--- Création des Catégories Principales ---")
        for name, icon in categories_data:
            cat, created = IngredientCategory.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + {name}"))
            else:
                self.stdout.write(f"  = {name} (existe déjà)")

        # ---------------------------------------------------------------------
        # 2. Catégories Fonctionnelles (Usage)
        # ---------------------------------------------------------------------
        func_cats_data = [
            # Pâtisserie
            "Pâtisserie", "Boulangerie", "Confiserie", "Chocolaterie",
            # Rôles techniques
            "Texturant", "Gélifiant", "Épaississant", "Émulsifiant", "Levant", "Conservateur",
            # Rôles nutritionnels / culinaires
            "Féculent", "Protéine", "Fibre", 
            "Aromatique", "Colorant", "Assaisonnement",
            "Garniture", "Décoration",
            # Types de cuisine
            "Cuisine Asiatique", "Cuisine Méditerranéenne",
        ]

        self.stdout.write("\n--- Création des Catégories Fonctionnelles ---")
        for name in func_cats_data:
            cat, created = FunctionalCategory.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + {name}"))

        # ---------------------------------------------------------------------
        # 3. Labels
        # ---------------------------------------------------------------------
        labels_data = ["Bio (AB)", "Label Rouge", "AOP", "AOC", "IGP", "STG", "Halal", "Casher", "Sans Gluten", "Vegan"]
        
        self.stdout.write("\n--- Création des Labels ---")
        for name in labels_data:
            obj, created = Label.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + {name}"))

        # ---------------------------------------------------------------------
        # 4. Usages Culinaires
        # ---------------------------------------------------------------------
        uses_data = [
            "Cru", "Cuit", "Marinade", "Infusion", "Rôti", "Grillé", "Poché", "Vapeur", 
            "Sauté", "Frit", "Braisé", "Confit", "Fumé", "Séché", "Fermenté",
            "Liaison", "Finition", "Glaçage", "Farce"
        ]

        self.stdout.write("\n--- Création des Usages Culinaires ---")
        for name in uses_data:
            obj, created = CulinaryUse.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + {name}"))

        # ---------------------------------------------------------------------
        # 5. Familles (Exemples scientifiques)
        # ---------------------------------------------------------------------
        families_data = [
            "Solanacées (Tomates, Aubergines...)", "Cucurbitacées (Courges...)", "Alliacées (Ail, Oignon...)",
            "Agrumes", "Fruits Rouges", "Fruits à Noyau", "Fruits à Pépins", "Exotiques",
            "Poissons Blancs", "Poissons Gras (Bleus)", "Poissons Plats",
            "Bovidés", "Gallinacés",
            "Ombellifères (Carotte, Anis...)",
        ]

        self.stdout.write("\n--- Création des Familles ---")
        for name in families_data:
            obj, created = IngredientFamily.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + {name}"))

        # ---------------------------------------------------------------------
        # 6. Catégories de RECETTES (Hiérarchie)
        # ---------------------------------------------------------------------
        recipe_structure = {
            "Cuisine Salée": [
                "Entrées Froides", "Entrées Chaudes", "Potages & Soupes",
                "Plats de Viande", "Plats de Poisson", "Plats Végétariens",
                "Garnitures & Accompagnements",
                "Sauces Salées & Coulis", "Bases & Fonds",
            ],
            "Pâtisserie & Sucré": [
                "Pâtes de Base", "Crèmes & Appareils", "Biscuits & Gâteaux de Voyage",
                "Entremets & Petits Gâteaux", "Tartes & Tartelettes",
                "Confiserie & Chocolat", "Glaces & Sorbets",
                "Sauces Sucrées & Coulis", "Desserts à l'assiette",
                "Viennoiserie & Boulangerie"
            ],
            "Cocktails & Boissons": [
                "Cocktails avec Alcool", "Cocktails sans Alcool (Mocktails)", 
                "Boissons Chaudes", "Jus & Smoothies"
            ]
        }

        self.stdout.write("\n--- Création des Catégories de Recettes ---")
        for parent_name, sub_cats in recipe_structure.items():
            parent, _ = RecipeCategory.objects.get_or_create(
                slug=slugify(parent_name),
                defaults={'name': parent_name}
            )
            for sub_name in sub_cats:
                RecipeCategory.objects.get_or_create(
                    slug=slugify(sub_name),
                    defaults={'name': sub_name, 'parent': parent}
                )
                self.stdout.write(self.style.SUCCESS(f"  + {parent_name} > {sub_name}"))

        self.stdout.write(self.style.SUCCESS('\nsuccès : Base de données initialisée avec les référentiels V2 ! 🚀'))
