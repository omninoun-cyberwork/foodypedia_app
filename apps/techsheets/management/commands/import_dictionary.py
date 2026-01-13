import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.techsheets.models import Technique

class Command(BaseCommand):
    help = 'Import culinary dictionary from JSON'

    def handle(self, *args, **options):
        # File path provided by user
        json_file_path = r"C:\Foodypedia\Termes Culinaires.json"
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return

        self.stdout.write(f'Reading {json_file_path}...')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            techniques_list = data.get('techniques', [])
            self.stdout.write(f'Found {len(techniques_list)} items.')

            created_count = 0
            updated_count = 0

            for item in techniques_list:
                nom = item.get('nom')
                if not nom:
                    continue
                    
                slug = item.get('slug') or slugify(nom)
                
                # Extract fields
                defaults = {
                    'domaine': item.get('domaine', 'Cuisine'),
                    'definition': item.get('definition', ''),
                    'objectif': item.get('objectif', []),
                    'principe': item.get('principe', ''),
                    'exemples': item.get('exemples', {}),
                    'erreurs_frequentes': item.get('erreurs_frequentes', []),
                    'niveau': item.get('niveau', []),
                }

                obj, created = Technique.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'nom': nom,
                        **defaults
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Import Complete: {created_count} created, {updated_count} updated.'))
            
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON Error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
