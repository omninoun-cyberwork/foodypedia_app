from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.recipes.models import RecipeCategory

class Command(BaseCommand):
    help = 'Seeds hierarchical recipe categories: Cuisine et gastronomie & Pâtisseries et desserts'

    def handle(self, *args, **options):
        # 1. Main Families
        families = [
            {'name': 'Cuisine et gastronomie', 'slug': 'cuisine-et-gastronomie'},
            {'name': 'Pâtisseries et desserts', 'slug': 'patisseries-et-desserts'},
        ]

        hierarchy = {
            'cuisine-et-gastronomie': [
                {
                    'name': 'Entrées',
                    'slug': 'entrees',
                    'children': [
                        {'name': 'Salades & Crudités', 'slug': 'salades-et-crudites'},
                        {'name': 'Entrées chaudes (soupes, feuilletés, gratins légers)', 'slug': 'entrees-chaudes'},
                    ]
                },
                {
                    'name': 'Plats principaux',
                    'slug': 'plats-principaux',
                    'children': [
                        {'name': 'Poissons & Fruits de mer', 'slug': 'poissons-et-fruits-de-mer'},
                        {'name': 'Viandes rouges (bœuf, agneau, gibier)', 'slug': 'viandes-rouges'},
                        {'name': 'Volailles & Lapin', 'slug': 'volailles-et-lapin'},
                        {'name': 'Pâtes & Riz (risottos, gratins, plats mijotés)', 'slug': 'pates-et-riz'},
                        {'name': 'Légumes & Garnitures (purées, poêlées, gratins)', 'slug': 'legumes-et-garnitures'},
                    ]
                },
                {
                    'name': 'Spécialités',
                    'slug': 'specialites',
                    'children': [
                        {'name': 'Œufs & Fromages (omelettes, quiches, gratins)', 'slug': 'oeufs-et-fromages'},
                        {'name': 'Pain & Pâtisserie salée (pizzas, fougasses, brioches salées)', 'slug': 'pain-et-patisserie-salee'},
                        {'name': 'Sauces & Condiments', 'slug': 'sauces-et-condiments'},
                    ]
                }
            ],
            'patisseries-et-desserts': [
                {
                    'name': 'Desserts classiques (gâteaux, crèmes, tartes)',
                    'slug': 'desserts-classiques',
                    'children': []
                },
                {
                    'name': 'Desserts glacés & fruités (sorbets, mousses, salades de fruits)',
                    'slug': 'desserts-glaces-et-fruites',
                    'children': []
                }
            ]
        }

        self.stdout.write(self.style.SUCCESS('Starting recipe category seeding...'))

        # Create Families
        family_objs = {}
        for fam in families:
            obj, created = RecipeCategory.objects.update_or_create(
                slug=fam['slug'],
                defaults={'name': fam['name']}
            )
            family_objs[fam['slug']] = obj
            msg = f'Family "{fam["name"]}" ' + ('created' if created else 'updated')
            self.stdout.write(msg)

        # Create Sub-categories (L2 and L3)
        for fam_slug, subcats in hierarchy.items():
            parent_family = family_objs[fam_slug]
            
            for sub in subcats:
                # Level 2
                l2_obj, created = RecipeCategory.objects.update_or_create(
                    slug=sub['slug'],
                    defaults={
                        'name': sub['name'],
                        'parent': parent_family
                    }
                )
                msg = f'  - Category "{sub["name"]}" ' + ('created' if created else 'updated')
                self.stdout.write(msg)

                # Level 3 (Children)
                for child in sub.get('children', []):
                    l3_obj, created = RecipeCategory.objects.update_or_create(
                        slug=child['slug'],
                        defaults={
                            'name': child['name'],
                            'parent': l2_obj
                        }
                    )
                    msg = f'    * Sub-category "{child["name"]}" ' + ('created' if created else 'updated')
                    self.stdout.write(msg)

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully!'))
