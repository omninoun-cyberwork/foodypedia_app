import json
import os
import glob

source_dir = r"C:\Foodypedia\Fichiers techniques de cuisine"
json_files = glob.glob(os.path.join(source_dir, "*.json"))

print(f"--- Diagnostic Report ---")
total_expected = 0

for file_path in json_files:
    # Skip the combined file if it exists
    if "all_techniques_combined.json" in file_path:
        continue
        
    print(f"\nFile: {os.path.basename(file_path)}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try parsing
            data = json.loads(content)
            
            if "techniques" in data:
                count = len(data["techniques"])
                print(f"  -> Valid JSON. Count: {count} techniques.")
                total_expected += count
                # Optional: Print first technique name to verify unique content
                if count > 0:
                    print(f"  -> First item: {data['techniques'][0].get('nom', 'Unknown')}")
            else:
                print(f"  -> WARNING: Key 'techniques' not found. Keys: {list(data.keys())}")
                
    except json.JSONDecodeError as e:
        print(f"  -> ERROR: Invalid JSON. {e}")
    except Exception as e:
        print(f"  -> ERROR: {e}")

print(f"\n--- Total Expected: {total_expected} ---")
