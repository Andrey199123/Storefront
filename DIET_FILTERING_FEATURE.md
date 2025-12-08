# Special Diet Filtering Feature

## Overview
The SmartChoice Pantry System now includes special diet filtering options that allow clients to filter food items based on their dietary preferences and restrictions when ordering through the cart system.

## Features

### Dietary Filter Options
Clients can filter products by the following dietary preferences:
- 🌱 **Vegan** - No animal products
- 🥕 **Vegetarian** - No meat products
- 🌾 **Gluten-Free** - No gluten-containing ingredients
- 🥛 **Dairy-Free** - No dairy products
- 🧂 **Low Sodium** - Reduced sodium content
- 🍬 **Sugar-Free** - No added sugars

### How It Works

#### For Clients (Shopping Interface)
1. Navigate to any food category (Fruits, Vegetables, Dairy, Proteins, Grains, Other)
2. Use the filter buttons at the top of the items page
3. Click one or more dietary filter buttons to activate them
4. Products are filtered in real-time using client-side JavaScript
5. Only products matching ALL selected filters are displayed (AND logic)
6. Click "Clear All" to remove all filters and see all products

#### For Staff (Product Management)
When adding or editing products, staff can mark dietary indicators:
- Vegan
- Vegetarian
- Gluten-Free
- Low Sodium
- Sugar-Free
- Dairy-Free

These indicators are stored in the product database and used for filtering.

## Database Changes

### Product Class
The `Product` class already includes:
- `dietary_indicators` - List of dietary tags (e.g., ["vegan", "gluten-free"])
- `allergens` - List of allergens (e.g., ["milk", "eggs"])

### Client Class
The `Client` class includes:
- `dietary_prefs` - List of client's dietary preferences
- `allergens` - List of client's allergen restrictions

## Implementation Details

### Frontend (shop_items.html)
- Filter buttons with visual active state
- JavaScript functions for real-time filtering
- Products tagged with `data-dietary` attribute containing comma-separated dietary indicators
- Filters use AND logic (product must have ALL selected filters)

### Backend (main.py)
- Updated `shop_category_items()` route to accept dietary filter query parameters
- Server-side filtering support (currently using client-side for better UX)
- Products maintain dietary_indicators list

### Sample Data (setup_sample_data.py)
- Enhanced with diverse products having various dietary indicators
- Examples include:
  - Vegan options: Tofu, Lentils, Black Beans, Almond Milk
  - Gluten-free options: Rice, Quinoa, Gluten-Free Bread
  - Low-sodium options: Fresh vegetables, specific canned goods
  - Dairy-free options: Almond Milk, Coconut Yogurt

## Testing

### Test the Feature
1. Run `python setup_sample_data.py` to create sample products with dietary indicators
2. Run `python add_inventory.py` to add inventory to all products
3. Start the application: `python main.py`
4. Visit http://127.0.0.1:5000/shop
5. Login with Client ID: C00001
6. Navigate to any category
7. Try different filter combinations

### Example Test Cases
- Filter by "Vegan" in Proteins → Should show Tofu, Lentils, Black Beans, Peanut Butter
- Filter by "Gluten-Free" in Grains → Should show Brown Rice, Quinoa, Gluten-Free Bread, Oatmeal
- Filter by "Vegan" + "Gluten-Free" → Should show only products with BOTH tags
- Filter by "Dairy-Free" in Dairy → Should show Almond Milk, Coconut Yogurt

## Future Enhancements
- Save client dietary preferences and auto-apply filters
- Highlight allergen warnings based on client profile
- Add more dietary categories (Kosher, Halal, Organic, etc.)
- Server-side filtering with URL parameters for bookmarking
- Filter by nutrition score ranges
- Exclude allergens automatically based on client profile
