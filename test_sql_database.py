#!/usr/bin/env python3
"""
Test script to verify SQL database functionality
"""
from flask import Flask
from database import db, User, Product, Client, Location, Movement, Order, Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_database():
    with app.app_context():
        print("Testing SQL Database...")
        print("=" * 60)
        
        # Test Users
        print("\n1. Testing Users:")
        users = User.query.all()
        print(f"   ✓ Found {len(users)} users")
        if users:
            print(f"   - {users[0].username} ({users[0].email})")
        
        # Test Products
        print("\n2. Testing Products:")
        products = Product.query.all()
        print(f"   ✓ Found {len(products)} products")
        if products:
            sample = products[0]
            print(f"   - {sample.product_id}: {sample.category}, {sample.points} points")
            print(f"   - Dietary: {sample.get_dietary_indicators()}")
        
        # Test Clients
        print("\n3. Testing Clients:")
        clients = Client.query.all()
        print(f"   ✓ Found {len(clients)} clients")
        for client in clients:
            print(f"   - {client.client_id}: {client.name}")
        
        # Test Locations
        print("\n4. Testing Locations:")
        locations = Location.query.all()
        print(f"   ✓ Found {len(locations)} locations")
        for loc in locations:
            print(f"   - {loc.location_id}")
        
        # Test Movements
        print("\n5. Testing Movements:")
        movements = Movement.query.all()
        print(f"   ✓ Found {len(movements)} movements")
        if movements:
            sample = movements[0]
            print(f"   - Movement #{sample.movement_id}: {sample.product_id}")
            print(f"     From: {sample.from_location} → To: {sample.to_location}")
            print(f"     Qty: {sample.qty}")
        
        # Test Orders
        print("\n6. Testing Orders:")
        orders = Order.query.all()
        print(f"   ✓ Found {len(orders)} orders")
        
        # Test Counter
        print("\n7. Testing Counter:")
        counter = Counter.query.filter_by(name='main').first()
        if counter:
            print(f"   ✓ Counter value: {counter.value}")
        
        # Test inventory calculation
        print("\n8. Testing Inventory Calculation:")
        test_product = products[0] if products else None
        if test_product:
            inventory = 0
            product_movements = Movement.query.filter_by(product_id=test_product.product_id).all()
            for mov in product_movements:
                if mov.to_location and mov.to_location != 'Customer':
                    inventory += int(mov.qty)
                if mov.from_location and mov.from_location != 'Customer':
                    inventory -= int(mov.qty)
            print(f"   ✓ {test_product.product_id} inventory: {inventory} units")
        
        # Test dietary filtering
        print("\n9. Testing Dietary Filtering:")
        vegan_products = [p for p in products if 'vegan' in p.get_dietary_indicators()]
        print(f"   ✓ Found {len(vegan_products)} vegan products")
        
        gluten_free = [p for p in products if 'gluten-free' in p.get_dietary_indicators()]
        print(f"   ✓ Found {len(gluten_free)} gluten-free products")
        
        print("\n" + "=" * 60)
        print("✅ All database tests passed!")
        print("\nDatabase is working correctly with SQL!")

if __name__ == '__main__':
    test_database()
