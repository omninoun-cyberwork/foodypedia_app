from django.core.management.base import BaseCommand
from apps.ingredients.models import Ingredient, IngredientCategory
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Create representative mock ingredients for Foodypedia'

    def handle(self, *args, **options):
        # Data to create
        # Format: (Name, CategoryName, Description)
        MOCK_DATA = [
            ("Carotte des Sables", "Légume", "Une carotte au goût sucré, cultivée dans le sable de la côte Ouest."),
            ("Boeuf de Kobé", "Viande", "La viande la plus persillée et tendre du monde, originaire du Japon."),
            ("Saumon Écossais", "Poisson", "Saumon Label Rouge élevé dans les lochs d'Écosse."),
            ("Vanille Bourbon", "Épice", "Gousse grasse et parfumée de la Réunion, idéale pour la pâtisserie."),
            ("Pomme Granny Smith", "Fruit", "Pomme verte acide et croquante, parfaite pour la cuisson."),
            ("Basilic Grand Vert", "Herbe", "L'herbe royale de la cuisine méditerranéenne."),
            ("Beurre AOP Charentes", "Produit Laitier", "Beurre riche et onctueux pour le feuilletage."),
            ("Farine T55", "Céréale", "Farine blanche standard pour la pâtisserie courante."),
        ]

        # Ensure categories (loose matching)
        for name, cat_name, desc in MOCK_DATA:
            # Find category (startswith to allow 'Viande' matching 'Viandes & Volailles' found in populate script)
            cat = IngredientCategory.objects.filter(name__icontains=cat_name).first()
            if not cat:
                self.stdout.write(self.style.WARNING(f"Category '{cat_name}' not found for {name}. Skipping."))
                continue

            slug = slugify(name)
            obj, created = Ingredient.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': cat,
                    'description': desc,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {name}"))
            else:
                self.stdout.write(f"Exists: {name}")

        self.stdout.write(self.style.SUCCESS("Mock data creation complete."))
