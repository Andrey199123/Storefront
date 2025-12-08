#!/usr/bin/env python3
"""
Setup script to create sample data for SmartChoice Pantry System (SQL Version)
Run this after first launch to populate with example products and a test client
"""

from flask import Flask
from werkzeug.security import generate_password_hash
from database import db, User, Product, Client, Location, Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def setup_sample_data():
    with app.app_context():
        print("Setting up sample data for SmartChoice Pantry...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Initialize counter
        counter = Counter(name='main', value=100)
        db.session.add(counter)
        
        # Create sample products
        products_data = [
            # Fruits
            ("Apples", "Fruits", "Fresh, 3 lb bag", 2, 6, 85, ["vegan", "gluten-free"], [], "1234567890"),
            ("Bananas", "Fruits", "Fresh, bunch of 5-6", 1, 5, 80, ["vegan", "gluten-free"], [], ""),
            ("Oranges", "Fruits", "Fresh, 4 lb bag", 2, 8, 90, ["vegan", "gluten-free"], [], ""),
            ("Strawberries", "Fruits", "Fresh, 1 lb container", 3, 4, 88, ["vegan", "gluten-free"], [], ""),
            
            # Vegetables
            ("Broccoli", "Vegetables", "Fresh, 2-3 stalks", 2, 4, 95, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Carrots", "Vegetables", "Fresh, 2 lb bag", 1, 8, 92, ["vegan", "gluten-free"], [], ""),
            ("Lettuce", "Vegetables", "Fresh, 1 head", 1, 4, 85, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Tomatoes", "Vegetables", "Fresh, 2 lb", 2, 6, 88, ["vegan", "gluten-free"], [], ""),
            ("Spinach", "Vegetables", "Fresh, 10 oz bag", 2, 3, 98, ["vegan", "gluten-free", "low-sodium"], [], ""),
            
            # Dairy
            ("Milk - 2%", "Dairy", "Half gallon", 3, 8, 70, [], ["milk"], ""),
            ("Almond Milk", "Dairy", "Half gallon", 3, 8, 72, ["vegan", "dairy-free", "gluten-free"], [], ""),
            ("Yogurt - Plain", "Dairy", "32 oz container", 3, 8, 75, [], ["milk"], ""),
            ("Cheese - Cheddar", "Dairy", "8 oz block", 3, 8, 60, [], ["milk"], ""),
            ("Eggs", "Dairy", "1 dozen", 3, 12, 85, [], ["eggs"], ""),
            ("Coconut Yogurt", "Dairy", "24 oz container", 3, 6, 70, ["vegan", "dairy-free", "gluten-free"], [], ""),
            
            # Proteins
            ("Chicken Breast", "Proteins", "Frozen, 2 lb", 5, 8, 80, ["gluten-free"], [], ""),
            ("Ground Beef", "Proteins", "Frozen, 1 lb", 5, 4, 65, ["gluten-free"], [], ""),
            ("Canned Tuna", "Proteins", "5 oz can", 2, 2, 75, ["gluten-free"], ["fish"], ""),
            ("Black Beans", "Proteins", "15 oz can", 1, 4, 90, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Peanut Butter", "Proteins", "16 oz jar", 3, 16, 70, ["vegan", "gluten-free"], ["peanuts"], ""),
            ("Tofu - Firm", "Proteins", "14 oz package", 3, 4, 85, ["vegan", "vegetarian", "gluten-free", "low-sodium"], [], ""),
            ("Lentils - Dry", "Proteins", "16 oz bag", 2, 12, 92, ["vegan", "gluten-free", "low-sodium"], [], ""),
            
            # Grains
            ("Whole Wheat Bread", "Grains", "20 oz loaf", 2, 20, 75, [], ["gluten"], ""),
            ("Gluten-Free Bread", "Grains", "18 oz loaf", 3, 18, 70, ["gluten-free"], [], ""),
            ("Brown Rice", "Grains", "2 lb bag", 2, 16, 85, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Pasta - Whole Wheat", "Grains", "16 oz box", 2, 8, 70, [], ["gluten"], ""),
            ("Pasta - Gluten Free", "Grains", "12 oz box", 3, 6, 68, ["vegan", "gluten-free"], [], ""),
            ("Oatmeal", "Grains", "18 oz container", 2, 12, 88, ["vegan", "gluten-free"], [], ""),
            ("Quinoa", "Grains", "16 oz bag", 3, 12, 90, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Cereal - Whole Grain", "Grains", "12 oz box", 2, 10, 65, [], [], ""),
            
            # Other
            ("Olive Oil", "Other", "16 oz bottle", 3, 32, 75, ["vegan", "gluten-free", "dairy-free"], [], ""),
            ("Canned Tomatoes", "Other", "28 oz can", 1, 6, 80, ["vegan", "gluten-free", "low-sodium"], [], ""),
            ("Soup - Vegetable", "Other", "15 oz can", 2, 2, 60, ["vegan", "vegetarian"], [], ""),
            ("Soup - Low Sodium", "Other", "15 oz can", 2, 2, 65, ["vegan", "vegetarian", "low-sodium"], [], ""),
            ("Honey", "Other", "12 oz bottle", 2, 24, 55, ["vegetarian", "gluten-free"], [], ""),
            ("Maple Syrup", "Other", "12 oz bottle", 3, 24, 50, ["vegan", "gluten-free", "sugar-free"], [], ""),
        ]
        
        for prod_data in products_data:
            product = Product(
                product_id=prod_data[0],
                category=prod_data[1],
                description=prod_data[2],
                points=prod_data[3],
                servings=prod_data[4],
                nutrition_score=prod_data[5],
                upc=prod_data[8]
            )
            product.set_dietary_indicators(prod_data[6])
            product.set_allergens(prod_data[7])
            db.session.add(product)
        
        print(f"✓ Created {len(products_data)} sample products")
        
        # Create sample clients
        clients_data = [
            ("C00001", "John Smith", "john.smith@example.com", "555-0123", 4, "English", 100),
            ("C00002", "Maria Garcia", "maria.garcia@example.com", "555-0124", 2, "Spanish", 75),
        ]
        
        for client_data in clients_data:
            client = Client(
                client_id=client_data[0],
                name=client_data[1],
                email=client_data[2],
                phone=client_data[3],
                household_size=client_data[4],
                language=client_data[5],
                points_per_visit=client_data[6]
            )
            db.session.add(client)
        
        print(f"✓ Created {len(clients_data)} sample clients")
        print("  - Client ID: C00001 (John Smith)")
        print("  - Client ID: C00002 (Maria Garcia)")
        
        # Create sample admin user
        admin_user = User(
            name='Admin User',
            username='admin',
            email='admin@pantry.org',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        print("✓ Created admin user")
        print("  - Username: admin")
        print("  - Password: admin123")
        
        # Create locations
        locations_data = ['Pantry', 'Warehouse', 'Refrigerator', 'Customer', 'Reserved']
        for loc_id in locations_data:
            location = Location(location_id=loc_id)
            db.session.add(location)
        
        print(f"✓ Created {len(locations_data)} locations")
        
        # Commit all changes
        db.session.commit()
        
        print("\n✅ Sample data setup complete!")
        print("\nNext steps:")
        print("1. Run: python3 add_inventory.py (to add stock)")
        print("2. Run: python3 main.py")
        print("3. Login at http://127.0.0.1:5000/ with admin/admin123")
        print("4. Test client shopping at http://127.0.0.1:5000/shop with Client ID: C00001")
        print("5. Test kiosk mode at http://127.0.0.1:5000/kiosk")

if __name__ == '__main__':
    setup_sample_data()
