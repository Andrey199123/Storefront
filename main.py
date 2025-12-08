# SmartChoice Pantry System - Food Pantry Management Software
# SQL Database Version
from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
from collections import defaultdict
from datetime import datetime, timedelta
import os
import re
import pytz
from werkzeug.security import check_password_hash, generate_password_hash
from database import db, User, Product as DBProduct, Client as DBClient, Location as DBLocation
from database import Movement as DBMovement, Order as DBOrder, Appointment as DBAppointment, Counter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    # Ensure default locations exist
    for loc_id in ['Customer', 'Reserved', 'Pantry']:
        if not DBLocation.query.filter_by(location_id=loc_id).first():
            db.session.add(DBLocation(location_id=loc_id))
    db.session.commit()


# Helper function to remove specific locations
def remove_specific_locations(locations, names_to_remove):
    return [location for location in locations if location.location_id not in names_to_remove]


# Helper to convert DB Product to dict-like object for templates
class ProductProxy:
    def __init__(self, db_product):
        self.product_id = db_product.product_id
        self.price = db_product.price
        self.purchase_price = db_product.purchase_price
        self.category = db_product.category
        self.description = db_product.description
        self.upc = db_product.upc
        self.servings = db_product.servings
        self.points = db_product.points
        self.nutrition_score = db_product.nutrition_score
        self.dietary_indicators = db_product.get_dietary_indicators()
        self.allergens = db_product.get_allergens()
        self.image_url = db_product.image_url
        self.date_created = db_product.date_created
        self.available_qty = 0  # Will be set by inventory calculation


class ClientProxy:
    def __init__(self, db_client):
        self.client_id = db_client.client_id
        self.name = db_client.name
        self.email = db_client.email
        self.phone = db_client.phone
        self.address = db_client.address
        self.household_size = db_client.household_size
        self.language = db_client.language
        self.eligibility_groups = db_client.get_eligibility_groups()
        self.points_per_visit = db_client.points_per_visit
        self.visits_per_period = db_client.visits_per_period
        self.allergens = db_client.get_allergens()
        self.dietary_prefs = db_client.get_dietary_prefs()
        self.date_created = db_client.date_created
        self.last_visit = db_client.last_visit


class LocationProxy:
    def __init__(self, db_location):
        self.location_id = db_location.location_id
        self.date_created = db_location.date_created


class MovementProxy:
    def __init__(self, db_movement):
        self.movement_id = db_movement.movement_id
        self.product_id = db_movement.product_id
        self.qty = db_movement.qty
        self.price = db_movement.price
        self.from_location = db_movement.from_location
        self.to_location = db_movement.to_location
        self.movement_time = db_movement.movement_time


class OrderProxy:
    def __init__(self, db_order):
        self.order_id = db_order.order_id
        self.client_id = db_order.client_id
        self.items = db_order.get_items()
        self.total_points = db_order.total_points
        self.fulfillment_method = db_order.fulfillment_method
        self.status = db_order.status
        self.pickup_time = db_order.pickup_time
        self.created_at = db_order.created_at
        self.completed_at = db_order.completed_at


