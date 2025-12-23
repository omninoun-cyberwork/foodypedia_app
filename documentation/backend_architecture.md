# Backend Architecture Documentation - Recipes Application

## 1. Data Models (`apps/recipes/models.py`)

The recipe system is built around a flexible, hierarchical structure.

### `RecipeCategory`
- **Purpose**: Classifies recipes into top-level sections (Cuisine, Pâtisserie) and sub-rubriques (Viande, Poisson).
- **Hierarchy**: Uses a self-referencing `parent` field to support infinite nesting.
- **Slug**: Unique identifier for URL-based filtering (e.g., `?root=cuisine`).

### `Recette` (Recipe)
- **Central Model**: Stores main metadata (title, description, times).
- **Authors**: Many-to-Many relationship with the User model.
- **Techniques**: Linked to the `Technique` model.
- **Ingredients**: Linked via a pivot model `QuantiteIngredient` to support both raw ingredients and sub-recipes.

### `QuantiteIngredient` (Recipe Line)
- **Recursive Logic**: Each line in a recipe can be either:
  1. A raw `Ingredient` (from the Ingredients app).
  2. A `sub_recipe` (another `Recette` instance).
- **Validation**: Enforces that one (and only one) of these options is selected.

---

## 2. API ViewSets (`apps/recipes/views.py`)

### `RecetteViewSet`
- **Recursive Filtering**: Implements custom `get_queryset` logic. When filtering by a category slug (e.g., `cuisine`), it automatically collects all children IDs to include all descendant recipes in the results.
- **Optimization**: Uses `prefetch_related` on `lignes_ingredients__ingredient`, `auteurs`, and `techniques_cles` to prevent N+1 query issues.
- **Statistiques**: Custom action to provide high-level metrics (total count, top authors).

### `RecipeCategoryViewSet`
- **Static Access**: Provides the list of all categories.
- **Pagination**: Disabled (`pagination_class = None`) to allow the frontend to easily map and filter categories for dropdowns.

---

## 3. Filtering & Search Logic

- **Category Filtering**: Supported via `category__slug` (exact match) or `category__root_slug` (recursive match).
- **Search**: Multi-field search enabled on `titre` and `description`.
- **Ordering**: Alphabetical by default for better encyclopedic navigation.

---

## 4. Ingredients Application (`apps/ingredients/models.py`)

The Ingredients app provides the master data for the wiki.

### `Ingredient`
- **Rich Data**: Includes scientific name, seasonality, and detailed guides (buying, storage, preparation).
- **Taxonomy**: Connects to `IngredientCategory` for broad classification.
- **Cross-App Link**: Recettes link to this model via `QuantiteIngredient`.
