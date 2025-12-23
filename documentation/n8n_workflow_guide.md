# n8n AI Agent Prompt & JSON Template

To populate Foodypedia with high-quality data, use the following prompt and structure in your n8n workflow.

## 1. The AI Master Prompt

**System Instructions for the AI Node:**
> You are an expert gastronomic and botanical encyclopedia editor for "Foodypedia".
> Your task is to generate a valid JSON object for an ingredient based on a filename and a category provided in the input.
> 
> **Guidelines:**
> 1. **Language**: Strictly use French for all text fields (description, guides, etc.).
> 2. **Accuracy**: Research (using your internal knowledge) the scientific name and detailed culinary characteristics.
> 3. **Tone**: Educational, professional, and precise ("Wiki" style).
> 4. **Image Handling**: Use the provided `OriginalFileName` for the `image_filename` field.
> 5. **Hierarchy**: 
>    - The `category` should be a simple slug (e.g., 'poisson', 'legume', 'viande', 'epice').
>    - `functional_categories` should be a list of tags (e.g., ['proteine', 'mer', 'gras']).
> 
> **Output Format (JSON):**
> ```json
> {
>   "name": "Nom Commun (ex: Saumon Atlantique)",
>   "scientific_name": "Latin Name (ex: Salmo salar)",
>   "category": "slug-categorie",
>   "description": "Description détaillée...",
>   "seasonality": "Saison (ex: Printemps / Automne)",
>   "buying_guide": "Comment le choisir au marché...",
>   "storage_guide": "Comment le conserver...",
>   "prep_guide": "Comment le préparer avant cuisson...",
>   "nutrition_info": "Valeurs nutritionnelles clés...",
>   "texture": "Description de la texture (ex: Ferme et fondante)",
>   "image_filename": "nom_du_fichier_original.jpg",
>   "functional_categories": ["tag1", "tag2"],
>   "specific_data": {
>     "key1": "value1",
>     "key2": "value2"
>   }
> }
> ```

---

## 2. n8n Workflow Architecture

### Step 1: Drive Discovery
- **Node**: `Google Drive` (List Files)
- **Folder ID**: `1XwjYfchdludcsc9ExCP6z79PIf3w4Yqb`
- **Recursive**: `True`

### Step 2: Extraction & Filter (Code Node)
```javascript
const results = [];
for (const item of items) {
  const name = item.name.toLowerCase();
  // Filter out non-images and source files
  if (name.endsWith('.jpg') || name.endsWith('.png') || name.endsWith('.webp')) {
    if (!name.includes('.psd') && !name.includes('.exe')) {
       results.push({
         json: {
           original_filename: item.name,
           clean_name: item.name.split('.')[0].replace(/[_-]/g, ' '),
           // Guess category from parent folder name
           category_guess: item.parents && item.parents[0] // You might need a map node here
         }
       });
    }
  }
}
return results;
```

### Step 3: AI Generation
- **Node**: `AI Agent` or `OpenAI` node.
- **Input**: Pass the `clean_name` and `category_guess`.
- **Output**: JSON following the prompt above.

### Step 4: Storage
- **Node**: `Write Binary File` (Aggregate items first to create one JSON file per category).