@app.route('/', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        form_type = request.form['form_type']
        if form_type == 'login':
            username_or_email = request.form['username_or_email']
            password = request.form['password']
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.username
                session['user_role'] = user.role
                flash('Login successful')
                return redirect('/home')
            else:
                flash('Invalid username/email or password')
        elif form_type == 'register':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            if User.query.filter_by(username=username).first():
                flash('Username already exists')
            elif User.query.filter_by(email=email).first():
                flash('Email already exists')
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(name=name, username=username, email=email, 
                              password=hashed_password, role='staff')
                db.session.add(new_user)
                db.session.commit()
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
    client = DBClient.query.filter_by(client_id=client_id).first()
    
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
    db_client = DBClient.query.filter_by(client_id=client_id).first()
    client = ClientProxy(db_client)
    
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
    
    for item in cart:
        product = DBProduct.query.filter_by(product_id=item['product_id']).first()
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
    db_client = DBClient.query.filter_by(client_id=client_id).first()
    client = ClientProxy(db_client)
    
    # Get dietary filters from query parameters
    diet_filters = request.args.getlist('diet')
    
    # Filter products by category
    db_products = DBProduct.query.filter_by(category=category).all()
    
    category_products = []
    for db_product in db_products:
        product = ProductProxy(db_product)
        
        # Apply dietary filters if any
        if diet_filters:
            if not all(diet_filter in product.dietary_indicators for diet_filter in diet_filters):
                continue
        
        # Calculate available inventory
        inventory = 0
        movements = DBMovement.query.filter_by(product_id=product.product_id).all()
        for mov in movements:
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
    
    product = DBProduct.query.filter_by(product_id=product_id).first()
    
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
    db_client = DBClient.query.filter_by(client_id=client_id).first()
    client = ClientProxy(db_client)
    
    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty')
        return redirect('/shop/categories')
    
    if request.method == 'POST':
        fulfillment_method = request.form.get('fulfillment_method')
        pickup_time = request.form.get('pickup_time')
        
        # Create order
        order_id = Counter.get_next_id()
        total_points = sum(item['points'] * item['quantity'] for item in cart)
        
        order = DBOrder(
            order_id=order_id,
            client_id=client_id,
            total_points=total_points,
            fulfillment_method=fulfillment_method,
            pickup_time=pickup_time
        )
        order.set_items(cart)
        db.session.add(order)
        
        # Update inventory - reserve items
        for item in cart:
            movement_id = Counter.get_next_id()
            new_movement = DBMovement(
                movement_id=movement_id,
                product_id=item['product_id'],
                qty=item['quantity'],
                price=0,
                from_location='Pantry',
                to_location='Reserved'
            )
            db.session.add(new_movement)
        
        db.session.commit()
        
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
    
    db_order = DBOrder.query.filter_by(order_id=order_id).first()
    
    if not db_order:
        flash('Order not found')
        return redirect('/shop/categories')
    
    order = OrderProxy(db_order)
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
    
    db_products = DBProduct.query.all()
    products = [ProductProxy(p) for p in db_products]
    
    db_locations = DBLocation.query.all()
    locations = [LocationProxy(l) for l in db_locations]
    
    db_clients = DBClient.query.all()
    clients = [ClientProxy(c) for c in db_clients]
    
    db_orders = DBOrder.query.order_by(DBOrder.created_at.desc()).limit(10).all()
    recent_orders = [OrderProxy(o) for o in db_orders]
    
    # Get pending orders count
    pending_orders = DBOrder.query.filter_by(status='Pending').count()
    
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
        counter = Counter.get_next_id()
        client_id = f"C{counter:05d}"
        
        new_client = DBClient(
            client_id=client_id,
            name=name,
            email=email,
            phone=phone,
            household_size=household_size,
            language=language
        )
        
        try:
            db.session.add(new_client)
            db.session.commit()
            flash(f'Client {name} added successfully! Client ID: {client_id}')
            return redirect("/clients/")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding client: {e}")
    
    db_clients = DBClient.query.all()
    clients = [ClientProxy(c) for c in db_clients]
    return render_template("clients.html", clients=clients)


@app.route('/clients/<client_id>', methods=["GET", "POST"])
def view_client_detail(client_id):
    """View and edit client details"""
    if 'user_id' not in session:
        return redirect('/')
    
    db_client = DBClient.query.filter_by(client_id=client_id).first()
    
    if not db_client:
        flash('Client not found')
        return redirect('/clients/')
    
    if request.method == "POST":
        db_client.name = request.form["client_name"]
        db_client.email = request.form.get("client_email", "")
        db_client.phone = request.form.get("client_phone", "")
        db_client.household_size = int(request.form.get("household_size", 1))
        db_client.language = request.form.get("language", "English")
        db_client.points_per_visit = int(request.form.get("points_per_visit", 100))
        
        db.session.commit()
        flash('Client updated successfully')
        return redirect('/clients/')
    
    client = ClientProxy(db_client)
    
    # Get client's order history
    db_orders = DBOrder.query.filter_by(client_id=client_id).order_by(DBOrder.created_at.desc()).all()
    client_orders = [OrderProxy(o) for o in db_orders]
    
    return render_template("client_detail.html", client=client, orders=client_orders)


@app.route('/orders/', methods=["GET"])
def view_orders():
    """View all orders"""
    if 'user_id' not in session:
        return redirect('/')
    
    db_orders = DBOrder.query.order_by(DBOrder.created_at.desc()).all()
    orders = [OrderProxy(o) for o in db_orders]
    
    # Create client lookup
    db_clients = DBClient.query.all()
    client_lookup = {c.client_id: c.name for c in db_clients}
    
    return render_template("orders.html", orders=orders, client_lookup=client_lookup)


@app.route('/orders/<int:order_id>/update-status', methods=["POST"])
def update_order_status(order_id):
    """Update order status"""
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    new_status = request.json.get('status')
    order = DBOrder.query.filter_by(order_id=order_id).first()
    
    if order:
        order.status = new_status
        if new_status == 'Completed':
            order.completed_at = datetime.now(pytz.timezone('America/New_York'))
            
            # Move items from Reserved to Customer
            items = order.get_items()
            for item in items:
                movement_id = Counter.get_next_id()
                new_movement = DBMovement(
                    movement_id=movement_id,
                    product_id=item['product_id'],
                    qty=item['quantity'],
                    price=0,
                    from_location='Reserved',
                    to_location='Customer'
                )
                db.session.add(new_movement)
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False})


