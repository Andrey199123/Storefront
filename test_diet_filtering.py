#!/usr/bin/env python3
"""
Test script to verify diet filtering functionality
"""

import sys
sys.path.append('.')
from main import load_from_pkl

def test_diet_filtering():
    print("Testing Diet Filtering Feature\n")
    print("=" * 60)
    
    # Load products
    products = load_from_pkl('product.pkl')
    
    if not products:
        print("❌ No products found. Run setup_sample_data.py first!")
        return
    
    print(f"✓ Loaded {len(products)} products\n")
    
    # Test filters
    filters = {
        "vegan": [],
        "vegetarian": [],
        "gluten-free": [],
        "dairy-free": [],
        "low-sodium": [],
        "sugar-free": []
    }
    
    # Categorize products by dietary indicators
    for product in products:
        for indicator in product.dietary_indicators:
            if indicator in filters:
                filters[indicator].append(product.product_id)
    
    # Display results
    print("DIETARY FILTER RESULTS:")
    print("-" * 60)
    
    for diet_type, product_list in filters.items():
        print(f"\n🔍 {diet_type.upper()}: {len(product_list)} products")
        if product_list:
            for i, product_name in enumerate(product_list[:5], 1):
                print(f"   {i}. {product_name}")
            if len(product_list) > 5:
                print(f"   ... and {len(product_list) - 5} more")
    
    # Test combination filters
    print("\n" + "=" * 60)
    print("COMBINATION FILTER TESTS:")
    print("-" * 60)
    
    # Vegan + Gluten-Free
    vegan_gf = [p for p in products if "vegan" in p.dietary_indicators and "gluten-free" in p.dietary_indicators]
    print(f"\n🌱 Vegan + Gluten-Free: {len(vegan_gf)} products")
    for p in vegan_gf[:5]:
        print(f"   - {p.product_id} ({p.category})")
    
    # Vegetarian + Low-Sodium
    veg_ls = [p for p in products if "vegetarian" in p.dietary_indicators and "low-sodium" in p.dietary_indicators]
    print(f"\n🥕 Vegetarian + Low-Sodium: {len(veg_ls)} products")
    for p in veg_ls[:5]:
        print(f"   - {p.product_id} ({p.category})")
    
    # Products by category with dietary indicators
    print("\n" + "=" * 60)
    print("PRODUCTS BY CATEGORY WITH DIETARY INDICATORS:")
    print("-" * 60)
    
    categories = {}
    for product in products:
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append(product)
    
    for category, prods in sorted(categories.items()):
        print(f"\n📦 {category.upper()}: {len(prods)} products")
        for p in prods[:3]:
            indicators = ", ".join(p.dietary_indicators) if p.dietary_indicators else "None"
            print(f"   - {p.product_id}: [{indicators}]")
        if len(prods) > 3:
            print(f"   ... and {len(prods) - 3} more")
    
    print("\n" + "=" * 60)
    print("✅ Diet filtering test complete!")
    print("\nTo test in the web interface:")
    print("1. Run: python main.py")
    print("2. Visit: http://127.0.0.1:5000/shop")
    print("3. Login with Client ID: C00001")
    print("4. Navigate to any category and use the filter buttons")

if __name__ == '__main__':
    test_diet_filtering()
