"""
Shopping Service Simulator
Simulates e-commerce APIs for shopping offers and merchandise
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

app = Flask(__name__)

# Mock shopping data
CATEGORIES = {
    "electronics": {
        "name": "Electronics",
        "subcategories": ["smartphones", "laptops", "tablets", "accessories", "gaming"]
    },
    "fashion": {
        "name": "Fashion",
        "subcategories": ["clothing", "shoes", "accessories", "jewelry", "watches"]
    },
    "home": {
        "name": "Home & Garden",
        "subcategories": ["furniture", "decor", "kitchen", "outdoor", "tools"]
    },
    "sports": {
        "name": "Sports & Outdoors",
        "subcategories": ["fitness", "outdoor-gear", "team-sports", "water-sports", "cycling"]
    },
    "books": {
        "name": "Books & Media",
        "subcategories": ["fiction", "non-fiction", "textbooks", "ebooks", "audiobooks"]
    }
}

BRANDS = [
    {"name": "TechPro", "category": "electronics", "premium": True},
    {"name": "StyleMax", "category": "fashion", "premium": False},
    {"name": "HomeComfort", "category": "home", "premium": False},
    {"name": "SportElite", "category": "sports", "premium": True},
    {"name": "ReadWell", "category": "books", "premium": False},
    {"name": "LuxuryTech", "category": "electronics", "premium": True},
    {"name": "FastFashion", "category": "fashion", "premium": False},
    {"name": "PremiumHome", "category": "home", "premium": True},
    {"name": "ActiveLife", "category": "sports", "premium": False},
    {"name": "KnowledgeBase", "category": "books", "premium": True},
]

PRODUCT_TEMPLATES = {
    "electronics": [
        {"name": "Smartphone X1", "base_price": 699, "rating": 4.5},
        {"name": "Laptop Pro 15", "base_price": 1299, "rating": 4.3},
        {"name": "Tablet Air", "base_price": 399, "rating": 4.2},
        {"name": "Wireless Headphones", "base_price": 199, "rating": 4.4},
        {"name": "Gaming Console", "base_price": 499, "rating": 4.6},
        {"name": "Smart Watch", "base_price": 299, "rating": 4.1},
    ],
    "fashion": [
        {"name": "Designer Jeans", "base_price": 89, "rating": 4.0},
        {"name": "Leather Jacket", "base_price": 249, "rating": 4.3},
        {"name": "Running Shoes", "base_price": 129, "rating": 4.4},
        {"name": "Evening Dress", "base_price": 159, "rating": 4.2},
        {"name": "Casual Shirt", "base_price": 39, "rating": 3.9},
        {"name": "Winter Coat", "base_price": 199, "rating": 4.1},
    ],
    "home": [
        {"name": "Coffee Maker Deluxe", "base_price": 149, "rating": 4.3},
        {"name": "Dining Table Set", "base_price": 599, "rating": 4.0},
        {"name": "Garden Tool Kit", "base_price": 79, "rating": 4.2},
        {"name": "Throw Pillow Set", "base_price": 49, "rating": 3.8},
        {"name": "LED Floor Lamp", "base_price": 89, "rating": 4.1},
        {"name": "Kitchen Knife Set", "base_price": 99, "rating": 4.4},
    ],
    "sports": [
        {"name": "Yoga Mat Premium", "base_price": 59, "rating": 4.3},
        {"name": "Bicycle Mountain", "base_price": 899, "rating": 4.5},
        {"name": "Tennis Racket Pro", "base_price": 179, "rating": 4.2},
        {"name": "Fitness Tracker", "base_price": 149, "rating": 4.0},
        {"name": "Camping Tent", "base_price": 299, "rating": 4.4},
        {"name": "Basketball Shoes", "base_price": 119, "rating": 4.1},
    ],
    "books": [
        {"name": "Programming Guide 2024", "base_price": 49, "rating": 4.6},
        {"name": "Mystery Novel Collection", "base_price": 24, "rating": 4.2},
        {"name": "Cooking Masterclass", "base_price": 34, "rating": 4.4},
        {"name": "History of Technology", "base_price": 39, "rating": 4.1},
        {"name": "Self-Help Success", "base_price": 19, "rating": 3.9},
        {"name": "Art & Design Basics", "base_price": 44, "rating": 4.3},
    ]
}

def generate_product_price(base_price, is_premium=False, has_discount=False):
    """Generate realistic product pricing with variations"""
    # Brand premium
    brand_multiplier = 1.3 if is_premium else random.uniform(0.8, 1.2)
    
    # Market variation
    market_variation = random.uniform(0.9, 1.15)
    
    # Stock level pricing
    stock_multiplier = random.choice([1.0, 1.0, 1.0, 1.1, 0.95])  # Most products at regular price
    
    final_price = base_price * brand_multiplier * market_variation * stock_multiplier
    
    # Apply discounts
    if has_discount:
        discount_percent = random.uniform(0.1, 0.3)  # 10-30% discount
        final_price *= (1 - discount_percent)
    
    return round(final_price, 2)

def generate_shipping_options(price):
    """Generate shipping options based on order value"""
    options = [
        {
            "method": "standard",
            "name": "Standard Shipping",
            "cost": 9.99 if price < 50 else 0,
            "delivery_days": "5-7 business days",
            "free_threshold": 50
        },
        {
            "method": "express",
            "name": "Express Shipping",
            "cost": 19.99,
            "delivery_days": "2-3 business days",
            "free_threshold": None
        },
        {
            "method": "overnight",
            "name": "Overnight Shipping",
            "cost": 39.99,
            "delivery_days": "1 business day",
            "free_threshold": None
        }
    ]
    
    return options

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "shopping-simulator",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    return jsonify({
        "categories": CATEGORIES
    })

@app.route('/brands', methods=['GET'])
def get_brands():
    """Get all available brands"""
    category = request.args.get('category')
    
    brands = BRANDS
    if category:
        brands = [b for b in brands if b['category'] == category]
    
    return jsonify({
        "brands": brands,
        "count": len(brands)
    })

@app.route('/products/search', methods=['GET'])
def search_products():
    """Search products with various filters"""
    category = request.args.get('category', '').lower()
    query = request.args.get('q', '')
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', 10000))
    brand = request.args.get('brand', '')
    sort_by = request.args.get('sort', 'relevance')  # relevance, price_low, price_high, rating
    limit = int(request.args.get('limit', 20))
    
    products = []
    
    # Filter by category
    categories_to_search = [category] if category in PRODUCT_TEMPLATES else PRODUCT_TEMPLATES.keys()
    
    for cat in categories_to_search:
        for template in PRODUCT_TEMPLATES[cat]:
            # Generate multiple products per template with different brands
            relevant_brands = [b for b in BRANDS if b['category'] == cat]
            if brand:
                relevant_brands = [b for b in relevant_brands if b['name'].lower() == brand.lower()]
            
            for brand_info in relevant_brands[:2]:  # Limit brands per template
                # Skip if query doesn't match
                if query and query.lower() not in template['name'].lower() and query.lower() not in brand_info['name'].lower():
                    continue
                
                has_discount = random.random() < 0.3  # 30% chance of discount
                price = generate_product_price(template['base_price'], brand_info['premium'], has_discount)
                
                # Price filter
                if price < min_price or price > max_price:
                    continue
                
                product = {
                    "product_id": str(uuid.uuid4()),
                    "name": f"{brand_info['name']} {template['name']}",
                    "category": cat,
                    "subcategory": random.choice(CATEGORIES[cat]['subcategories']),
                    "brand": brand_info['name'],
                    "price": price,
                    "original_price": template['base_price'] if has_discount else price,
                    "discount_percent": round((1 - price/template['base_price']) * 100, 1) if has_discount else 0,
                    "rating": template['rating'] + random.uniform(-0.3, 0.3),
                    "review_count": random.randint(10, 1000),
                    "in_stock": random.choice([True, True, True, True, False]),  # 80% in stock
                    "stock_quantity": random.randint(0, 100) if random.random() > 0.1 else 0,
                    "shipping_options": generate_shipping_options(price),
                    "features": random.sample([
                        "Fast delivery", "Best seller", "Limited edition", "Eco-friendly",
                        "Premium quality", "Customer favorite", "New arrival", "Sale item"
                    ], random.randint(1, 3)),
                    "images": [f"https://example.com/images/{uuid.uuid4()}.jpg"],
                    "description": f"High-quality {template['name']} from {brand_info['name']}. Perfect for your {cat} needs."
                }
                
                # Round rating
                product['rating'] = round(max(1.0, min(5.0, product['rating'])), 1)
                
                products.append(product)
    
    # Sort products
    if sort_by == 'price_low':
        products.sort(key=lambda x: x['price'])
    elif sort_by == 'price_high':
        products.sort(key=lambda x: x['price'], reverse=True)
    elif sort_by == 'rating':
        products.sort(key=lambda x: x['rating'], reverse=True)
    else:  # relevance - mix of rating and randomness
        products.sort(key=lambda x: (x['rating'] * random.uniform(0.8, 1.2)), reverse=True)
    
    # Limit results
    products = products[:limit]
    
    return jsonify({
        "search_criteria": {
            "category": category,
            "query": query,
            "min_price": min_price,
            "max_price": max_price,
            "brand": brand,
            "sort_by": sort_by
        },
        "products": products,
        "total_count": len(products),
        "has_more": len(products) == limit
    })

@app.route('/products/<product_id>', methods=['GET'])
def get_product_details(product_id):
    """Get detailed product information"""
    # Simulate product lookup
    category = random.choice(list(PRODUCT_TEMPLATES.keys()))
    template = random.choice(PRODUCT_TEMPLATES[category])
    brand = random.choice([b for b in BRANDS if b['category'] == category])
    
    price = generate_product_price(template['base_price'], brand['premium'])
    
    return jsonify({
        "product_id": product_id,
        "name": f"{brand['name']} {template['name']}",
        "category": category,
        "brand": brand['name'],
        "price": price,
        "rating": template['rating'],
        "review_count": random.randint(50, 2000),
        "in_stock": True,
        "stock_quantity": random.randint(5, 50),
        "shipping_options": generate_shipping_options(price),
        "specifications": {
            "weight": f"{random.uniform(0.1, 10.0):.1f} lbs",
            "dimensions": f"{random.randint(5, 20)}x{random.randint(5, 20)}x{random.randint(1, 10)} inches",
            "warranty": f"{random.choice([1, 2, 3, 5])} years",
            "material": random.choice(["Plastic", "Metal", "Wood", "Fabric", "Glass", "Composite"])
        },
        "images": [f"https://example.com/images/{uuid.uuid4()}.jpg" for _ in range(random.randint(2, 6))],
        "description": f"Premium {template['name']} from {brand['name']}. Excellent quality and performance.",
        "related_products": [str(uuid.uuid4()) for _ in range(4)]
    })

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add product to shopping cart"""
    data = request.get_json()
    
    required_fields = ['product_id', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    cart_item_id = str(uuid.uuid4())
    
    return jsonify({
        "cart_item_id": cart_item_id,
        "product_id": data['product_id'],
        "quantity": data['quantity'],
        "added_at": datetime.utcnow().isoformat(),
        "status": "added"
    })

@app.route('/order/create', methods=['POST'])
def create_order():
    """Create a shopping order"""
    data = request.get_json()
    
    required_fields = ['items', 'shipping_address', 'payment_method']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    order_id = f"ORD{random.randint(100000, 999999)}"
    
    # Calculate totals
    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in data['items'])
    shipping_cost = data.get('shipping_cost', 9.99)
    tax = subtotal * 0.08  # 8% tax
    total = subtotal + shipping_cost + tax
    
    return jsonify({
        "order_id": order_id,
        "status": "confirmed",
        "order_details": {
            "items": data['items'],
            "subtotal": round(subtotal, 2),
            "shipping_cost": shipping_cost,
            "tax": round(tax, 2),
            "total": round(total, 2),
            "currency": "USD"
        },
        "shipping_address": data['shipping_address'],
        "estimated_delivery": (datetime.now() + timedelta(days=random.randint(3, 10))).date().isoformat(),
        "tracking_number": f"TRK{random.randint(1000000000, 9999999999)}",
        "order_date": datetime.utcnow().isoformat()
    })

