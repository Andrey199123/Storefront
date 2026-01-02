"""
Database module for SmartChoice Pantry System
Migrated from PKL files to SQLite with SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import json

db = SQLAlchemy()

def get_eastern_time():
    """Get current time in Eastern timezone"""
    return datetime.now(pytz.timezone('America/New_York'))

def get_eastern_time_str():
    """Get current time as formatted string in Eastern timezone"""
    return get_eastern_time().strftime("%A, %B %d, %Y %I:%M %p")


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='staff')
    date_created = db.Column(db.DateTime, default=get_eastern_time)
    
    def to_dict(self):
        return {
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(200), unique=True, nullable=False)
    price = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    category = db.Column(db.String(100), default='Other')
    description = db.Column(db.Text, default='')
    upc = db.Column(db.String(100), default='')
    servings = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=1)
    nutrition_score = db.Column(db.Integer, default=50)
    dietary_indicators = db.Column(db.Text, default='[]')  # JSON array
    allergens = db.Column(db.Text, default='[]')  # JSON array
    image_url = db.Column(db.String(500), default='')
    date_created = db.Column(db.String(200), default=get_eastern_time_str)
    
    # Relationships
    movements = db.relationship('Movement', backref='product', lazy=True, foreign_keys='Movement.product_id')
    
    def get_dietary_indicators(self):
        """Get dietary indicators as list"""
        try:
            return json.loads(self.dietary_indicators) if self.dietary_indicators else []
        except:
            return []
    
    def set_dietary_indicators(self, indicators):
        """Set dietary indicators from list"""
        self.dietary_indicators = json.dumps(indicators if indicators else [])
    
    def get_allergens(self):
        """Get allergens as list"""
        try:
            return json.loads(self.allergens) if self.allergens else []
        except:
            return []
    
    def set_allergens(self, allergen_list):
        """Set allergens from list"""
        self.allergens = json.dumps(allergen_list if allergen_list else [])
    
    def __repr__(self):
        return f'<Product {self.product_id}>'


class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), default='')
    phone = db.Column(db.String(50), default='')
    address = db.Column(db.Text, default='')
    household_size = db.Column(db.Integer, default=1)
    language = db.Column(db.String(50), default='English')
    eligibility_groups = db.Column(db.Text, default='[]')  # JSON array
    points_per_visit = db.Column(db.Integer, default=100)
    visits_per_period = db.Column(db.Integer, default=1)
    allergens = db.Column(db.Text, default='[]')  # JSON array
    dietary_prefs = db.Column(db.Text, default='[]')  # JSON array
    date_created = db.Column(db.String(200), default=get_eastern_time_str)
    last_visit = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    orders = db.relationship('Order', backref='client', lazy=True)
    appointments = db.relationship('Appointment', backref='client', lazy=True)
    
    def get_eligibility_groups(self):
        try:
            return json.loads(self.eligibility_groups) if self.eligibility_groups else []
        except:
            return []
    
    def set_eligibility_groups(self, groups):
        self.eligibility_groups = json.dumps(groups if groups else [])
    
    def get_allergens(self):
        try:
            return json.loads(self.allergens) if self.allergens else []
        except:
            return []
    
    def set_allergens(self, allergen_list):
        self.allergens = json.dumps(allergen_list if allergen_list else [])
    
    def get_dietary_prefs(self):
        try:
            return json.loads(self.dietary_prefs) if self.dietary_prefs else []
        except:
            return []
    
    def set_dietary_prefs(self, prefs):
        self.dietary_prefs = json.dumps(prefs if prefs else [])
    
    def __repr__(self):
        return f'<Client {self.name}>'


class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.String(200), unique=True, nullable=False)
    date_created = db.Column(db.String(200), default=get_eastern_time_str)
    
    # Relationships
    movements_from = db.relationship('Movement', backref='from_loc', lazy=True, foreign_keys='Movement.from_location')
    movements_to = db.relationship('Movement', backref='to_loc', lazy=True, foreign_keys='Movement.to_location')
    
    def __repr__(self):
        return f'<Location {self.location_id}>'


class Movement(db.Model):
    __tablename__ = 'movements'
    
    id = db.Column(db.Integer, primary_key=True)
    movement_id = db.Column(db.Integer, unique=True, nullable=False)
    product_id = db.Column(db.String(200), db.ForeignKey('products.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, default=0)
    from_location = db.Column(db.String(200), db.ForeignKey('locations.location_id'), nullable=True)
    to_location = db.Column(db.String(200), db.ForeignKey('locations.location_id'), nullable=True)
    movement_time = db.Column(db.String(200), default=get_eastern_time_str)
    
    def __repr__(self):
        return f'<Movement {self.movement_id}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    client_id = db.Column(db.String(100), db.ForeignKey('clients.client_id'), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON array of items
    total_points = db.Column(db.Integer, nullable=False)
    fulfillment_method = db.Column(db.String(100), default='Pickup')
    satellite_location = db.Column(db.String(200), nullable=True)  # For satellite pickup
    note_to_staff = db.Column(db.Text, nullable=True)  # Client notes for staff
    status = db.Column(db.String(50), default='Pending')
    pickup_time = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=get_eastern_time)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def get_items(self):
        """Get items as list"""
        try:
            return json.loads(self.items) if self.items else []
        except:
            return []
    
    def set_items(self, items_list):
        """Set items from list"""
        self.items = json.dumps(items_list if items_list else [])
    
    def __repr__(self):
        return f'<Order {self.order_id}>'


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, unique=True, nullable=False)
    client_id = db.Column(db.String(100), db.ForeignKey('clients.client_id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(100), default='Shopping')
    status = db.Column(db.String(50), default='Scheduled')
    created_at = db.Column(db.DateTime, default=get_eastern_time)
    
    def __repr__(self):
        return f'<Appointment {self.appointment_id}>'


class StaffMessage(db.Model):
    __tablename__ = 'staff_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, unique=True, nullable=False)
    client_id = db.Column(db.String(100), db.ForeignKey('clients.client_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_eastern_time)
    
    def __repr__(self):
        return f'<StaffMessage {self.message_id}>'


class Survey(db.Model):
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, unique=True, nullable=False)
    client_id = db.Column(db.String(100), nullable=True)
    survey_data = db.Column(db.Text, nullable=False)  # JSON data
    created_at = db.Column(db.DateTime, default=get_eastern_time)
    
    def get_survey_data(self):
        try:
            return json.loads(self.survey_data) if self.survey_data else {}
        except:
            return {}
    
    def set_survey_data(self, data):
        self.survey_data = json.dumps(data if data else {})
    
    def __repr__(self):
        return f'<Survey {self.survey_id}>'


class Counter(db.Model):
    __tablename__ = 'counter'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, default='main')
    value = db.Column(db.Integer, default=0)
    
    @staticmethod
    def get_next_id():
        """Get next ID and increment counter"""
        counter = Counter.query.filter_by(name='main').first()
        if not counter:
            counter = Counter(name='main', value=100)
            db.session.add(counter)
            db.session.commit()
        
        counter.value += 1
        db.session.commit()
        return counter.value
    
    @staticmethod
    def get_current_id():
        """Get current counter value without incrementing"""
        counter = Counter.query.filter_by(name='main').first()
        if not counter:
            counter = Counter(name='main', value=100)
            db.session.add(counter)
            db.session.commit()
        return counter.value
