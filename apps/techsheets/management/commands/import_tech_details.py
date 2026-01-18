import json
from django.core.management.base import BaseCommand
from apps.techsheets.models import Technique

class Command(BaseCommand):
    help = 'Import Technical Sheets Details (Phases, Materiel) from JSON'

    def handle(self, *args, **options):
        file_path = 'vue_detaillée_techniques.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            items = data.get('fiches_techniques_detaillees', [])
            count = 0
            
            for item in items:
                slug = item.get('slug')
                try:
                    technique = Technique.objects.get(slug=slug)
                    
                    # Update fields
                    technique.reference_id = item.get('reference_cap')
                    technique.phases = item.get('phases')
                    technique.materiel = item.get('materiel')
                    technique.is_active_techsheet = True
                    
                    # Deduce Category from Ref ID (Simple heuristic)
                    ref = item.get('reference_cap', '')
                    if 'PB' in ref:
                        technique.categorie_cap = 'BASE'
                    elif 'C' in ref and 'S' not in ref: # Not fully accurate but a start
                         technique.categorie_cap = 'CUISSON'
                    elif 'FS' in ref:
                        technique.categorie_cap = 'SAUCE'
                    
                    technique.save()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated: {technique.nom}'))
                    
                except Technique.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Technique not found for slug: {slug}'))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} techniques.'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
