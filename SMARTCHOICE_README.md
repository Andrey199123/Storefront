# SmartChoice™ Pantry Management System

A complete food pantry management software solution based on SmartChoice Pantry, featuring client choice ordering, real-time inventory management, and multiple fulfillment options.

## Features

### Client-Facing Features
- **Online Shopping Portal** - Clients can shop from home using any device
- **Touchscreen Kiosk Mode** - On-site self-service shopping
- **MyPlate Categories** - Organized by USDA MyPlate food groups (Fruits, Vegetables, Dairy, Proteins, Grains)
- **Points System** - Configurable points per visit and per category
- **Nutrition Scoring** - Products rated 0-100 for nutritional value
- **Dietary Indicators** - Vegan, vegetarian, gluten-free, low-sodium, etc.
- **Allergen Management** - Track and filter by allergens
- **Multiple Fulfillment Options**:
  - Pantry Pickup (inside)
  - Curbside Pickup
  - 24/7 Refrigerated Lockers
  - Home Delivery
  - Satellite Pickup Locations
- **Multi-Language Support** - English, Spanish, French, Chinese, Arabic, Russian

### Staff/Admin Features
- **Client Management** - Register and manage client profiles
- **Order Management** - Track and fulfill orders with status updates
- **Product Management** - Add products with full nutritional data
- **Inventory Management** - Real-time stock tracking with movements
- **Location Management** - Multiple storage locations
- **Reporting** - Inventory reports and order history

## Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Access the application:
- Staff Portal: http://127.0.0.1:5000/
- Client Shopping: http://127.0.0.1:5000/shop
- Kiosk Mode: http://127.0.0.1:5000/kiosk

### Initial Setup

1. **Register Staff Account**
   - Go to http://127.0.0.1:5000/
   - Click "Register" and create your admin account

2. **Add Locations**
   - Go to Locations menu
   - Add storage locations (e.g., "Pantry", "Warehouse", "Refrigerator")
   - System automatically creates "Customer" and "Reserved" locations

3. **Add Products**
   - Go to Products menu
   - Add products with:
     - Name and description
     - MyPlate category
     - Points value
     - Nutrition score (0-100)
     - Dietary indicators
     - Allergens
     - UPC/barcode (optional)

4. **Add Inventory**
   - Go to Inventory Movements
   - Record incoming inventory (from blank location to storage location)

5. **Register Clients**
   - Go to Clients menu
   - Add client information:
     - Name, email, phone
     - Household size
     - Language preference
     - Points per visit (default: 100)
   - Client receives a unique Client ID (e.g., C00001)

## Usage

### Client Shopping (Online)

1. Client goes to http://127.0.0.1:5000/shop
2. Enters their Client ID
3. Browses MyPlate categories
4. Adds items to cart (within points limit)
5. Proceeds to checkout
6. Selects fulfillment method
7. Receives order confirmation

### Kiosk Shopping (On-Site)

1. Client approaches kiosk at http://127.0.0.1:5000/kiosk
2. Enters Client ID on touchscreen
3. Selects categories and adds items
4. Reviews MyPlate points summary
5. Completes order
6. Receives order number for pickup

### Staff Order Fulfillment

1. Go to Orders menu
2. View pending orders
3. Prepare items for pickup/delivery
4. Update order status:
   - Pending → Ready → Completed
5. When marked "Completed", inventory automatically moves from Reserved to Customer

## Data Structure

### Products
- Name, category, description
- Points, servings, nutrition score
- Dietary indicators and allergens
- UPC/barcode

### Clients
- Client ID, name, contact info
- Household size, language
- Points per visit, visit frequency
- Allergen/dietary preferences

### Orders
- Order ID, client, items
- Total points, fulfillment method
- Status, timestamps

### Inventory Movements
- Product, quantity
- From location → To location
- Timestamp

## Key Differences from Original SmartChoice

This is a simplified implementation focusing on core functionality:

**Included:**
- Client choice shopping (online & kiosk)
- MyPlate categories
- Points system
- Nutrition scoring
- Dietary indicators & allergens
- Multiple fulfillment options
- Real-time inventory
- Order management

**Not Included (can be added later):**
- Stripe payment integration
- DoorDash delivery API
- Salesforce integration
- TEFAP/SNAP reporting
- Food is Medicine prescriptions
- Appointment scheduling
- Survey functionality
- Test cells for research
- Quick Trip baskets
- Healthy swap suggestions

## File Structure

```
├── main.py                          # Main Flask application
├── requirements.txt                 # Python dependencies
├── templates/
│   ├── base.html                   # Staff portal base template
│   ├── index.html                  # Staff dashboard
│   ├── login.html                  # Staff login
│   ├── clients.html                # Client management
│   ├── client_detail.html          # Client profile
│   ├── orders.html                 # Order management
│   ├── products.html               # Product management
│   ├── update-product.html         # Edit product
│   ├── locations.html              # Location management
│   ├── movements.html              # Inventory movements
│   ├── product-balance.html        # Inventory report
│   ├── client_login.html           # Client shopping login
│   ├── shop_categories.html        # MyPlate category selection
│   ├── shop_items.html             # Product browsing
│   ├── shop_checkout.html          # Checkout & fulfillment
│   ├── order_confirmation.html     # Order confirmation
│   ├── kiosk_login.html            # Kiosk start screen
│   ├── kiosk_categories.html       # Kiosk shopping
│   └── kiosk_complete.html         # Kiosk completion
├── static/                          # CSS, JS, images
└── *.pkl                           # Data files (pickle format)
```

## Data Files

The system uses pickle files for data storage:
- `users.pkl` - Staff accounts
- `clients.pkl` - Client profiles
- `product.pkl` - Product catalog
- `location.pkl` - Storage locations
- `movement.pkl` - Inventory movements
- `orders.pkl` - Client orders
- `counter.txt` - ID counter

**Note:** For production use, migrate to a proper database (PostgreSQL, MySQL, etc.)

## Customization

### Adjust Points Per Visit
Edit client profile to change points allocation

### Add More Categories
Modify category lists in templates and main.py

### Change Nutrition Scoring
Update product nutrition_score field (0-100 scale)

### Add Languages
Add language options in client forms and implement translations

## Support

This system is designed for food pantries to provide dignified, client-choice food access. For questions or issues, contact your development team.

## License

This is a custom implementation for Poverello partnership. All rights reserved.
