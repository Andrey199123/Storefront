# SmartChoice Pantry - Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Sample Data
```bash
python3 setup_sample_data.py
```

This creates:
- 26 sample products across all MyPlate categories
- 2 test clients (C00001 and C00002)
- Admin user (username: `admin`, password: `admin123`)
- 5 locations (Pantry, Warehouse, Refrigerator, Customer, Reserved)

### 3. Start the Application
```bash
python3 main.py
```

The server will start at http://127.0.0.1:5000/

## Testing the System

### Test 1: Staff Portal

1. Go to http://127.0.0.1:5000/
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. You'll see the dashboard with stats
4. Explore the menu:
   - **Clients** - View registered clients
   - **Orders** - See all orders (empty initially)
   - **Products** - View the 26 sample products
   - **Locations** - See storage locations
   - **Inventory Movements** - Add stock to products

### Test 2: Add Inventory

Before clients can shop, you need to add inventory:

1. Go to **Inventory Movements**
2. Click "Add Movement"
3. Select a product (e.g., "Apples")
4. Enter quantity (e.g., 50)
5. From Location: leave blank (receiving new stock)
6. To Location: select "Pantry"
7. Click "Add Movement"
8. Repeat for several products so clients have items to choose from

### Test 3: Client Online Shopping

1. Open a new browser tab/window
2. Go to http://127.0.0.1:5000/shop
3. Enter Client ID: `C00001`
4. Click "Start Shopping"
5. You'll see the MyPlate category screen with:
   - Fruits, Vegetables, Dairy, Proteins, Grains, Other
   - Your cart on the right
   - Points remaining (100 points)
   - MyPlate points breakdown
6. Click on a category (e.g., "Fruits")
7. Browse products with nutrition scores
8. Click "Add to Cart" on items
9. Return to categories and add more items
10. When ready, click "Checkout"
11. Select a fulfillment method:
    - Pantry Pickup
    - Curbside Pickup
    - 24/7 Refrigerated Locker
    - Home Delivery
    - Satellite Pickup Location
12. Click "Place Order"
13. You'll see order confirmation with order number

### Test 4: Staff Order Fulfillment

1. Go back to staff portal
2. Click **Orders** in the menu
3. You'll see the order you just placed
4. Click the status dropdown and change from "Pending" to "Ready"
5. When client picks up, change to "Completed"
6. When marked "Completed", inventory automatically moves from Reserved to Customer

### Test 5: Kiosk Mode

1. Go to http://127.0.0.1:5000/kiosk
2. Enter Client ID: `C00002`
3. Click "Start Shopping"
4. You'll see a full-screen touchscreen interface
5. Select categories and add items
6. Watch the MyPlate points update in real-time
7. Click "Complete Order"
8. Order is immediately fulfilled (no checkout step)
9. Screen shows confirmation and auto-returns to start

## Key Features to Explore

### Product Management
- Add products with MyPlate categories
- Set nutrition scores (0-100)
- Mark dietary indicators (vegan, gluten-free, etc.)
- Flag allergens (milk, eggs, nuts, etc.)
- Assign points values

### Client Management
- Register new clients
- Set household size
- Choose language preference
- Configure points per visit
- View order history

### Inventory System
- Track stock across multiple locations
- Move items between locations
- Reserve items when ordered online
- Complete orders to move to Customer
- View current inventory report

### MyPlate Points System
- Each product has a category (Fruits, Vegetables, etc.)
- Each product costs points
- Clients have a points budget per visit
- Cart shows breakdown by MyPlate category
- Encourages balanced nutrition

### Nutrition Features
- Products scored 0-100
- Green/yellow/red indicators (70+, 40-69, <40)
- Items sorted by nutrition score
- Dietary filters (vegan, vegetarian, etc.)
- Allergen warnings

## Common Tasks

### Add a New Client
1. Go to **Clients**
2. Fill in the form:
   - Name (required)
   - Email, phone (optional)
   - Household size
   - Language
3. Click "Add Client"
4. Client receives a unique ID (e.g., C00003)
5. Give this ID to the client for shopping

### Add a New Product
1. Go to **Products**
2. Fill in the form:
   - Product name (required)
   - MyPlate category (required)
   - Description
   - Points (required)
   - Nutrition score (0-100)
   - Servings
   - Check dietary indicators
   - Check allergens
3. Click "Add Product"

### Receive Inventory
1. Go to **Inventory Movements**
2. Select product
3. Enter quantity
4. From Location: leave blank
5. To Location: select storage location
6. Click "Add Movement"

### Transfer Between Locations
1. Go to **Inventory Movements**
2. Select product
3. Enter quantity
4. From Location: select source
5. To Location: select destination
6. Click "Add Movement"

## Tips

- **Points Budget**: Adjust per client based on household size
- **Nutrition Scores**: Higher scores appear first in shopping
- **Inventory**: Keep "Pantry" stocked for online/kiosk orders
- **Orders**: Check Orders menu regularly for pending pickups
- **Client IDs**: Print ID cards for clients to use at kiosk

## Troubleshooting

**Problem**: Client can't see products when shopping
- **Solution**: Add inventory to products via Inventory Movements

**Problem**: Client exceeds points limit
- **Solution**: Adjust points_per_visit in client profile

**Problem**: Order not showing in Orders menu
- **Solution**: Refresh the page, check that order was completed

**Problem**: Kiosk screen too small
- **Solution**: Press F11 for fullscreen mode

## Next Steps

1. Add more products from your actual inventory
2. Register your real clients
3. Customize points values based on your pantry's needs
4. Set up multiple storage locations
5. Train staff on order fulfillment process
6. Set up kiosk tablet/touchscreen for on-site use

## Support

For questions or issues, refer to SMARTCHOICE_README.md for detailed documentation.

---

**Ready to go!** Your SmartChoice Pantry system is now fully operational. Start by adding inventory, then invite clients to shop online or at your kiosk.
