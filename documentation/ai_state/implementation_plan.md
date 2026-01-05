# Redesign Ingredient Category Cards

The goal is to update the ingredient landing page with a set of specific categories, using the provided images and a premium, modern design.

## User Review Required

> [!NOTE]
> I am hardcoding the category metadata (names, image paths, and short descriptions) in the frontend to ensure the "wow" effect and specific layout requested. These will still link to the backend for ingredient filtering.

## Proposed Changes

### Frontend Assets
Images have been moved to [frontend/public/images/categories/](file:///C:/Foodypedia/frontend/public/images/categories/).

### Ingredients Page
#### [MODIFY] [page.tsx](file:///C:/Foodypedia/frontend/src/app/ingredients/page.tsx)
- Define a `LANDING_CATEGORIES` constant with the following details for each category:
    - Name
    - Image path
    - Slug (mapping to backend categories)
    - Short description
    - Example sub-categories/ingredients
- Update the `IngredientsContent` component to use these categories when on the landing view.
- Redesign the category card:
    - Reduce card size.
    - Implement a "premium" look (glassmorphism, soft gradients, smooth hover effects).
    - Display the small description and sub-items as requested.
    - Use Next.js `Image` component with optimization.

### Design Details
- **Glassmorphism**: Use semi-transparent backgrounds with `backdrop-blur`.
- **Micro-interactions**: Subtle scale and shadow transitions on hover.
- **Typography**: Refined font sizes and weights and line-clamp for descriptions.

## Verification Plan

### Manual Verification
- Navigate to `/ingredients`.
- Verify that the 10 new category cards are displayed correctly.
- Check that the images load properly.
- Verify that clicking a card filters the ingredients by that category (or equivalent).
- Test on different screen sizes (responsive design).
