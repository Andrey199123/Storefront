"""
Script to update product images with specific food images from Unsplash
"""
from main import app, db
from database import Product

# Mapping of food keywords to specific Unsplash image URLs
FOOD_IMAGES = {
    # Fruits
    'apple': 'https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=400',
    'banana': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400',
    'orange': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400',
    'grape': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400',
    'strawberry': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400',
    'strawberries': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400',
    'blueberry': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400',
    'blueberries': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400',
    'peach': 'https://images.unsplash.com/photo-1629828874514-c1e5103f2150?w=400',
    'pear': 'https://images.unsplash.com/photo-1514756331096-242fdeb70d4a?w=400',
    'mango': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=400',
    'watermelon': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400',
    'pineapple': 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400',
    'cherry': 'https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400',
    'cherries': 'https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400',
    'lemon': 'https://images.unsplash.com/photo-1590502593747-42a996133562?w=400',
    'lime': 'https://images.unsplash.com/photo-1590502593747-42a996133562?w=400',
    'kiwi': 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400',
    'cantaloupe': 'https://images.unsplash.com/photo-1571575173700-afb9492e6a50?w=400',
    'melon': 'https://images.unsplash.com/photo-1571575173700-afb9492e6a50?w=400',
    'fruit': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400',
    
    # Vegetables
    'carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
    'carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400',
    'broccoli': 'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400',
    'spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
    'lettuce': 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400',
    'tomato': 'https://images.unsplash.com/photo-1546470427-227c7369a9b8?w=400',
    'tomatoes': 'https://images.unsplash.com/photo-1546470427-227c7369a9b8?w=400',
    'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82ber?w=400',
    'potatoes': 'https://images.unsplash.com/photo-1518977676601-b53f82ber?w=400',
    'onion': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400',
    'pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400',
    'bell pepper': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400',
    'cucumber': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400',
    'celery': 'https://images.unsplash.com/photo-1580391564590-aeca65c5e2d3?w=400',
    'corn': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400',
    'peas': 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=400',
    'green beans': 'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?w=400',
    'beans': 'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?w=400',
    'cabbage': 'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?w=400',
    'cauliflower': 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=400',
    'zucchini': 'https://images.unsplash.com/photo-1563252722-6434563a985d?w=400',
    'squash': 'https://images.unsplash.com/photo-1570586437263-ab629fccc818?w=400',
    'asparagus': 'https://images.unsplash.com/photo-1515471209610-dae1c92d8777?w=400',
    'mushroom': 'https://images.unsplash.com/photo-1504545102780-26774c1bb073?w=400',
    'mushrooms': 'https://images.unsplash.com/photo-1504545102780-26774c1bb073?w=400',
    'kale': 'https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?w=400',
    'salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
    'vegetable': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
    
    # Dairy
    'milk': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400',
    'cheese': 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400',
    'cheddar': 'https://images.unsplash.com/photo-1618164436241-4473940d1f5c?w=400',
    'yogurt': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400',
    'butter': 'https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400',
    'cream': 'https://images.unsplash.com/photo-1625938145744-533e82abcab3?w=400',
    'ice cream': 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400',
    'egg': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400',
    'eggs': 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400',
    'cottage cheese': 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400',
    
    # Proteins
    'chicken': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400',
    'beef': 'https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400',
    'steak': 'https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400',
    'pork': 'https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=400',
    'fish': 'https://images.unsplash.com/photo-1510130387422-82bed34b37e9?w=400',
    'salmon': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
    'tuna': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400',
    'shrimp': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=400',
    'turkey': 'https://images.unsplash.com/photo-1574672280600-4accfa5b6f98?w=400',
    'ham': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=400',
    'bacon': 'https://images.unsplash.com/photo-1606851091851-e8c8c0fca5ba?w=400',
    'sausage': 'https://images.unsplash.com/photo-1601628828688-632f38a5a7d0?w=400',
    'tofu': 'https://images.unsplash.com/photo-1628689469838-524a4a973b8e?w=400',
    'nuts': 'https://images.unsplash.com/photo-1536816579748-4ecb3f03d72a?w=400',
    'peanut': 'https://images.unsplash.com/photo-1567892320421-1c657571ea4a?w=400',
    'almond': 'https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=400',
    'lentils': 'https://images.unsplash.com/photo-1585996746495-4b5e8e4d0d8a?w=400',
    
    # Grains
    'bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400',
    'rice': 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400',
    'pasta': 'https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=400',
    'cereal': 'https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=400',
    'oatmeal': 'https://images.unsplash.com/photo-1517673400267-0251440c45dc?w=400',
    'oats': 'https://images.unsplash.com/photo-1517673400267-0251440c45dc?w=400',
    'tortilla': 'https://images.unsplash.com/photo-1612966986610-4c9b8a3d8f5a?w=400',
    'bagel': 'https://images.unsplash.com/photo-1585445490387-f47934b73b54?w=400',
    'muffin': 'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=400',
    'cracker': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
    'crackers': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
    'flour': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400',
    'wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400',
    'quinoa': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
    
    # Other/Canned/Misc
    'soup': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400',
    'sauce': 'https://images.unsplash.com/photo-1472476443507-c7a5948772fc?w=400',
    'tomato sauce': 'https://images.unsplash.com/photo-1472476443507-c7a5948772fc?w=400',
    'juice': 'https://images.unsplash.com/photo-1534353473418-4cfa6c56fd38?w=400',
    'water': 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400',
    'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400',
    'tea': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400',
    'honey': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400',
    'jam': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400',
    'jelly': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400',
    'peanut butter': 'https://images.unsplash.com/photo-1598511726623-d2e9996892f0?w=400',
    'oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
    'olive oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400',
    'sugar': 'https://images.unsplash.com/photo-1581268752205-e9a0c8e7e8b0?w=400',
    'salt': 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=400',
    'spice': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400',
    'canned': 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400',
}

# Category fallback images
CATEGORY_IMAGES = {
    'Fruits': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400',
    'Vegetables': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
    'Dairy': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400',
    'Proteins': 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400',
    'Grains': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400',
    'Other': 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=400',
}

def find_best_image(product_name, category):
    """Find the best matching image for a product"""
    name_lower = product_name.lower()
    
    # Check for exact or partial matches in food images
    for keyword, url in FOOD_IMAGES.items():
        if keyword in name_lower:
            return url
    
    # Fall back to category image
    return CATEGORY_IMAGES.get(category, CATEGORY_IMAGES['Other'])

def update_all_images():
    """Update all product images"""
    with app.app_context():
        products = Product.query.all()
        updated = 0
        
        for product in products:
            new_image = find_best_image(product.product_id, product.category)
            if product.image_url != new_image:
                product.image_url = new_image
                updated += 1
                print(f"Updated: {product.product_id} -> {new_image[:50]}...")
        
        db.session.commit()
        print(f"\nUpdated {updated} product images")

if __name__ == '__main__':
    update_all_images()
