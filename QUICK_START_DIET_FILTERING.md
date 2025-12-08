# Quick Start: Diet Filtering Feature

## 🚀 Get Started in 3 Steps

### Step 1: Setup Data
```bash
python3 setup_sample_data.py
python3 add_inventory.py
```

### Step 2: Start Application
```bash
python3 main.py
```

### Step 3: Test the Feature
1. Open browser: http://127.0.0.1:5000/shop
2. Login with Client ID: **C00001**
3. Click any category (e.g., "Proteins")
4. Use the filter buttons at the top!

## 🎯 Try These Examples

### Example 1: Find Vegan Options
1. Go to **Proteins** category
2. Click **🌱 Vegan** button
3. See: Tofu, Lentils, Black Beans, Peanut Butter

### Example 2: Find Gluten-Free Grains
1. Go to **Grains** category
2. Click **🌾 Gluten-Free** button
3. See: Brown Rice, Quinoa, Gluten-Free Bread, Oatmeal

### Example 3: Combine Filters
1. Go to **Proteins** category
2. Click **🌱 Vegan** + **🌾 Gluten-Free**
3. See only products with BOTH tags

### Example 4: Low Sodium Options
1. Go to **Vegetables** category
2. Click **🧂 Low Sodium** button
3. See: Broccoli, Lettuce, Spinach

## 📊 What You'll See

### Filter Buttons
```
🌱 Vegan  🥕 Vegetarian  🌾 Gluten-Free  
🥛 Dairy-Free  🧂 Low Sodium  🍬 Sugar-Free  
[Clear All]
```

### Active Filter
- Blue background with white text
- Products automatically filtered

### Product Cards
- Show dietary badges below nutrition score
- Example: `vegan` `gluten-free` `low-sodium`

## 🔍 Product Counts by Filter

- **Vegan**: 24 products
- **Vegetarian**: 4 products
- **Gluten-Free**: 27 products
- **Dairy-Free**: 3 products
- **Low-Sodium**: 10 products
- **Sugar-Free**: 1 product

## 💡 Tips

1. **Multiple Filters**: Click multiple buttons to narrow results
2. **Clear All**: Reset all filters with one click
3. **No Results**: If no products match, try fewer filters
4. **Categories**: Filters work in all 6 categories
5. **Real-Time**: No page reload needed!

## 🐛 Troubleshooting

### No products showing?
- Click "Clear All" to reset filters
- Make sure you ran `add_inventory.py`

### Filters not working?
- Check browser console for JavaScript errors
- Try refreshing the page

### No dietary badges on products?
- Run `setup_sample_data.py` again
- This will create products with dietary indicators

## 📱 Works On

- ✅ Desktop browsers
- ✅ Mobile browsers
- ✅ Tablets
- ✅ Kiosk mode

## 🎓 For Developers

### Add New Filter
1. Add button in `templates/shop_items.html`:
```html
<button class="filter-btn" data-filter="organic" onclick="toggleFilter(this)">
    🌿 Organic
</button>
```

2. Add indicator to products in `setup_sample_data.py`:
```python
Product("Apples", dietary_indicators=["organic", "vegan"])
```

### Test Your Changes
```bash
python3 test_diet_filtering.py
```

## 📚 More Information

- Full documentation: `DIET_FILTERING_FEATURE.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Test results: Run `test_diet_filtering.py`

---

**Need Help?** Check the main README.md or DIET_FILTERING_FEATURE.md
