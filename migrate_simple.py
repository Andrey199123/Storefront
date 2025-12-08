#!/usr/bin/env python3
"""
Simple migration script - manually unpickle and migrate data
"""
import pickle
import os
import json
from flask import Flask
from database import db, User, Product, Client, Location, Movement, Order, Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def read_counter():
    try:
        with open('counter.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 100

def migrate():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Migrate counter
        print("\nMigrating counter...")
        counter_value = read_counter()
        counter = Counter.query.filter_by(name='main').first()
        if not counter:
            counter = Counter(name='main', value=counter_value)
            db.session.add(counter)
        else:
            counter.value = counter_value
        db.session.commit()
        print(f"  ✓ Counter set to {counter_value}")
        
        # Migrate users - they're stored as dicts
        print("\nMigrating users...")
        try:
            with open('users.pkl', 'rb') as f:
                users_data = pickle.load(f)
                for user_dict in users_data:
                    if not User.query.filter_by(username=user_dict['username']).first():
                        user = User(
                            name=user_dict.get('name', ''),
                            username=user_dict['username'],
                            email=user_dict['email'],
                            password=user_dict['password'],
                            role=user_dict.get('role', 'staff')
                        )
                        db.session.add(user)
                db.session.commit()
                print(f"  ✓ Migrated {len(users_data)} users")
        except Exception as e:
            print(f"  ⚠ Users migration: {e}")
        
        # For other data, we'll use __dict__ to extract attributes
        print("\nMigrating locations...")
        try:
            with open('location.pkl', 'rb') as f:
                # Temporarily define Location class for unpickling
                import sys
                import types
                
                # Create a dummy module
                dummy_main = types.ModuleType('main')
                
                # Define minimal classes for unpickling
                class OldLocation:
                    pass
                
                dummy_main.Location = OldLocation
                sys.modules['main'] = dummy_main
                
                locations_data = pickle.load(f)
                for loc_obj in locations_data:
                    loc_id = loc_obj.__dict__.get('location_id')
                    if loc_id and not Location.query.filter_by(location_id=loc_id).first():
                        location = Location(
                            location_id=loc_id,
                            date_created=loc_obj.__dict__.get('date_created', '')
                        )
                        db.session.add(location)
                db.session.commit()
                print(f"  ✓ Migrated {len(locations_data)} locations")
        except Exception as e:
            print(f"  ⚠ Locations migration: {e}")
            # Create default locations
            for loc_id in ['Customer', 'Reserved', 'Pantry', 'Warehouse', 'Refrigerator']:
                if not Location.query.filter_by(location_id=loc_id).first():
                    db.session.add(Location(location_id=loc_id))
            db.session.commit()
            print("  ✓ Created default locations")
        
        # Similar approach for products
        print("\nMigrating products...")
        try:
            with open('product.pkl', 'rb') as f:
                import sys
                import types
                dummy_main = types.ModuleType('main')
                class OldProduct:
                    pass
                dummy_main.Product = OldProduct
                sys.modules['main'] = dummy_main
                
                products_data = pickle.load(f)
                for prod_obj in products_data:
                    prod_dict = prod_obj.__dict__
                    if not Product.query.filter_by(product_id=prod_dict.get('product_id')).first():
                        product = Product(
                            product_id=prod_dict.get('product_id'),
                            price=float(prod_dict.get('price', 0)),
                            purchase_price=float(prod_dict.get('purchase_price', 0)),
                            category=prod_dict.get('category', 'Other'),
                            description=prod_dict.get('description', ''),
                            upc=prod_dict.get('upc', ''),
                            servings=prod_dict.get('servings', 1),
                            points=prod_dict.get('points', 1),
                            nutrition_score=prod_dict.get('nutrition_score', 50),
                            image_url=prod_dict.get('image_url', ''),
                            date_created=prod_dict.get('date_created', '')
                        )
                        product.set_dietary_indicators(prod_dict.get('dietary_indicators', []))
                        product.set_allergens(prod_dict.get('allergens', []))
                        db.session.add(product)
                db.session.commit()
                print(f"  ✓ Migrated {len(products_data)} products")
        except Exception as e:
            print(f"  ⚠ Products migration: {e}")
        
        # Clients
        print("\nMigrating clients...")
        try:
            with open('clients.pkl', 'rb') as f:
                import sys
                import types
                dummy_main = types.ModuleType('main')
                class OldClient:
                    pass
                dummy_main.Client = OldClient
                sys.modules['main'] = dummy_main
                
                clients_data = pickle.load(f)
                for client_obj in clients_data:
                    client_dict = client_obj.__dict__
                    if not Client.query.filter_by(client_id=client_dict.get('client_id')).first():
                        client = Client(
                            client_id=client_dict.get('client_id'),
                            name=client_dict.get('name'),
                            email=client_dict.get('email', ''),
                            phone=client_dict.get('phone', ''),
                            address=client_dict.get('address', ''),
                            household_size=client_dict.get('household_size', 1),
                            language=client_dict.get('language', 'English'),
                            points_per_visit=client_dict.get('points_per_visit', 100),
                            visits_per_period=client_dict.get('visits_per_period', 1),
                            date_created=client_dict.get('date_created', ''),
                            last_visit=client_dict.get('last_visit')
                        )
                        client.set_eligibility_groups(client_dict.get('eligibility_groups', []))
                        client.set_allergens(client_dict.get('allergens', []))
                        client.set_dietary_prefs(client_dict.get('dietary_prefs', []))
                        db.session.add(client)
                db.session.commit()
                print(f"  ✓ Migrated {len(clients_data)} clients")
        except Exception as e:
            print(f"  ⚠ Clients migration: {e}")
        
        # Movements
        print("\nMigrating movements...")
        try:
            with open('movement.pkl', 'rb') as f:
                import sys
                import types
                dummy_main = types.ModuleType('main')
                class OldMovement:
                    pass
                dummy_main.Movement = OldMovement
                sys.modules['main'] = dummy_main
                
                movements_data = pickle.load(f)
                for mov_obj in movements_data:
                    mov_dict = mov_obj.__dict__
                    if not Movement.query.filter_by(movement_id=mov_dict.get('movement_id')).first():
                        movement = Movement(
                            movement_id=mov_dict.get('movement_id'),
                            product_id=mov_dict.get('product_id'),
                            qty=int(mov_dict.get('qty', 0)),
                            price=float(mov_dict.get('price', 0)),
                            from_location=mov_dict.get('from_location') or None,
                            to_location=mov_dict.get('to_location') or None,
                            movement_time=mov_dict.get('movement_time', '')
                        )
                        db.session.add(movement)
                db.session.commit()
                print(f"  ✓ Migrated {len(movements_data)} movements")
        except Exception as e:
            print(f"  ⚠ Movements migration: {e}")
        
        # Orders
        print("\nMigrating orders...")
        try:
            with open('orders.pkl', 'rb') as f:
                import sys
                import types
                dummy_main = types.ModuleType('main')
                class OldOrder:
                    pass
                dummy_main.Order = OldOrder
                sys.modules['main'] = dummy_main
                
                orders_data = pickle.load(f)
                for order_obj in orders_data:
                    order_dict = order_obj.__dict__
                    if not Order.query.filter_by(order_id=order_dict.get('order_id')).first():
                        order = Order(
                            order_id=order_dict.get('order_id'),
                            client_id=order_dict.get('client_id'),
                            total_points=order_dict.get('total_points', 0),
                            fulfillment_method=order_dict.get('fulfillment_method', 'Pickup'),
                            status=order_dict.get('status', 'Pending'),
                            pickup_time=order_dict.get('pickup_time'),
                            created_at=order_dict.get('created_at'),
                            completed_at=order_dict.get('completed_at')
                        )
                        order.set_items(order_dict.get('items', []))
                        db.session.add(order)
                db.session.commit()
                print(f"  ✓ Migrated {len(orders_data)} orders")
        except Exception as e:
            print(f"  ⚠ Orders migration: {e}")
        
        print("\n✅ Migration complete!")
        print(f"\nDatabase created: pantry.db")
        print(f"Total records:")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Products: {Product.query.count()}")
        print(f"  - Clients: {Client.query.count()}")
        print(f"  - Locations: {Location.query.count()}")
        print(f"  - Movements: {Movement.query.count()}")
        print(f"  - Orders: {Order.query.count()}")

if __name__ == '__main__':
    migrate()
