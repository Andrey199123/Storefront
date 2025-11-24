# SmartChoice Pantry System - Food Pantry Management Software
from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
from collections import defaultdict
import pickle
from datetime import datetime, timedelta
import os
import re
import pytz
from werkzeug.security import check_password_hash, generate_password_hash
import subprocess

# Data files
users_file = 'users.pkl'
clients_file = 'clients.pkl'
product_file = 'product.pkl'
location_file = 'location.pkl'
movement_file = 'movement.pkl'
orders_file = 'orders.pkl'
appointments_file = 'appointments.pkl'
surveys_file = 'surveys.pkl'
counter_file = 'counter.txt'  # File for creating IDs

# Initialize data files
for file in [users_file, clients_file, product_file, location_file, movement_file, orders_file, appointments_file, surveys_file]:
    if not os.path.exists(file):
        open(file, 'wb').close()

if not os.path.exists(counter_file):
    open(counter_file, 'w').close()

app = Flask(__name__)
app.secret_key = 'gJwlRqBv959595'  #IMPORTANT


# Remove customer and remove location when display options to add a new movement
def remove_specific_locations(locations, names_to_remove):
    return [location for location in locations if location.location_id not in names_to_remove]


# Read ID counter
def read_counter(filename):
    try:
        with open(filename, 'r') as file:
            counter = int(file.read())
    except FileNotFoundError:
        # If the file doesn't exist, start with counter value 0
        counter = 0
    return counter


# Save ID counter
def write_counter(filename, counter):
    with open(filename, 'w') as file:
        file.write(str(counter))


def save_to_pkl(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_from_pkl(filename):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except EOFError:
        return []


class Product:
    def __init__(self, product_id, price=0, purchase_price=0, category='Other', description='', 
                 upc='', servings=1, points=1, nutrition_score=50, dietary_indicators=None, 
                 allergens=None, image_url=''):
        self.product_id = product_id
        self.date_created = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y %I:%M %p")
        self.price = price
        self.purchase_price = purchase_price
        self.category = category  # Fruits, Vegetables, Dairy, Proteins, Grains, Other
        self.description = description
        self.upc = upc
        self.servings = servings
        self.points = points
        self.nutrition_score = nutrition_score  # 0-100
        self.dietary_indicators = dietary_indicators or []  # vegan, vegetarian, gluten-free, etc.
        self.allergens = allergens or []  # milk, eggs, fish, etc.
        self.image_url = image_url

    def __repr__(self):
        return f'<Product {self.product_id}>'


class Client:
    def __init__(self, client_id, name, email='', phone='', address='', household_size=1, 
                 language='English', eligibility_groups=None, points_per_visit=100, 
                 visits_per_period=1, allergens=None, dietary_prefs=None):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.household_size = household_size
        self.language = language
        self.eligibility_groups = eligibility_groups or []
        self.points_per_visit = points_per_visit
        self.visits_per_period = visits_per_period
        self.allergens = allergens or []
        self.dietary_prefs = dietary_prefs or []
        self.date_created = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y %I:%M %p")
        self.last_visit = None

    def __repr__(self):
        return f'<Client {self.name}>'


class Order:
    def __init__(self, order_id, client_id, items, total_points, fulfillment_method='Pickup', 
                 status='Pending', pickup_time=None):
        self.order_id = order_id
        self.client_id = client_id
        self.items = items  # List of {product_id, quantity, points}
        self.total_points = total_points
        self.fulfillment_method = fulfillment_method  # Pickup, Curbside, Delivery, Locker, Satellite
        self.status = status  # Pending, Ready, Completed, Cancelled
        self.pickup_time = pickup_time
        self.created_at = datetime.now().astimezone(pytz.timezone('America/New_York'))
        self.completed_at = None

    def __repr__(self):
        return f'<Order {self.order_id}>'


class Appointment:
    def __init__(self, appointment_id, client_id, appointment_time, appointment_type='Shopping', status='Scheduled'):
        self.appointment_id = appointment_id
        self.client_id = client_id
        self.appointment_time = appointment_time
        self.appointment_type = appointment_type  # Shopping, Pickup
        self.status = status  # Scheduled, Checked-In, Completed, Cancelled
        self.created_at = datetime.now().astimezone(pytz.timezone('America/New_York'))

    def __repr__(self):
        return f'<Appointment {self.appointment_id}>'


class Location:
    def __init__(self, location_id):
        self.location_id = location_id
        self.date_created = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y "
                                                                                                  "%I:%M %p")

    def __repr__(self):
        return f'<Location {self.location_id}>'