@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = DBLocation(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/locations/")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding location: {e}")
    
    db_locations = DBLocation.query.all()
    locations = [LocationProxy(l) for l in db_locations]
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
        
        new_product = DBProduct(
            product_id=product_name,
            price=product_price,
            purchase_price=purchase_price,
            category=category,
            description=description,
            upc=upc,
            servings=servings,
            points=points,
            nutrition_score=nutrition_score
        )
        new_product.set_dietary_indicators(dietary_indicators)
        new_product.set_allergens(allergens)

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully')
            return redirect("/products/")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding product: {e}")
    
    db_products = DBProduct.query.all()
    products = [ProductProxy(p) for p in db_products]
    return render_template("products.html", products=products)


@app.route("/update-product/<name>", methods=["POST", "GET"])
def updateProduct(name):
    """Update product details"""
    if 'user_id' not in session:
        return redirect('/')
    
    product = DBProduct.query.filter_by(product_id=name).first()

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
        product.set_dietary_indicators(dietary_indicators)
        product.set_allergens(allergens)

        try:
            # Update product_id in movements if changed
            if old_product_id != new_product_id:
                movements = DBMovement.query.filter_by(product_id=old_product_id).all()
                for mov in movements:
                    mov.product_id = new_product_id
            
            db.session.commit()
            flash('Product updated successfully')
            return redirect("/products/")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product: {e}")
    
    product_proxy = ProductProxy(product)
    return render_template("update-product.html", product=product_proxy)


@app.route("/delete-product/<name>")
def deleteProduct(name):
    """Deletes a product"""
    try:
        product = DBProduct.query.filter_by(product_id=name).first()

        if not product:
            return "Product not found", 404

        db.session.delete(product)
        db.session.commit()
        return redirect("/products/")
    except Exception as e:
        db.session.rollback()
        return f"There was an issue while deleting the Product: {str(e)}"


@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    """Updates a location"""
    try:
        location = DBLocation.query.filter_by(location_id=name).first()

        if not location:
            return "Location not found", 404

        old_location = location.location_id
        if request.method == "POST":
            new_location_id = request.form['location_name']
            location.location_id = new_location_id

            try:
                # Update location_id in movements if changed
                if old_location != new_location_id:
                    movements_from = DBMovement.query.filter_by(from_location=old_location).all()
                    for mov in movements_from:
                        mov.from_location = new_location_id
                    
                    movements_to = DBMovement.query.filter_by(to_location=old_location).all()
                    for mov in movements_to:
                        mov.to_location = new_location_id
                
                db.session.commit()
                return redirect("/locations/")
            except Exception as e:
                db.session.rollback()
                return f"There was an issue while updating the Location: {str(e)}"
        else:
            location_proxy = LocationProxy(location)
            return render_template("update-location.html", location=location_proxy)
    except Exception as e:
        return f"There was an issue while loading the Location: {str(e)}"


