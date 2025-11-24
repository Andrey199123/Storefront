#!/usr/bin/env python3
"""
Quick script to add inventory to all products
This makes them available for client shopping
"""

import pickle
from datetime import datetime
import pytz

# Import classes from main.py
import sys
sys.path.append('.')
from main import Movement, load_from_pkl, save_to_pkl, read_counter, write_counter

def add_inventory_to_all_products():
    print("Adding inventory to all products...")
    
    # Load products
    products = load_from_pkl('product.pkl')
    movements = load_from_pkl('movement.pkl')
    counter = read_counter('counter.txt')
    
    # Add 50 units of each product to Pantry location
    for product in products:
        counter += 1
        new_movement = Movement(
            price=0,
            movement_id=counter,
            product_id=product.product_id,
            qty=50,
            from_location='',  # Receiving new stock
            to_location='Pantry'
        )
        movements.append(new_movement)
        print(f"  ✓ Added 50 units of {product.product_id} to Pantry")
    
    # Save everything
    save_to_pkl(movements, 'movement.pkl')
    write_counter('counter.txt', counter)
    
    print(f"\n✅ Successfully added inventory for {len(products)} products!")
    print("\nNow clients can shop:")
    print("- Online: http://127.0.0.1:5000/shop (Client ID: C00001)")
    print("- Kiosk: http://127.0.0.1:5000/kiosk (Client ID: C00002)")

if __name__ == '__main__':
    add_inventory_to_all_products()
