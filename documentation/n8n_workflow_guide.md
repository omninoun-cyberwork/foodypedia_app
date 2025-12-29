# n8n AI Agent Prompt & JSON Template

To populate Foodypedia with high-quality data, use the following prompt and structure in your n8n workflow.

## 1. The AI Master Prompt

**System Instructions for the AI Node:**
> You are an expert gastronomic and botanical encyclopedia editor for "Foodypedia".
> Your task is to generate a valid JSON object for an ingredient based on a filename and a category provided in the input.
> 
> **Guidelines for Excellence:**
> 1. **Language**: Full French (Botanical precision, professional culinary tone).
> 2. **Scientific Mapping**: Research `scientific_name` and link to `glossary_term` (the root name of the ingredient in a technical dictionary).
> 3. **Structure**: 
>    - `category`: Must be one of our slugs: `legume`, `poisson`, `viande`, `epice`, `fromage`, `pates`, `fruit`, `cremerie`.
>    - `functional_categories`: Professional usage tags (e.g., `texturant`, `aromatisation`, `base-sauce`, `garniture`).
>    - `tags`: AI-generated creative tags for SEO and internal search.
> 4. **Specific Data**: Deep dive into technical details (e.g., for cheese: `milk_type`, `pasteurization`, `maturation`).
> 
> **Standardized JSON Output:**
> ```json
> {
>   "name": "Nom de l'ingrédient",
>   "scientific_name": "Nom latin",
>   "glossary_term": "Terme racine (ex: Citron)",
>   "category": "slug-categorie",
>   "description": "Texte encyclopédique...",
>   "seasonality": "Mois ou périodes",
>   "buying_guide": "Conseils d'expert...",
>   "storage_guide": "Conservation pro...",
>   "prep_guide": "Techniques de préparation...",
>   "nutrition_info": "Valeurs clés...",
>   "texture": "Description tactile/gustative",
>   "image_filename": "nom_original.jpg",
>   "functional_categories": ["usage1", "usage2"],
>   "tags": ["tag-ia-1", "tag-ia-2"],
>   "specific_data": {
>     "info_cle_1": "valeur",
>     "info_cle_2": "valeur"
>   }
> }
> ```

---

## 2. n8n Workflow Architecture

### Step 1: Drive Discovery (Configuration Cruciale)
Si vous avez une erreur "Forbidden" ou "transferOwnership", c'est que vous n'utilisez pas la bonne opération.

**Paramètres du noeud Google Drive :**
1. **Resource** : `File` (et non `Folder` ! Dans Google Drive API, un dossier est aussi un fichier).
2. **Operation** : `List`
3. **Filtres (Options)** :
   - **Folder ID** : Copiez l'ID de votre dossier "Légumes" ici.
   - **Recursive** : `True` (pour aller chercher dans les sous-dossiers).

> [!WARNING]
> N'utilisez **JAMAIS** l'opération `Share` ou `Permissions` pour lire des fichiers. Ces opérations servent à modifier qui a accès au dossier, ce qui demande des droits d'administration très élevés.

### Step 2: Extraction & Filter (Code Node)
Ce code prépare les données pour l'IA. Pour changer de catégorie, modifiez la ligne `category_guess`.

```javascript
const results = [];
for (const item of items) {
  const file = item.json;
  const name = file.name.toLowerCase();
  
  // On ne garde que les images
  if (name.endsWith('.jpg') || name.endsWith('.png') || name.endsWith('.webp')) {
     results.push({
       json: {
         original_filename: file.name,
         // Nettoyage du nom (ex: "saumon_bio.jpg" -> "saumon bio")
         clean_name: file.name.split('.')[0].replace(/[_-]/g, ' '),
         
         // 💡 CHANGEZ ICI SELON VOTRE DOSSIER : 
         // 'legume', 'poisson', 'viande', 'fromage', 'pates', 'épice'
         category_guess: "legume" 
       }
     });
  }
}
return results;
```

---

## 3. Déclenchement (Trigger)

Pour peupler la base de données initialement, vous n'avez pas besoin d'un trigger automatique "temps réel". 

1. **Trigger Manuel** : Cliquez simplement sur **"Execute Workflow"** en bas de l'écran n8n après avoir configuré vos dossiers. C'est la méthode la plus sûre pour contrôler ce que vous importez.
2. **Trigger Google Drive (Optionnel)** : Si vous voulez que Foodypedia se mette à jour dès que vous déposez une photo dans un dossier, ajoutez un noeud **"Google Drive Trigger"** au début, configuré sur "File Created".

### Step 3: AI Generation (OpenAI / Chat GPT)
Si vous avez une erreur "404 - This is a chat model", suivez ce réglage :

1. **Resource** : `Chat` (C'est le point crucial !).
2. **Operation** : `Message` (ou `Complete` selon la version, mais dans la ressource Chat).
3. **Model** : `gpt-4o` or `gpt-3.5-turbo`.
4. **Prompt** : `Génère la fiche pour : {{ $json.clean_name }} (Catégorie : {{ $json.category_guess }})`

### Step 4: Final Aggregation (Merge into one JSON file)
Pour regrouper les 25+ ingrédients générés par l'IA en un seul fichier prêt à importer :

1. Ajoutez un noeud **Code** à la fin du flux.
2. Collez ce script (il fusionne tout et crée le fichier binaire) :

```javascript
const allIngredients = [];
for (const item of $input.all()) {
  try {
    const ingredient = JSON.parse(item.json.message.content);
    allIngredients.push(ingredient);
  } catch (e) {
    // Ignore malformed items
  }
}

const binaryData = await helpers.prepareBinaryData(
  Buffer.from(JSON.stringify(allIngredients, null, 2)),
  'ingredients_data.json',
  'application/json'
);

return [
  {
    json: { message: "Fichier prêt !", total: allIngredients.length },
    binary: { data: binaryData }
  }
];
```

3. **Exécution** : Cliquez sur "Execute Workflow", attendez la fin, puis téléchargez le fichier via l'onglet **Binary** du dernier noeud.

---

## 4. Importation dans Foodypedia
Une fois le fichier `ingredients_data.json` téléchargé :
1. Copiez-le dans `C:\Foodypedia\imports\`.
2. Lancez la commande Django :
`python manage.py batch_import_ingredients --file imports/ingredients_data.json`