@app.route("/delete-location/<name>")
def deleteLocation(name):
    try:
        location = DBLocation.query.filter_by(location_id=name).first()

        if not location:
            return "Location not found", 404

        db.session.delete(location)
        db.session.commit()
        return redirect("/locations/")
    except Exception as e:
        db.session.rollback()
        return f"There was an issue while deleting the Location: {str(e)}"


@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    db_products = DBProduct.query.all()
    products = [ProductProxy(p) for p in db_products]
    
    if request.method == "POST":
        product_id = request.form["productId"]
        product = DBProduct.query.filter_by(product_id=product_id).first()
        price = product.price if product else 0
        
        qty = request.form["qty"]
        fromLocation = request.form["fromLocation"]
        toLocation = request.form["toLocation"]
        
        movement_id = Counter.get_next_id()
        new_movement = DBMovement(
            movement_id=movement_id,
            product_id=product_id,
            qty=qty,
            price=price,
            from_location=fromLocation if fromLocation else None,
            to_location=toLocation if toLocation else None
        )
        
        try:
            db.session.add(new_movement)
            db.session.commit()
            return redirect("/movements/")
        except Exception as e:
            db.session.rollback()
            return f"There was an issue while adding a new Movement: {str(e)}"
    else:
        db_movements = DBMovement.query.all()
        movements = [MovementProxy(m) for m in db_movements]
        
        db_locations = DBLocation.query.all()
        locations = remove_specific_locations([LocationProxy(l) for l in db_locations], ["Customer"])
        
        return render_template("movements.html", movements=movements, products=products, locations=locations)


@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):
    try:
        movement = DBMovement.query.filter_by(movement_id=id).first()
        if not movement:
            return "Movement not found", 404

        db_products = DBProduct.query.all()
        products = [ProductProxy(p) for p in db_products]
        
        db_locations = DBLocation.query.all()
        locations = [LocationProxy(l) for l in db_locations]

        if request.method == "POST":
            product_id = request.form["productId"]
            product = DBProduct.query.filter_by(product_id=product_id).first()
            
            movement.price = product.price if product else 0
            movement.product_id = product_id
            movement.qty = int(request.form["qty"])
            movement.from_location = request.form["fromLocation"] if request.form["fromLocation"] else None
            movement.to_location = request.form["toLocation"] if request.form["toLocation"] else None

            try:
                db.session.commit()
                return redirect("/movements/")
            except Exception as e:
                db.session.rollback()
                return f"There was an issue while updating the Product Movement: {str(e)}"
        else:
            movement_proxy = MovementProxy(movement)
            return render_template("update-movement.html", movement=movement_proxy, locations=locations, products=products)
    except Exception as e:
        return f"There was an issue while loading the data: {str(e)}"


@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    try:
        movement = DBMovement.query.filter_by(movement_id=id).first()

        if not movement:
            return "Movement not found", 404

        db.session.delete(movement)
        db.session.commit()
        return redirect("/movements/")
    except Exception as e:
        db.session.rollback()
        return f"There was an issue while deleting the Product Movement: {str(e)}"


@app.route("/product-balance/", methods=["POST", "GET"])
def productBalanceReport():
    """Shows current inventory"""
    try:
        movements = DBMovement.query.all()

        balancedDict = defaultdict(lambda: defaultdict(dict))
        tempProduct = ''

        for mov in movements:
            if tempProduct == mov.product_id:
                if not (not mov.to_location or "qty" in balancedDict[mov.product_id][mov.to_location]):
                    balancedDict[mov.product_id][mov.to_location]["qty"] = 0
                if not (not mov.from_location or "qty" in balancedDict[mov.product_id][mov.from_location]):
                    balancedDict[mov.product_id][mov.from_location]["qty"] = 0

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
    movements = DBMovement.query.filter_by(to_location='Customer').all()
    revenue = 0
    products_dict = {}
    
    for mov in movements:
        product = DBProduct.query.filter_by(product_id=mov.product_id).first()
        if product:
            product_proxy = ProductProxy(product)
            products_dict[product_proxy] = mov.qty
            revenue += (float(product.price) - float(product.purchase_price)) * int(mov.qty)
    
    return render_template("revenue-report.html", revenue_data="{:.2f}".format(revenue), products=products_dict)


