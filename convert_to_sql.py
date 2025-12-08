#!/usr/bin/env python3
"""
Automated conversion script to replace PKL operations with SQL in main.py
"""
import re

def convert_main_py():
    """Convert main.py from PKL to SQL database"""
    
    with open('main_pkl_backup.py', 'r') as f:
        content = f.read()
    
    # Replace imports
    content = re.sub(
        r'import pickle\n',
        '',
        content
    )
    
    content = re.sub(
        r'from flask import Flask.*\n',
        'from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for\n',
        content
    )
    
    # Add database imports after Flask import
    content = content.replace(
        'from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for\n',
        '''from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
from database import db, User, Product as DBProduct, Client as DBClient, Location as DBLocation
from database import Movement as DBMovement, Order as DBOrder, Appointment as DBAppointment, Counter
'''
    )
    
    # Remove PKL file definitions and initialization
    content = re.sub(
        r"# Data files.*?open\(counter_file, 'w'\)\.close\(\)",
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add database configuration
    content = content.replace(
        "app = Flask(__name__)\napp.secret_key = 'gJwlRqBv959595'  #IMPORTANT",
        """app = Flask(__name__)
app.secret_key = 'gJwlRqBv959595'  # IMPORTANT
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    # Ensure default locations exist
    if not DBLocation.query.filter_by(location_id='Customer').first():
        customer_loc = DBLocation(location_id='Customer')
        db.session.add(customer_loc)
    if not DBLocation.query.filter_by(location_id='Reserved').first():
        reserved_loc = DBLocation(location_id='Reserved')
        db.session.add(reserved_loc)
    if not DBLocation.query.filter_by(location_id='Pantry').first():
        pantry_loc = DBLocation(location_id='Pantry')
        db.session.add(pantry_loc)
    db.session.commit()"""
    )
    
    # Remove old class definitions
    content = re.sub(
        r'class Product:.*?return f\'<Product \{self\.product_id\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'class Client:.*?return f\'<Client \{self\.name\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'class Order:.*?return f\'<Order \{self\.order_id\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'class Appointment:.*?return f\'<Appointment \{self\.appointment_id\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'class Location:.*?return f\'<Location \{self\.location_id\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'class Movement:.*?return f\'<Movement \{self\.movement_id\}>\'',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove PKL helper functions
    content = re.sub(
        r'def save_to_pkl\(data, filename\):.*?pickle\.dump\(data, file\)',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'def load_from_pkl\(filename\):.*?return \[\]',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'def read_counter\(filename\):.*?return counter',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'def write_counter\(filename, counter\):.*?file\.write\(str\(counter\)\)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Clean up multiple blank lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    with open('main_converted.py', 'w') as f:
        f.write(content)
    
    print("✓ Created main_converted.py with initial conversions")
    print("  Manual route updates still needed")

if __name__ == '__main__':
    convert_main_py()