@app.route('/order/<order_id>', methods=['GET'])
def get_order_status(order_id):
    """Get order status and details"""
    statuses = ["confirmed", "processing", "shipped", "delivered", "cancelled"]
    
    return jsonify({
        "order_id": order_id,
        "status": random.choice(statuses),
        "order_date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
        "total_amount": random.randint(50, 500),
        "items_count": random.randint(1, 5),
        "tracking_number": f"TRK{random.randint(1000000000, 9999999999)}",
        "estimated_delivery": (datetime.now() + timedelta(days=random.randint(1, 10))).date().isoformat()
    })

@app.route('/cancel/<order_id>', methods=['POST'])
def cancel_order(order_id):
    """Cancel a shopping order"""
    try:
        # Simulate order cancellation processing
        success_rate = 0.8  # 80% success rate for simulation
        
        if random.random() < success_rate:
            # Order status affects cancellation
            order_statuses = ["confirmed", "processing", "shipped"]
            current_status = random.choice(order_statuses)
            
            original_amount = random.randint(50, 800)
            
            if current_status == "confirmed":
                cancellation_fee = 0  # Free cancellation
                refund_amount = original_amount
            elif current_status == "processing":
                cancellation_fee = random.randint(5, 25)  # Small processing fee
                refund_amount = original_amount - cancellation_fee
            else:  # shipped
                cancellation_fee = random.randint(15, 50)  # Return shipping fee
                refund_amount = original_amount - cancellation_fee
            
            return jsonify({
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
                "original_status": current_status,
                "original_amount": original_amount,
                "cancellation_fee": cancellation_fee,
                "refund_amount": refund_amount,
                "processing_time": "1-3 business days",
                "message": f"Order cancelled successfully. Was in {current_status} status."
            }), 200
        else:
            return jsonify({
                "success": False,
                "order_id": order_id,
                "error": "Cannot cancel - order already delivered or out for delivery",
                "message": "Please initiate a return instead"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Cancellation processing failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5004, host='0.0.0.0')