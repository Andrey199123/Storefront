#!/usr/bin/env python3
"""
Script to add image URLs to all existing products (SQL version)
Uses free Unsplash images for food items
"""

from flask import Flask
from database import db, Product

# Create app context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Image mapping for each product
PRODUCT_IMAGES = {
    # Fruits
    "Apples": "https://media.self.com/photos/5b6b0b0cbb7f036f7f5cbcfa/4:3/w_2560%2Cc_limit/apples.jpg",
    "Bananas": "https://blog-images-1.pharmeasy.in/blog/production/wp-content/uploads/2021/01/30152155/shutterstock_518328943-1.jpg",
    "Oranges": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQR1d55KRpVZtNZDCGxi193hqjtIhz1Nb-OBQ&s",
    "Strawberries": "https://www.gardentech.com/-/media/project/oneweb/gardentech/images/blog/how-to-grow-your-own-tasty-strawberries/strawberries-header-og.jpg",

    # Vegetables
    "Broccoli": "https://images.squarespace-cdn.com/content/v1/5b5aa0922487fd1ce32c117a/1547765015801-FSR1DVSKCZU3PAYWIRQG/broccoli.jpg",
    "Carrots": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStL5RNQUBSIsu4dIr3lpIBVMwFX7I0Gn5H_Q&s",
    "Lettuce": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Iceberg_lettuce_in_SB.jpg/1200px-Iceberg_lettuce_in_SB.jpg",
    "Tomatoes": "https://images-prod.healthline.com/hlcmsresource/images/AN_images/tomatoes-1296x728-feature.jpg",
    "Spinach": "https://i0.wp.com/post.healthline.com/wp-content/uploads/2019/05/spinach-1296x728-header.jpg?w=1155&h=1528",

    # Dairy
    "Milk - 2%": "https://static1.squarespace.com/static/6508404030fe0519d54c5c79/652d5f6de438172996f955d7/652d606fe438172996f9a456/1749142856255/fresh-milk-mug-jug-wooden-table-scaled-584x388.jpeg?format=1500w",
    "Almond Milk": "https://40aprons.com/wp-content/uploads/2019/07/how-to-make-almond-milk-2-500x500.jpg",
    "Yogurt - Plain": "https://pha-cms.s3.amazonaws.com/image/555/medium.jpg?1498143175",
    "Cheese - Cheddar": "https://pearlvalleycheese.com/cdn/shop/files/sharp-cheddar-slices_1.jpg?v=1755888466&width=2400",
    "Eggs": "https://cdn.britannica.com/94/151894-050-F72A5317/Brown-eggs.jpg",
    "Coconut Yogurt": "https://thecoconutmama.com/wp-content/uploads/2012/11/coconut-yogurt-shut-scaled.webp",

    # Proteins
    "Chicken Breast": "https://www.everydaycheapskate.com/wp-content/uploads/20250407-how-to-cook-boneless-skinless-chicken-breast-on-a-cutting-board-with-thyme-garlic-and-red-peppercorns.png",
    "Ground Beef": "https://justcook.butcherbox.com/wp-content/uploads/2019/06/ground-beef.jpg",
    "Canned Tuna": "https://cdn.apartmenttherapy.info/image/upload/v1712076214/k/Edit/Canned_Tuna_027-cropped.jpg",
    "Black Beans": "https://www.feastingathome.com/wp-content/uploads/2025/05/Black-Bean-Recipe-11.jpg",
    "Peanut Butter": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQWhqaHgIkE_KfZz0Isf5l8Ui8Kh-EMORn83Q&s",
    "Tofu - Firm": "https://www.foodinjapan.org/wp-content/uploads/2023/02/25378446_m-1.jpg",
    "Lentils - Dry": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWcKrOShwKNH5mYu3fCnf3CkThEtQnGbS6hg&s",

    # Grains
    "Whole Wheat Bread": "https://www.organicsbylee.com/wp-content/uploads/2019/03/wholewheatbread-copy.jpg",
    "Gluten-Free Bread": "https://www.seasonalcravings.com/wp-content/uploads/2024/10/HR-GF-White-Bread-14-scaled.jpg",
    "Brown Rice": "https://img.etimg.com/thumb/width-1200,height-900,imgsize-242102,resizemode-75,msid-120284877/magazines/panache/is-brown-rice-as-healthy-as-you-think-new-study-uncovers-concerning-toxic-arsenic-risk.jpg",
    "Pasta - Whole Wheat": "https://hips.hearstapps.com/hmg-prod/images/whole-wheat-pasta-gettyimages-488392474-64359d6e6fa92.jpg?crop=0.6648xw:1xh;center,top&resize=640:*",
    "Pasta - Gluten Free": "https://www.mamaknowsglutenfree.com/wp-content/uploads/2024/06/featured-gluten-free-pasta-master-recipe_.jpg",
    "Oatmeal": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJXf3g-Oh2vxxkRj-LuHdmn1YK6djgsj-cww&s",
    "Quinoa": "https://www.artfrommytable.com/wp-content/uploads/2022/01/instant_pot_quinoa_square.jpg",
    "Cereal - Whole Grain": "https://i0.wp.com/thecookstreat.com/wp-content/uploads/2019/01/SkilletBreakfastCereal.jpg?resize=800%2C533&ssl=1",

    # Other
    "Olive Oil": "https://health.ucdavis.edu/media-resources/contenthub/post/internet/good-food/2024/04/images-body/olive-oil-health-benefits.jpg",
    "Canned Tomatoes": "https://www.unlockfood.ca/EatRightOntario/media/Website-images-resized/bigstock-Open-Tin-Of-Chopped-Tomatoes-119675888.jpg",
    "Soup - Vegetable": "https://cdn.loveandlemons.com/wp-content/uploads/2019/12/vegetable-soup.jpg",
    "Soup - Low Sodium": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSw0eHjjNLQXNT8A2etUZ-bpSqAZw_k46qXrA&s",
    "Honey": "https://cdn.mos.cms.futurecdn.net/v2/t:0,l:592,cw:3558,ch:2669,q:80,w:2560/zcz8f72orNC9GKgm3tbqMY.jpg",
    "Maple Syrup": "https://www.cleanjuice.com/wp-content/uploads/2023/06/Pure-Maple-Syrup-2-scaled-1.jpeg",
}

def add_images_to_products():
    print("Adding images to products in SQL database...")

    with app.app_context():
        products = Product.query.all()
        updated_count = 0

        for product in products:
            if product.product_id in PRODUCT_IMAGES:
                product.image_url = PRODUCT_IMAGES[product.product_id]
                updated_count += 1
                print(f"  ✓ Added image to {product.product_id}")
            else:
                print(f"  ⚠ No image found for {product.product_id}")

        db.session.commit()

    print(f"\n✅ Successfully updated {updated_count} products with images!")
    print("Refresh your browser to see the changes.")

if __name__ == '__main__':
    add_images_to_products()