@app.route("/movements/get-from-locations", methods=["POST"])
def getLocations():
    product_id = request.form["productId"]
    locationDict = defaultdict(int)

    movements = DBMovement.query.filter_by(product_id=product_id).all()
    for mov in movements:
        if mov.from_location:
            locationDict[mov.from_location] += mov.qty

    # Filter out "Customer" and "Remove"
    filtered_locations = {loc: qty for loc, qty in locationDict.items() if loc not in ["Customer", "Remove"]}
    return filtered_locations


@app.route("/dup-locations/", methods=["POST", "GET"])
def getDuplicate():
    """Checks if there are any duplicate locations"""
    location = request.form["location"]
    if len(location) == 0:
        return {"output": False}
    
    existing = DBLocation.query.filter_by(location_id=location).first()
    return {"output": not bool(existing)}


def is_valid_price(price):
    """Checks if the price is valid"""
    price_pattern = re.compile(r'^\d+\.\d{2}$')
    return bool(price_pattern.match(price))


@app.route("/dup-products/", methods=["POST", "GET"])
def getPDuplicate():
    """Checks if there are any duplicate product names"""
    product_name = request.form["product_name"]
    product_price = request.form["product_price"]
    purchase_price = request.form["purchase_price"]
    
    existing = DBProduct.query.filter_by(product_id=product_name).first()
    duplicate = bool(existing)

    return {"output": ((not duplicate) and is_valid_price(product_price) and is_valid_price(purchase_price))}


@app.route('/kiosk', methods=['GET'])
def kiosk_mode():
    """Kiosk shopping interface"""
    return render_template('kiosk_login.html')


@app.route('/kiosk/start', methods=['POST'])
def kiosk_start():
    """Start kiosk shopping session"""
    client_id = request.form.get('client_id')
    client = DBClient.query.filter_by(client_id=client_id).first()
    
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
    db_client = DBClient.query.filter_by(client_id=client_id).first()
    client = ClientProxy(db_client)
    
    cart = session.get('kiosk_cart', [])
    points_used = sum(item['points'] * item['quantity'] for item in cart)
    points_remaining = client.points_per_visit - points_used
    
    # Calculate MyPlate points
    myplate_points = {'Fruits': 0, 'Vegetables': 0, 'Dairy': 0, 'Proteins': 0, 'Grains': 0, 'Other': 0}
    for item in cart:
        product = DBProduct.query.filter_by(product_id=item['product_id']).first()
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
    order_id = Counter.get_next_id()
    total_points = sum(item['points'] * item['quantity'] for item in cart)
    
    order = DBOrder(
        order_id=order_id,
        client_id=client_id,
        total_points=total_points,
        fulfillment_method='In-Person Pickup',
        status='Completed'
    )
    order.set_items(cart)
    db.session.add(order)
    
    # Update inventory
    for item in cart:
        movement_id = Counter.get_next_id()
        new_movement = DBMovement(
            movement_id=movement_id,
            product_id=item['product_id'],
            qty=item['quantity'],
            price=0,
            from_location='Pantry',
            to_location='Customer'
        )
        db.session.add(new_movement)
    
    db.session.commit()
    
    # Clear session
    session.pop('kiosk_client_id', None)
    session.pop('kiosk_cart', None)
    session.pop('kiosk_mode', None)
    
    order_proxy = OrderProxy(order)
    return render_template('kiosk_complete.html', order=order_proxy)


if __name__ == "__main__":
    app.run(debug=True)
