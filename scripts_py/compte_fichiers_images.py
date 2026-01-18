import os
import csv

def count_files_in_subdirs():
    root_dir = r'C:\Foodypedia\static\ingredients_pics'
    output_path = r'C:\Foodypedia\compte_fichiers_images.csv'
    
    if not os.path.exists(root_dir):
        print(f"Erreur : Le dossier {root_dir} n'existe pas.")
        return

    data = []
    
    # Parcourir chaque élément du dossier racine
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        
        # Si c'est un dossier
        if os.path.isdir(item_path):
            # Compter uniquement les fichiers à l'intérieur
            file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
            data.append([item, file_count])
            
    # Trier par nom de dossier
    data.sort()
    
    # Écrire dans le fichier CSV
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Nom Dossier', 'Nombre de Fichiers'])
        writer.writerows(data)
        
    print(f"Export terminé : {len(data)} dossiers traités. Fichier : {output_path}")

if __name__ == "__main__":
    count_files_in_subdirs()
