#!/usr/bin/env python3
"""
Setup script to create sample data for SmartChoice Pantry System
Run this after first launch to populate with example products and a test client
"""

import pickle
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash

# Import classes from main.py
import sys
sys.path.append('.')
from main import Product, Client, Location, save_to_pkl, load_from_pkl

def setup_sample_data():
    print("Setting up sample data for SmartChoice Pantry...")
    
    # Create sample products
    products = [
        # Fruits
        Product("Apples", category="Fruits", description="Fresh, 3 lb bag", points=2, servings=6, nutrition_score=85, dietary_indicators=["vegan", "gluten-free"], upc="1234567890"),
        Product("Bananas", category="Fruits", description="Fresh, bunch of 5-6", points=1, servings=5, nutrition_score=80, dietary_indicators=["vegan", "gluten-free"]),
        Product("Oranges", category="Fruits", description="Fresh, 4 lb bag", points=2, servings=8, nutrition_score=90, dietary_indicators=["vegan", "gluten-free"]),
        Product("Strawberries", category="Fruits", description="Fresh, 1 lb container", points=3, servings=4, nutrition_score=88, dietary_indicators=["vegan", "gluten-free"]),
        
        # Vegetables
        Product("Broccoli", category="Vegetables", description="Fresh, 2-3 stalks", points=2, servings=4, nutrition_score=95, dietary_indicators=["vegan", "gluten-free", "low-sodium"]),
        Product("Carrots", category="Vegetables", description="Fresh, 2 lb bag", points=1, servings=8, nutrition_score=92, dietary_indicators=["vegan", "gluten-free"]),
        Product("Lettuce", category="Vegetables", description="Fresh, 1 head", points=1, servings=4, nutrition_score=85, dietary_indicators=["vegan", "gluten-free", "low-sodium"]),
        Product("Tomatoes", category="Vegetables", description="Fresh, 2 lb", points=2, servings=6, nutrition_score=88, dietary_indicators=["vegan", "gluten-free"]),
        Product("Spinach", category="Vegetables", description="Fresh, 10 oz bag", points=2, servings=3, nutrition_score=98, dietary_indicators=["vegan", "gluten-free", "low-sodium"]),
        
        # Dairy
        Product("Milk - 2%", category="Dairy", description="Half gallon", points=3, servings=8, nutrition_score=70, allergens=["milk"]),
        Product("Yogurt - Plain", category="Dairy", description="32 oz container", points=3, servings=8, nutrition_score=75, allergens=["milk"]),
        Product("Cheese - Cheddar", category="Dairy", description="8 oz block", points=3, servings=8, nutrition_score=60, allergens=["milk"]),
        Product("Eggs", category="Dairy", description="1 dozen", points=3, servings=12, nutrition_score=85, allergens=["eggs"]),
        
        # Proteins
        Product("Chicken Breast", category="Proteins", description="Frozen, 2 lb", points=5, servings=8, nutrition_score=80),
        Product("Ground Beef", category="Proteins", description="Frozen, 1 lb", points=5, servings=4, nutrition_score=65),
        Product("Canned Tuna", category="Proteins", description="5 oz can", points=2, servings=2, nutrition_score=75, allergens=["fish"]),
        Product("Black Beans", category="Proteins", description="15 oz can", points=1, servings=4, nutrition_score=90, dietary_indicators=["vegan", "gluten-free"]),
        Product("Peanut Butter", category="Proteins", description="16 oz jar", points=3, servings=16, nutrition_score=70, allergens=["peanuts"]),
        
        # Grains
        Product("Whole Wheat Bread", category="Grains", description="20 oz loaf", points=2, servings=20, nutrition_score=75, allergens=["gluten"]),
        Product("Brown Rice", category="Grains", description="2 lb bag", points=2, servings=16, nutrition_score=85, dietary_indicators=["vegan", "gluten-free"]),
        Product("Pasta - Whole Wheat", category="Grains", description="16 oz box", points=2, servings=8, nutrition_score=70, allergens=["gluten"]),
        Product("Oatmeal", category="Grains", description="18 oz container", points=2, servings=12, nutrition_score=88, dietary_indicators=["vegan"]),
        Product("Cereal - Whole Grain", category="Grains", description="12 oz box", points=2, servings=10, nutrition_score=65),
        
        # Other
        Product("Olive Oil", category="Other", description="16 oz bottle", points=3, servings=32, nutrition_score=75, dietary_indicators=["vegan", "gluten-free"]),
        Product("Canned Tomatoes", category="Other", description="28 oz can", points=1, servings=6, nutrition_score=80, dietary_indicators=["vegan", "gluten-free"]),
        Product("Soup - Vegetable", category="Other", description="15 oz can", points=2, servings=2, nutrition_score=60),
    ]
    
    save_to_pkl(products, 'product.pkl')
    print(f"✓ Created {len(products)} sample products")
    
    # Create sample client
    clients = [
        Client(
            client_id="C00001",
            name="John Smith",
            email="john.smith@example.com",
            phone="555-0123",
            household_size=4,
            language="English",
            points_per_visit=100
        ),
        Client(
            client_id="C00002",
            name="Maria Garcia",
            email="maria.garcia@example.com",
            phone="555-0124",
            household_size=2,
            language="Spanish",
            points_per_visit=75
        ),
    ]
    
    save_to_pkl(clients, 'clients.pkl')
    print(f"✓ Created {len(clients)} sample clients")
    print("  - Client ID: C00001 (John Smith)")
    print("  - Client ID: C00002 (Maria Garcia)")
    
    # Create sample admin user
    users = [
        {
            'name': 'Admin User',
            'username': 'admin',
            'email': 'admin@pantry.org',
            'password': generate_password_hash('admin123'),
            'role': 'admin'
        }
    ]
    
    save_to_pkl(users, 'users.pkl')
    print("✓ Created admin user")
    print("  - Username: admin")
    print("  - Password: admin123")
    
    # Create locations
    locations = [
        Location(location_id='Pantry'),
        Location(location_id='Warehouse'),
        Location(location_id='Refrigerator'),
        Location(location_id='Customer'),
        Location(location_id='Reserved'),
    ]
    
    save_to_pkl(locations, 'location.pkl')
    print(f"✓ Created {len(locations)} locations")
    
    # Initialize empty orders and movements
    save_to_pkl([], 'orders.pkl')
    save_to_pkl([], 'movement.pkl')
    save_to_pkl([], 'appointments.pkl')
    save_to_pkl([], 'surveys.pkl')
    
    # Set counter
    with open('counter.txt', 'w') as f:
        f.write('100')
    
    print("\n✅ Sample data setup complete!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Login at http://127.0.0.1:5000/ with admin/admin123")
    print("3. Go to Inventory Movements to add stock to products")
    print("4. Test client shopping at http://127.0.0.1:5000/shop with Client ID: C00001")
    print("5. Test kiosk mode at http://127.0.0.1:5000/kiosk")

if __name__ == '__main__':
    setup_sample_data()
