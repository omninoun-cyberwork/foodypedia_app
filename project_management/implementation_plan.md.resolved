# Refresh Ingredients Table from JSON

Clear the existing `ingredients` table and repopulate it using over 20 JSON files from `C:\Foodypedia\JSON des ingredients`. Each file represents a category. Images will be linked from `C:\Foodypedia\static\ingredients_pics`.

## Proposed Changes

### [Backend] Ingredients App

#### [NEW] [refresh_ingredients.py](file:///C:/Foodypedia/apps/ingredients/management/commands/refresh_ingredients.py)
Create a new management command to:
1.  **Empty Tables**: Delete all records from `Ingredient`, `IngredientImage`, `IngredientCategory`, and `FunctionalCategory`.
2.  **Iterate JSON Files**: Scan `C:\Foodypedia\JSON des ingredients`. Use filename (without extension) as `IngredientCategory` name.
3.  **Parse Ingredients**:
    - Create `Ingredient` entries.
    - Set `image_filename` and search for it in `C:\Foodypedia\static\ingredients_pics`.
    - Create `IngredientImage` for `variant_images`.
    - Map all fields: `scientific_name`, `description`, `category` (parent category), `seasonality`, `buying_guide`, `storage_guide`, `prep_guide`, `nutrition_info`, `texture`, `specific_data`, `tags`.
4.  **Auto-assign Category Image**: Pick the image of the first ingredient in the category as the category image if not otherwise specified.

### [Frontend] UI/UX Optimization

#### [MODIFY] [Ingredients Page](file:///C:/Foodypedia/frontend/src/app/ingredients/page.tsx)
1.  **Dynamic Categories**: Use categories fetched from the API (database) instead of the hardcoded `LANDING_CATEGORIES`.
2.  **Reduce Card Size**: Change card height from `h-80` to `h-64` or `h-56`.
3.  **Optimize Grid**: Increase column count on large screens (e.g., `2xl:grid-cols-6` or `7`) to accommodate more categories efficiently.
4.  **Maintain Aesthetics**: Keep the "Title at Top" and "Image Bottom" design but make it more compact.

## Verification Plan

### Automated Verification
- Run the command: `python manage.py refresh_ingredients`
- Verify the counts of ingredients in the database against the JSON files.
- Check for any integrity errors or missing mandatory fields.

### Manual Verification
- Log into the Django Admin and inspect a few ingredients from different categories to ensure all fields (including JSON fields and images) are correctly populated.
- Verify that images are displayed correctly in the frontend (if accessible).
