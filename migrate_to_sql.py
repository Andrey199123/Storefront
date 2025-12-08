#!/usr/bin/env python3
"""
Migration script to convert PKL files to SQL database
"""
import pickle
import os
import json
import sys
from flask import Flask

# Import from backup file to get old class definitions
sys.path.insert(0, os.path.dirname(__file__))
import main_pkl_backup as old_main

from database import db, User, Product, Client, Location, Movement, Order, Appointment, Survey, Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def load_from_pkl(filename):
    """Load data from PKL file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                return pickle.load(file)
    except (EOFError, FileNotFoundError):
        pass
    return []

def read_counter(filename):
    """Read counter from text file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                content = file.read().strip()
                return int(content) if content else 100
    except (FileNotFoundError, ValueError):
        pass
    return 100

def migrate_data():
    """Migrate all data from PKL to SQL"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Migrate counter
        print("\nMigrating counter...")
        counter_value = read_counter('counter.txt')
        counter = Counter.query.filter_by(name='main').first()
        if not counter:
            counter = Counter(name='main', value=counter_value)
            db.session.add(counter)
        else:
            counter.value = counter_value
        db.session.commit()
        print(f"  ✓ Counter set to {counter_value}")
        
        # Migrate users
        print("\nMigrating users...")
        users_data = load_from_pkl('users.pkl')
        for user_dict in users_data:
            existing = User.query.filter_by(username=user_dict['username']).first()
            if not existing:
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
        
        # Migrate locations
        print("\nMigrating locations...")
        locations_data = load_from_pkl('location.pkl')
        for loc_obj in locations_data:
            existing = Location.query.filter_by(location_id=loc_obj.location_id).first()
            if not existing:
                location = Location(
                    location_id=loc_obj.location_id,
                    date_created=loc_obj.date_created
                )
                db.session.add(location)
        db.session.commit()
        print(f"  ✓ Migrated {len(locations_data)} locations")
        
        # Migrate products
        print("\nMigrating products...")
        products_data = load_from_pkl('product.pkl')
        for prod_obj in products_data:
            existing = Product.query.filter_by(product_id=prod_obj.product_id).first()
            if not existing:
                product = Product(
                    product_id=prod_obj.product_id,
                    price=float(prod_obj.price) if prod_obj.price else 0,
                    purchase_price=float(prod_obj.purchase_price) if prod_obj.purchase_price else 0,
                    category=prod_obj.category,
                    description=prod_obj.description,
                    upc=prod_obj.upc,
                    servings=prod_obj.servings,
                    points=prod_obj.points,
                    nutrition_score=prod_obj.nutrition_score,
                    image_url=getattr(prod_obj, 'image_url', ''),
                    date_created=prod_obj.date_created
                )
                product.set_dietary_indicators(prod_obj.dietary_indicators)
                product.set_allergens(prod_obj.allergens)
                db.session.add(product)
        db.session.commit()
        print(f"  ✓ Migrated {len(products_data)} products")
        
        # Migrate clients
        print("\nMigrating clients...")
        clients_data = load_from_pkl('clients.pkl')
        for client_obj in clients_data:
            existing = Client.query.filter_by(client_id=client_obj.client_id).first()
            if not existing:
                client = Client(
                    client_id=client_obj.client_id,
                    name=client_obj.name,
                    email=client_obj.email,
                    phone=client_obj.phone,
                    address=client_obj.address,
                    household_size=client_obj.household_size,
                    language=client_obj.language,
                    points_per_visit=client_obj.points_per_visit,
                    visits_per_period=client_obj.visits_per_period,
                    date_created=client_obj.date_created,
                    last_visit=client_obj.last_visit
                )
                client.set_eligibility_groups(client_obj.eligibility_groups)
                client.set_allergens(client_obj.allergens)
                client.set_dietary_prefs(client_obj.dietary_prefs)
                db.session.add(client)
        db.session.commit()
        print(f"  ✓ Migrated {len(clients_data)} clients")
        
        # Migrate movements
        print("\nMigrating movements...")
        movements_data = load_from_pkl('movement.pkl')
        for mov_obj in movements_data:
            existing = Movement.query.filter_by(movement_id=mov_obj.movement_id).first()
            if not existing:
                movement = Movement(
                    movement_id=mov_obj.movement_id,
                    product_id=mov_obj.product_id,
                    qty=int(mov_obj.qty),
                    price=float(mov_obj.price) if mov_obj.price else 0,
                    from_location=mov_obj.from_location if mov_obj.from_location else None,
                    to_location=mov_obj.to_location if mov_obj.to_location else None,
                    movement_time=mov_obj.movement_time
                )
                db.session.add(movement)
        db.session.commit()
        print(f"  ✓ Migrated {len(movements_data)} movements")
        
        # Migrate orders
        print("\nMigrating orders...")
        orders_data = load_from_pkl('orders.pkl')
        for order_obj in orders_data:
            existing = Order.query.filter_by(order_id=order_obj.order_id).first()
            if not existing:
                order = Order(
                    order_id=order_obj.order_id,
                    client_id=order_obj.client_id,
                    total_points=order_obj.total_points,
                    fulfillment_method=order_obj.fulfillment_method,
                    status=order_obj.status,
                    pickup_time=order_obj.pickup_time,
                    created_at=order_obj.created_at,
                    completed_at=order_obj.completed_at
                )
                order.set_items(order_obj.items)
                db.session.add(order)
        db.session.commit()
        print(f"  ✓ Migrated {len(orders_data)} orders")
        
        # Migrate appointments
        print("\nMigrating appointments...")
        appointments_data = load_from_pkl('appointments.pkl')
        for appt_obj in appointments_data:
            existing = Appointment.query.filter_by(appointment_id=appt_obj.appointment_id).first()
            if not existing:
                appointment = Appointment(
                    appointment_id=appt_obj.appointment_id,
                    client_id=appt_obj.client_id,
                    appointment_time=appt_obj.appointment_time,
                    appointment_type=appt_obj.appointment_type,
                    status=appt_obj.status,
                    created_at=appt_obj.created_at
                )
                db.session.add(appointment)
        db.session.commit()
        print(f"  ✓ Migrated {len(appointments_data)} appointments")
        
        print("\n✅ Migration complete!")
        print(f"\nDatabase created: pantry.db")
        print(f"Total records migrated:")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Products: {Product.query.count()}")
        print(f"  - Clients: {Client.query.count()}")
        print(f"  - Locations: {Location.query.count()}")
        print(f"  - Movements: {Movement.query.count()}")
        print(f"  - Orders: {Order.query.count()}")
        print(f"  - Appointments: {Appointment.query.count()}")

if __name__ == '__main__':
    migrate_data()