class Movement:
    def __init__(self, price, movement_id, product_id, qty, from_location, to_location):
        self.price = price
        self.movement_id = movement_id
        self.product_id = product_id
        self.qty = qty
        self.from_location = from_location
        self.to_location = to_location
        self.movement_time = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y "
                                                                                                   "%I:%M %p")

    def __repr__(self):
        return f'<Movement {self.movement_id}>'


@app.route('/', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        form_type = request.form['form_type']
        if form_type == 'login':
            username_or_email = request.form['username_or_email']
            password = request.form['password']
            users = load_from_pkl(users_file)
            user = next((u for u in users if u['username'] == username_or_email or u['email'] == username_or_email), None)

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['username']
                session['user_role'] = user.get('role', 'staff')
                flash('Login successful')
                return redirect('/home')
            else:
                flash('Invalid username/email or password')
        elif form_type == 'register':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            users = load_from_pkl(users_file)

            if any(u['username'] == username for u in users):
                flash('Username already exists')
            elif any(u['email'] == email for u in users):
                flash('Email already exists')
            else:
                hashed_password = generate_password_hash(password)
                users.append({'name': name, 'username': username, 'email': email, 'password': hashed_password, 'role': 'staff'})
                save_to_pkl(users, users_file)
                flash('Registration successful. Please login.')
                return redirect('/')

    return render_template('login.html')


# Client Shopping Portal
@app.route('/shop', methods=['GET'])
def client_shop_login():
    """Client login page for shopping"""
    return render_template('client_login.html')


@app.route('/shop/login', methods=['POST'])
def client_login():
    """Handle client login"""
    client_id = request.form.get('client_id')
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    if client:
        session['client_id'] = client.client_id
        session['client_name'] = client.name
        session['client_language'] = client.language
        return redirect('/shop/categories')
    else:
        flash('Client ID not found')
        return redirect('/shop')


@app.route('/shop/categories', methods=['GET'])
def shop_categories():
    """Display MyPlate categories for shopping"""
    if 'client_id' not in session:
        return redirect('/shop')
    
    client_id = session['client_id']
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    # Get cart from session
    cart = session.get('cart', [])
    
    # Calculate points used
    points_used = sum(item['points'] * item['quantity'] for item in cart)
    points_remaining = client.points_per_visit - points_used
    
    # Calculate MyPlate points breakdown
    myplate_points = {
        'Fruits': 0,
        'Vegetables': 0,
        'Dairy': 0,
        'Proteins': 0,
        'Grains': 0,
        'Other': 0
    }
    
    products = load_from_pkl(product_file)
    for item in cart:
        product = next((p for p in products if p.product_id == item['product_id']), None)
        if product:
            myplate_points[product.category] += item['points'] * item['quantity']
    
    return render_template('shop_categories.html', client=client, cart=cart, 
                         points_used=points_used, points_remaining=points_remaining,
                         myplate_points=myplate_points)


@app.route('/shop/category/<category>', methods=['GET'])
def shop_category_items(category):
    """Display items in a specific category"""
    if 'client_id' not in session:
        return redirect('/shop')
    
    client_id = session['client_id']
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    products = load_from_pkl(product_file)
    movements = load_from_pkl(movement_file)
    
    # Filter products by category and check inventory
    category_products = []
    for product in products:
        if product.category == category:
            # Calculate available inventory
            inventory = 0
            for mov in movements:
                if mov.product_id == product.product_id:
                    if mov.to_location and mov.to_location != 'Customer':
                        inventory += int(mov.qty)
                    if mov.from_location and mov.from_location != 'Customer':
                        inventory -= int(mov.qty)
            
            if inventory > 0:
                product.available_qty = inventory
                category_products.append(product)
    
    # Sort by nutrition score (highest first)
    category_products.sort(key=lambda x: x.nutrition_score, reverse=True)
    
    cart = session.get('cart', [])
    points_used = sum(item['points'] * item['quantity'] for item in cart)
    points_remaining = client.points_per_visit - points_used
    
    return render_template('shop_items.html', category=category, products=category_products,
                         client=client, cart=cart, points_remaining=points_remaining)


@app.route('/shop/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add item to shopping cart"""
    if 'client_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))
    
    products = load_from_pkl(product_file)
    product = next((p for p in products if p.product_id == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'})
    
    cart = session.get('cart', [])
    
    # Check if item already in cart
    existing_item = next((item for item in cart if item['product_id'] == product_id), None)
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        cart.append({
            'product_id': product_id,
            'name': product.product_id,
            'quantity': quantity,
            'points': product.points,
            'category': product.category
        })
    
    session['cart'] = cart
    return jsonify({'success': True})


@app.route('/shop/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    if 'client_id' not in session:
        return jsonify({'success': False})
    
    product_id = request.json.get('product_id')
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    
    return jsonify({'success': True})


@app.route('/shop/checkout', methods=['GET', 'POST'])
def shop_checkout():
    """Checkout and select fulfillment method"""
    if 'client_id' not in session:
        return redirect('/shop')
    
    client_id = session['client_id']
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty')
        return redirect('/shop/categories')
    
    if request.method == 'POST':
        fulfillment_method = request.form.get('fulfillment_method')
        pickup_time = request.form.get('pickup_time')
        
        # Create order
        counter = read_counter(counter_file)
        counter += 1
        write_counter(counter_file, counter)
        
        total_points = sum(item['points'] * item['quantity'] for item in cart)
        
        order = Order(
            order_id=counter,
            client_id=client_id,
            items=cart,
            total_points=total_points,
            fulfillment_method=fulfillment_method,
            pickup_time=pickup_time
        )
        
        orders = load_from_pkl(orders_file)
        orders.append(order)
        save_to_pkl(orders, orders_file)
        
        # Update inventory - reserve items
        movements = load_from_pkl(movement_file)
        for item in cart:
            counter += 1
            new_movement = Movement(
                price=0,
                movement_id=counter,
                product_id=item['product_id'],
                qty=item['quantity'],
                from_location='Pantry',
                to_location='Reserved'
            )
            movements.append(new_movement)
        write_counter(counter_file, counter)
        save_to_pkl(movements, movement_file)
        
        # Clear cart
        session['cart'] = []
        
        flash(f'Order #{order.order_id} placed successfully!')
        return redirect('/shop/order-confirmation/' + str(order.order_id))
    
    return render_template('shop_checkout.html', client=client, cart=cart)


@app.route('/shop/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    if 'client_id' not in session:
        return redirect('/shop')
    
    orders = load_from_pkl(orders_file)
    order = next((o for o in orders if o.order_id == order_id), None)
    
    if not order:
        flash('Order not found')
        return redirect('/shop/categories')
    
    return render_template('order_confirmation.html', order=order)


@app.route('/shop/logout')
def client_logout():
    """Logout client"""
    session.pop('client_id', None)
    session.pop('client_name', None)
    session.pop('client_language', None)
    session.pop('cart', None)
    return redirect('/shop')


@app.route('/home', methods=["POST", "GET"])
def index():
    """Staff dashboard"""
    if 'user_id' not in session:
        return redirect('/')
    
    products = load_from_pkl(product_file)
    locations = load_from_pkl(location_file)
    clients = load_from_pkl(clients_file)
    orders = load_from_pkl(orders_file)
    
    # Get recent orders
    recent_orders = sorted(orders, key=lambda x: x.created_at, reverse=True)[:10]
    
    # Get pending orders count
    pending_orders = len([o for o in orders if o.status == 'Pending'])
    
    return render_template("index.html", products=products, locations=locations,
                         clients=clients, recent_orders=recent_orders, 
                         pending_orders=pending_orders)


@app.route('/clients/', methods=["POST", "GET"])
def view_clients():
    """View and manage clients"""
    if 'user_id' not in session:
        return redirect('/')
    
    if request.method == "POST":
        name = request.form["client_name"]
        email = request.form.get("client_email", "")
        phone = request.form.get("client_phone", "")
        household_size = int(request.form.get("household_size", 1))
        language = request.form.get("language", "English")
        
        # Generate client ID
        counter = read_counter(counter_file)
        counter += 1
        client_id = f"C{counter:05d}"
        write_counter(counter_file, counter)
        
        new_client = Client(
            client_id=client_id,
            name=name,
            email=email,
            phone=phone,
            household_size=household_size,
            language=language
        )
        
        try:
            clients = load_from_pkl(clients_file)
            clients.append(new_client)
            save_to_pkl(clients, clients_file)
            flash(f'Client {name} added successfully! Client ID: {client_id}')
            return redirect("/clients/")
        except Exception as e:
            flash(f"Error adding client: {e}")
    
    clients = load_from_pkl(clients_file)
    return render_template("clients.html", clients=clients)


@app.route('/clients/<client_id>', methods=["GET", "POST"])
def view_client_detail(client_id):
    """View and edit client details"""
    if 'user_id' not in session:
        return redirect('/')
    
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    if not client:
        flash('Client not found')
        return redirect('/clients/')
    
    if request.method == "POST":
        client.name = request.form["client_name"]
        client.email = request.form.get("client_email", "")
        client.phone = request.form.get("client_phone", "")
        client.household_size = int(request.form.get("household_size", 1))
        client.language = request.form.get("language", "English")
        client.points_per_visit = int(request.form.get("points_per_visit", 100))
        
        save_to_pkl(clients, clients_file)
        flash('Client updated successfully')
        return redirect('/clients/')
    
    # Get client's order history
    orders = load_from_pkl(orders_file)
    client_orders = [o for o in orders if o.client_id == client_id]
    client_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template("client_detail.html", client=client, orders=client_orders)


@app.route('/orders/', methods=["GET"])
def view_orders():
    """View all orders"""
    if 'user_id' not in session:
        return redirect('/')
    
    orders = load_from_pkl(orders_file)
    clients = load_from_pkl(clients_file)
    
    # Sort by most recent
    orders.sort(key=lambda x: x.created_at, reverse=True)
    
    # Create client lookup
    client_lookup = {c.client_id: c.name for c in clients}
    
    return render_template("orders.html", orders=orders, client_lookup=client_lookup)


@app.route('/orders/<int:order_id>/update-status', methods=["POST"])
def update_order_status(order_id):
    """Update order status"""
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    new_status = request.json.get('status')
    orders = load_from_pkl(orders_file)
    order = next((o for o in orders if o.order_id == order_id), None)
    
    if order:
        order.status = new_status
        if new_status == 'Completed':
            order.completed_at = datetime.now().astimezone(pytz.timezone('America/New_York'))
            
            # Move items from Reserved to Customer
            movements = load_from_pkl(movement_file)
            counter = read_counter(counter_file)
            
            for item in order.items:
                counter += 1
                new_movement = Movement(
                    price=0,
                    movement_id=counter,
                    product_id=item['product_id'],
                    qty=item['quantity'],
                    from_location='Reserved',
                    to_location='Customer'
                )
                movements.append(new_movement)
            
            write_counter(counter_file, counter)
            save_to_pkl(movements, movement_file)
        
        save_to_pkl(orders, orders_file)
        return jsonify({'success': True})
    
    return jsonify({'success': False})





@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            locations = load_from_pkl(location_file)
            locations.append(new_location)
            save_to_pkl(locations, location_file)
            return redirect("/locations/")

        except Exception:
            locations = load_from_pkl(location_file)
            return render_template("locations.html", locations=locations)
    else:
        locations = load_from_pkl(location_file)
        return render_template("locations.html", locations=locations)


@app.route('/products/', methods=["POST", "GET"])
def viewProduct():
    """View and manage products"""
    if 'user_id' not in session:
        return redirect('/')
    
    if (request.method == "POST") and ('product_name' in request.form):
        product_name = request.form["product_name"]
        product_price = request.form.get("product_price", 0)
        purchase_price = request.form.get("purchase_price", 0)
        category = request.form.get("category", "Other")
        description = request.form.get("description", "")
        upc = request.form.get("upc", "")
        servings = int(request.form.get("servings", 1))
        points = int(request.form.get("points", 1))
        nutrition_score = int(request.form.get("nutrition_score", 50))
        
        # Handle dietary indicators
        dietary_indicators = []
        if request.form.get("vegan"): dietary_indicators.append("vegan")
        if request.form.get("vegetarian"): dietary_indicators.append("vegetarian")
        if request.form.get("gluten_free"): dietary_indicators.append("gluten-free")
        if request.form.get("low_sodium"): dietary_indicators.append("low-sodium")
        if request.form.get("sugar_free"): dietary_indicators.append("sugar-free")
        if request.form.get("dairy_free"): dietary_indicators.append("dairy-free")
        
        # Handle allergens
        allergens = []
        if request.form.get("milk"): allergens.append("milk")
        if request.form.get("eggs"): allergens.append("eggs")
        if request.form.get("fish"): allergens.append("fish")
        if request.form.get("shellfish"): allergens.append("shellfish")
        if request.form.get("tree_nuts"): allergens.append("tree nuts")
        if request.form.get("peanuts"): allergens.append("peanuts")
        if request.form.get("gluten"): allergens.append("gluten")
        if request.form.get("soybeans"): allergens.append("soybeans")
        
        new_product = Product(
            product_id=product_name,
            price=product_price,
            purchase_price=purchase_price,
            category=category,
            description=description,
            upc=upc,
            servings=servings,
            points=points,
            nutrition_score=nutrition_score,
            dietary_indicators=dietary_indicators,
            allergens=allergens
        )

        try:
            products = load_from_pkl(product_file)
            products.append(new_product)
            save_to_pkl(products, product_file)
            flash('Product added successfully')
            return redirect("/products/")
        except Exception as e:
            flash(f"Error adding product: {e}")
    
    products = load_from_pkl(product_file)
    return render_template("products.html", products=products)


@app.route("/update-product/<name>", methods=["POST", "GET"])
def updateProduct(name):
    """Update product details"""
    if 'user_id' not in session:
        return redirect('/')
    
    products = load_from_pkl(product_file)
    product = next((prod for prod in products if prod.product_id == name), None)

    if not product:
        flash("Product not found")
        return redirect("/products/")

    old_product_id = product.product_id
    if request.method == "POST":
        new_product_id = request.form['product_name']
        new_price = request.form.get('product_price', 0)
        new_purchase_price = request.form.get('purchase_price', 0)
        category = request.form.get("category", "Other")
        description = request.form.get("description", "")
        upc = request.form.get("upc", "")
        servings = int(request.form.get("servings", 1))
        points = int(request.form.get("points", 1))
        nutrition_score = int(request.form.get("nutrition_score", 50))
        
        # Handle dietary indicators
        dietary_indicators = []
        if request.form.get("vegan"): dietary_indicators.append("vegan")
        if request.form.get("vegetarian"): dietary_indicators.append("vegetarian")
        if request.form.get("gluten_free"): dietary_indicators.append("gluten-free")
        if request.form.get("low_sodium"): dietary_indicators.append("low-sodium")
        if request.form.get("sugar_free"): dietary_indicators.append("sugar-free")
        if request.form.get("dairy_free"): dietary_indicators.append("dairy-free")
        
        # Handle allergens
        allergens = []
        if request.form.get("milk"): allergens.append("milk")
        if request.form.get("eggs"): allergens.append("eggs")
        if request.form.get("fish"): allergens.append("fish")
        if request.form.get("shellfish"): allergens.append("shellfish")
        if request.form.get("tree_nuts"): allergens.append("tree nuts")
        if request.form.get("peanuts"): allergens.append("peanuts")
        if request.form.get("gluten"): allergens.append("gluten")
        if request.form.get("soybeans"): allergens.append("soybeans")
        
        product.product_id = new_product_id
        product.price = new_price
        product.purchase_price = new_purchase_price
        product.category = category
        product.description = description
        product.upc = upc
        product.servings = servings
        product.points = points
        product.nutrition_score = nutrition_score
        product.dietary_indicators = dietary_indicators
        product.allergens = allergens

        try:
            save_to_pkl(products, product_file)
            updateProductInMovements(old_product_id, new_product_id)
            flash('Product updated successfully')
            return redirect("/products/")
        except Exception as e:
            flash(f"Error updating product: {e}")
    
    return render_template("update-product.html", product=product)


@app.route("/delete-product/<name>")
def deleteProduct(name):
    """Deletes a product by removing it from the pickle file."""
    try:
        products = load_from_pkl(product_file)
        product_to_delete = next((prod for prod in products if prod.product_id == name), None)

        if not product_to_delete:
            return "Product not found", 404

        products.remove(product_to_delete)
        save_to_pkl(products, product_file)
        return redirect("/products/")
    except Exception as e:
        return f"There was an issue while deleting the Product: {str(e)}"


@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    """Updates a location by modifying the pickle file."""
    try:
        locations = load_from_pkl(location_file)
        location = next((loc for loc in locations if loc.location_id == name), None)

        if not location:
            return "Location not found", 404

        old_location = location.location_id
        # Handles updating location
        if request.method == "POST":
            location.location_id = request.form['location_name']

            try:
                save_to_pkl(locations, location_file)
                updateLocationInMovements(old_location, request.form['location_name'])
                return redirect("/locations/")
            except Exception as e:
                return f"There was an issue while updating the Location: {str(e)}"
        else:
            return render_template("update-location.html", location=location)
    except Exception as e:
        return f"There was an issue while loading the Location: {str(e)}"


@app.route("/delete-location/<name>")
def deleteLocation(name):
    try:
        locations = load_from_pkl(location_file)
        location_to_delete = next((loc for loc in locations if loc.location_id == name), None)

        if not location_to_delete:
            return "Location not found", 404

        locations.remove(location_to_delete)
        save_to_pkl(locations, location_file)
        return redirect("/locations/")
    except Exception as e:
        return f"There was an issue while deleting the Location: {str(e)}"


@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    global price
    products = load_from_pkl(product_file)
    # Handles adding new movement
    if request.method == "POST":
        product_id = request.form["productId"]
        for product in products:
            if product_id == product.product_id:
                price = product.price
        qty = request.form["qty"]
        fromLocation = request.form["fromLocation"]
        toLocation = request.form["toLocation"]
        # gets ID from file and increments it
        counter = read_counter(counter_file)
        counter += 1
        new_movement = Movement(
            price=price,
            movement_id=counter,
            product_id=product_id,
            qty=qty,
            from_location=fromLocation,
            to_location=toLocation
        )
        write_counter(counter_file, counter)
        try:
            movements = load_from_pkl(movement_file)
            movements.append(new_movement)
            save_to_pkl(movements, movement_file)
            return redirect("/movements/")
        except Exception as e:
            return f"There was an issue while adding a new Movement: {str(e)}"
    else:
        products = load_from_pkl(product_file)
        movements = load_from_pkl(movement_file)
        return render_template("movements.html", movements=movements, products=products,
                               locations=remove_specific_locations(load_from_pkl(location_file), ["Customer"]))


@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):
    try:
        movements = load_from_pkl(movement_file)
        movement = next((mov for mov in movements if int(mov.movement_id) == id), None)
        if not movement:
            return "Movement not found", 404

        products = load_from_pkl(product_file)
        product = next((pro for pro in products), None)
        locations = load_from_pkl(location_file)

        if request.method == "POST":
            movement.price = product.price
            movement.product_id = request.form["productId"]
            movement.qty = int(request.form["qty"])
            movement.from_location = request.form["fromLocation"]
            movement.to_location = request.form["toLocation"]

            try:
                save_to_pkl(movements, movement_file)
                return redirect("/movements/")
            except Exception as e:
                return f"There was an issue while updating the Product Movement: {str(e)}"
        else:
            return render_template("update-movement.html", movement=movement, locations=locations, products=products)
    except Exception as e:
        return f"There was an issue while loading the data: {str(e)}"


@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    try:
        movements = load_from_pkl(movement_file)
        movement_to_delete = next((mov for mov in movements if int(mov.movement_id) == id), None)

        if not movement_to_delete:
            return "Movement not found", 404

        movements.remove(movement_to_delete)
        save_to_pkl(movements, movement_file)
        return redirect("/movements/")
    except Exception as e:
        return f"There was an issue while deleting the Product Movement: {str(e)}"


@app.route("/product-balance/", methods=["POST", "GET"])
def productBalanceReport():
    """Shows current inventory"""
    try:
        movements = load_from_pkl(movement_file)

        balancedDict = defaultdict(lambda: defaultdict(dict))
        tempProduct = ''

        for mov in movements:
            if tempProduct == mov.product_id:
                if not (not mov.to_location or "qty" in balancedDict[mov.product_id][mov.to_location]):
                    balancedDict[mov.product_id][mov.to_location]["qty"] = 0
                if not (not mov.from_location or "qty" in balancedDict[mov.product_id][mov.from_location]):
                    balancedDict[mov.product_id][mov.from_location]["qty"] = 0

                # Ensure mov.qty is an integer
                qty_to_add = int(mov.qty)

                if mov.to_location and "qty" in balancedDict[mov.product_id][mov.to_location]:
                    balancedDict[mov.product_id][mov.to_location]["qty"] = int(
                        balancedDict[mov.product_id][mov.to_location]["qty"]) + qty_to_add

                if mov.from_location and "qty" in balancedDict[mov.product_id][mov.from_location]:
                    balancedDict[mov.product_id][mov.from_location]["qty"] = int(
                        balancedDict[mov.product_id][mov.from_location]["qty"]) - qty_to_add
            else:
                tempProduct = mov.product_id
                if mov.to_location and not mov.from_location:
                    balancedDict[mov.product_id][mov.to_location]["qty"] = mov.qty

        return render_template("product-balance.html", movements=balancedDict)
    except Exception as e:
        return f"There was an issue while loading the data: {str(e)}"


@app.route("/revenue-report/", methods=["POST", "GET"])
def revenueReport():
    movements = load_from_pkl(movement_file)
    products = load_from_pkl(product_file)
    revenue = 0
    products_dict = {}
    for mov in movements:
        if mov.to_location == 'Customer':
            for product in products:
                if mov.product_id == product.product_id:  # Checks if product was bought by customer
                    products_dict[product] = mov.qty
                    revenue += (float(product.price) - float(product.purchase_price)) * int(mov.qty)
    return render_template("revenue-report.html", revenue_data="{:.2f}".format(revenue), products=products_dict)


@app.route("/movements/get-from-locations", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    locationDict = defaultdict(int)  # Use a single dictionary for quantities

    movements = load_from_pkl(movement_file)
    for mov in movements:
        if mov.product_id == product:
            locationDict[mov.from_location] += mov.qty

    # Filter out "Customer" and "remove"
    filtered_locations = {loc: qty for loc, qty in locationDict.items() if loc not in ["Customer", "Remove"]}
    return filtered_locations


@app.route("/dup-locations/", methods=["POST", "GET"])
def getDuplicate():
    """Checks if there are any duplicate locations for input handling when updating location"""
    location = request.form["location"]
    locations = load_from_pkl(location_file)
    if len(location) == 0:
        return {"output": False}
    duplicate = any(loc.location_id == location for loc in locations)

    return {"output": not duplicate}


def is_valid_price(price):
    """Checks if the price is valid for input validation when updating the product"""
    # Define the price pattern using a regular expression
    price_pattern = re.compile(r'^\d+\.\d{2}$')

    # Check if the price matches the pattern
    if price_pattern.match(price):
        return True
    else:
        return False


@app.route("/dup-products/", methods=["POST", "GET"])
def getPDuplicate():
    """Checks if there are any duplicate product names when updating product as input validation"""
    product_name = request.form["product_name"]
    product_price = request.form["product_price"]
    purchase_price = request.form["purchase_price"]
    products = load_from_pkl(product_file)
    duplicate = any(prod.product_id == product_name for prod in products)

    return {"output": ((not duplicate) and is_valid_price(product_price) and is_valid_price(purchase_price))}


@app.route('/kiosk', methods=['GET'])
def kiosk_mode():
    """Kiosk shopping interface"""
    return render_template('kiosk_login.html')


@app.route('/kiosk/start', methods=['POST'])
def kiosk_start():
    """Start kiosk shopping session"""
    client_id = request.form.get('client_id')
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    if client:
        session['kiosk_client_id'] = client.client_id
        session['kiosk_mode'] = True
        return redirect('/kiosk/categories')
    else:
        flash('Client ID not found')
        return redirect('/kiosk')


@app.route('/kiosk/categories', methods=['GET'])
def kiosk_categories():
    """Kiosk category selection screen"""
    if 'kiosk_client_id' not in session:
        return redirect('/kiosk')
    
    client_id = session['kiosk_client_id']
    clients = load_from_pkl(clients_file)
    client = next((c for c in clients if c.client_id == client_id), None)
    
    cart = session.get('kiosk_cart', [])
    points_used = sum(item['points'] * item['quantity'] for item in cart)
    points_remaining = client.points_per_visit - points_used
    
    # Calculate MyPlate points
    myplate_points = {'Fruits': 0, 'Vegetables': 0, 'Dairy': 0, 'Proteins': 0, 'Grains': 0, 'Other': 0}
    products = load_from_pkl(product_file)
    for item in cart:
        product = next((p for p in products if p.product_id == item['product_id']), None)
        if product:
            myplate_points[product.category] += item['points'] * item['quantity']
    
    return render_template('kiosk_categories.html', client=client, cart=cart,
                         points_used=points_used, points_remaining=points_remaining,
                         myplate_points=myplate_points)


@app.route('/kiosk/complete', methods=['POST'])
def kiosk_complete():
    """Complete kiosk order"""
    if 'kiosk_client_id' not in session:
        return redirect('/kiosk')
    
    client_id = session['kiosk_client_id']
    cart = session.get('kiosk_cart', [])
    
    if not cart:
        flash('Cart is empty')
        return redirect('/kiosk/categories')
    
    # Create order
    counter = read_counter(counter_file)
    counter += 1
    write_counter(counter_file, counter)
    
    total_points = sum(item['points'] * item['quantity'] for item in cart)
    
    order = Order(
        order_id=counter,
        client_id=client_id,
        items=cart,
        total_points=total_points,
        fulfillment_method='In-Person Pickup',
        status='Completed'
    )
    
    orders = load_from_pkl(orders_file)
    orders.append(order)
    save_to_pkl(orders, orders_file)
    
    # Update inventory
    movements = load_from_pkl(movement_file)
    for item in cart:
        counter += 1
        new_movement = Movement(
            price=0,
            movement_id=counter,
            product_id=item['product_id'],
            qty=item['quantity'],
            from_location='Pantry',
            to_location='Customer'
        )
        movements.append(new_movement)
    
    write_counter(counter_file, counter)
    save_to_pkl(movements, movement_file)
    
    # Clear session
    session.pop('kiosk_client_id', None)
    session.pop('kiosk_cart', None)
    session.pop('kiosk_mode', None)
    
    return render_template('kiosk_complete.html', order=order)


def updateLocationInMovements(old_location, new_location):
    """When a location is changed, it needs to be updated in movements that happened before the location was changed"""
    movements = load_from_pkl(movement_file)

    for mov in movements:
        if mov.from_location == old_location:
            mov.from_location = new_location
        if mov.to_location == old_location:
            mov.to_location = new_location

    save_to_pkl(movements, movement_file)


def updateProductInMovements(old_product, new_product):
    """When a product name is changed, it needs to be updated in movements that happened before the product name was
    changed"""
    try:
        movements = load_from_pkl(movement_file)
        for mov in movements:
            if mov.product_id == old_product:
                mov.product_id = new_product
        save_to_pkl(movements, movement_file)
    except Exception as e:
        return f"There was an issue while updating the Product in Movements: {str(e)}"


if __name__ == "__main__":
    # Create a customer 'location'
    locations = load_from_pkl(location_file)
    if 'Customer' not in [loc.location_id for loc in locations]:
        customer = Location(location_id='Customer')  # Customer is treated as a location
        locations.append(customer)
    if 'Remove' not in [loc.location_id for loc in locations]:
        remove = Location(location_id='Remove')  # Option to remove inventory
        locations.append(remove)
    save_to_pkl(locations, location_file)
    app.run(debug=True)
