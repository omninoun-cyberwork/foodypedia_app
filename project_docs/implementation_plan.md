# Ingredient Detail Page & UI Refinement

The goal is to provide a rich, encyclopedic view for each ingredient and optimize the grid display.

## Proposed Changes

### [Frontend] UI Refinements

#### [MODIFY] [ingredients/page.tsx](file:///c:/Foodypedia/frontend/src/app/ingredients/page.tsx)
- Smaller, more compact ingredient cards.
- Add "Cliquer pour fiche détaillée" hint on cards.
- Redesign detail page at /ingredients/[slug] with a 3-column layout.

### [Frontend] Detail Page

#### [MODIFY] [ingredients/[slug]/page.tsx](file:///c:/Foodypedia/frontend/src/app/ingredients/[slug]/page.tsx)
- Redesign for a 3-column layout on Desktop (`lg:grid-cols-3`):
    - **Column 1 (Side)**: Image (format carré réduit), Nom Scientifique, Saisonnalité.
    - **Column 2 (Main)**: Story & Guides (Description, Achat, Conservation, Préparation).
    - **Column 3 (Technical)**: Données Nutritionnelles, Tableau JSON (Spécifique).
- Increase font sizes for technical and bottom sections for better readability.
- Add a direct link to Django Admin (visible to staff/admin only) if helpful for management.

## Phase 3: Recipes & The AI Brain

- **2-Tier Hierarchical Filtering**: Implement a sidebar supporting the main families and their sub-categories:
    - **Cuisine et gastronomie**
        - **Entrées**
            - Salades & Crudités
            - Entrées chaudes (soupes, feuilletés, gratins légers)
        - **Plats principaux**
            - Poissons & Fruits de mer
            - Viandes rouges (bœuf, agneau, gibier)
            - Volailles & Lapin
            - Pâtes & Riz (risottos, gratins, plats mijotés)
            - Légumes & Garnitures (purées, poêlées, gratins)
        - **Spécialités**
            - Œufs & Fromages (omelettes, quiches, gratins)
            - Pain & Pâtisserie salée (pizzas, fougasses, brioches salées)
            - Sauces & Condiments
    - **Pâtisseries et desserts**
        - Desserts classiques (gâteaux, crèmes, tartes)
        - Desserts glacés & fruités (sorbets, mousses, salades de fruits)
- **Dynamic Search**: Real-time search by recipe name or ingredient.

### [Frontend] Recipe Detail Page
#### [NEW] [recipes/[slug]/page.tsx](file:///c:/Foodypedia/frontend/src/app/recipes/[slug]/page.tsx)
- Create a premium detail page for recipes.
- **Dynamic Ingredient Links**: Clickable links to ingredient detail pages.
- Layout: Large visual, clear steps, and technical costs table.

### [Backend] Hierarchical Category Seeding
#### [NEW] [management/commands/seed_recipe_categories.py]
- Management command to seed the full 2-tier hierarchy.
- **Root Categories**: "Cuisine et gastronomie" and "Pâtisseries et desserts".
- Assign correct parent-child relationships and unique slugs.
- Add descriptive icons for each top-level category.

### [Frontend] AI Menu Generator ("Le Cerveau Culinaire")
#### [NEW] [ai-chef/page.tsx](file:///c:/Foodypedia/frontend/src/app/ai-chef/page.tsx)
- **Concept**: A "Chef's Brain" interface where users select ingredients to get recipe suggestions.
- **Route**: `/ai-chef`
- **Aesthetic**: Dark/Premium mode option or distinct "AI" styling (Purple/Olive/Gold gradients). Glassmorphism heavily used.
- **Components**:
    - **Hero**: "Intelligence Culinaire active."
    - **Ingredient Selector**: Real-time search connected to `api/ingredients/` with a visual "Pantry" (Panier).
    - **Action**: "Inventer une Recette" button triggering a mock AI response (initially).
    - **Output**: A card view for the generated recipe suggestion.
- **Technical**:
    - **Frontend**: API call to `api/ai-chef/generate/` with selected ingredients.
    - **Backend**: New Django View `GenerateRecipeView` that:
        1. Receives ingredient list.
        2. Formats payload.
        3. POSTs to n8n Webhook URL (from ENV).
        4. Returns n8n response to frontend.
    - **n8n**: Workflow to accept ingredients -> LLM Agent -> JSON Recipe format -> Respond.

## Phase 5: Deployment & Git
#### [MODIFY] Final steps to ensure the project is stable for production.

## Verification Plan

### Manual Verification
- Navigate to the Ingredients list and check the new card layout.
- Click on several ingredients (e.g., Artichaut, Ciboule) and verify the detail page renders all data correctly.
- Test responsive layout (Mobile vs Desktop).
