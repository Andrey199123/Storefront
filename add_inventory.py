#!/usr/bin/env python3
"""
Quick script to add inventory to all products
This makes them available for client shopping
"""

from flask import Flask
from database import db, Product, Movement, Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def add_inventory_to_all_products():
    with app.app_context():
        print("Adding inventory to all products...")
        
        # Load products
        products = Product.query.all()
        
        # Add 50 units of each product to Pantry location
        for product in products:
            movement_id = Counter.get_next_id()
            new_movement = Movement(
                movement_id=movement_id,
                product_id=product.product_id,
                qty=50,
                price=0,
                from_location=None,  # Receiving new stock
                to_location='Pantry'
            )
            db.session.add(new_movement)
            print(f"  ✓ Added 50 units of {product.product_id} to Pantry")
        
        # Save everything
        db.session.commit()
        
        print(f"\n✅ Successfully added inventory for {len(products)} products!")
        print("\nNow clients can shop:")
        print("- Online: http://127.0.0.1:5000/shop (Client ID: C00001)")
        print("- Kiosk: http://127.0.0.1:5000/kiosk (Client ID: C00002)")

if __name__ == '__main__':
    add_inventory_to_all_products()
