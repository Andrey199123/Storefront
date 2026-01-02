# SmartChoice Pantry System

A comprehensive food pantry management system built with Flask and SQLite, featuring client shopping portals, inventory management, and dietary filtering.

## Features

### Staff Dashboard
- **Product Management**: Add, edit, and delete products with categories, pricing, nutrition scores, dietary indicators, and allergen information
- **Location Management**: Manage storage locations (Pantry, Warehouse, Refrigerator, etc.)
- **Inventory Movements**: Track product movements between locations
- **Order Management**: View and update order statuses
- **Client Management**: Add and manage client profiles

### Reports
- **Product Balance Report**: View current inventory levels across all locations
- **Revenue Report**: Track sales and revenue with printable receipts

### Client Shopping Portal
- **Points-Based System**: Clients shop using allocated points per visit
- **MyPlate Categories**: Products organized by Fruits, Vegetables, Dairy, Proteins, Grains, and Other
- **Special Diet Filtering**: Filter products by dietary preferences:
  - 🌱 Vegan
  - 🥕 Vegetarian
  - 🌾 Gluten-Free
  - 🥛 Dairy-Free
  - 🧂 Low Sodium
  - 🍬 Sugar-Free
- **Multiple Fulfillment Options**: Pickup, Curbside, Delivery, Locker, Satellite locations
- **Nutrition Scoring**: Products display nutrition scores (0-100)

### Kiosk Mode
- Touch-friendly interface for in-person shopping
- Large buttons and simplified navigation
- Quick checkout process

## Tech Stack
- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap (MDB)
- **Authentication**: Werkzeug password hashing

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Andrey199123/Storefront.git
cd Storefront
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
# Generate one with: python3 -c "import secrets; print(secrets.token_hex(32))"
```

4. Initialize the database with sample data:
```bash
python3 setup_sample_data_sql.py
python3 add_inventory.py
python3 add_product_images_sql.py  # Optional: Add product images
```

5. Run the application:
```bash
python3 main.py
```

6. Access the application:
- Staff Login: http://127.0.0.1:5000/
- Client Shopping: http://127.0.0.1:5000/shop
- Kiosk Mode: http://127.0.0.1:5000/kiosk

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Test Clients**: `C00001` (John Smith), `C00002` (Maria Garcia)

## Project Structure
```
├── main.py                    # Main Flask application
├── database.py                # SQLAlchemy models
├── requirements.txt           # Python dependencies
├── setup_sample_data_sql.py   # Database initialization script
├── add_inventory.py           # Inventory setup script
├── add_product_images_sql.py  # Product images script
├── templates/                 # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── index.html
│   ├── products.html
│   ├── shop_items.html
│   ├── shop_categories.html
│   └── ...
├── static/
│   ├── css/
│   └── js/
└── instance/
    └── pantry.db             # SQLite database (created on first run)
```

## API Endpoints

### Authentication
- `GET/POST /` - Login/Register page
- `GET /shop` - Client login
- `GET /kiosk` - Kiosk mode login

### Staff Routes
- `GET /home` - Dashboard
- `GET/POST /products/` - Product management
- `GET/POST /locations/` - Location management
- `GET/POST /movements/` - Inventory movements
- `GET/POST /clients/` - Client management
- `GET /orders/` - Order management
- `GET /product-balance/` - Inventory report
- `GET /revenue-report/` - Revenue report

### Client Shopping
- `GET /shop/categories` - Category selection
- `GET /shop/category/<category>` - Browse products (supports `?diet=` filter)
- `POST /shop/add-to-cart` - Add item to cart
- `POST /shop/remove-from-cart` - Remove item from cart
- `GET/POST /shop/checkout` - Checkout process

## Database Schema

### Main Tables
- **users** - Staff accounts
- **products** - Product catalog with dietary info
- **clients** - Client profiles
- **locations** - Storage locations
- **movements** - Inventory movements
- **orders** - Client orders
- **counter** - ID generation

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
This project is open source and available for educational and non-commercial use.
