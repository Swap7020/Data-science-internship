from fastapi import FastAPI, Query

app = FastAPI()

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},

    # Added products
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1599, 'category': 'Electronics', 'in_stock': False},
]

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# Get all products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# Filter products
@app.get('/products/filter')
def filter_products(
    category: str = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):
    result = products

    if category:
        result = [p for p in result if p['category'] == category]

    if max_price:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return {'filtered_products': result, 'count': len(result)}


# cheapest and most expensive
@app.get('/products/deals')
def product_deals():
    cheapest = min(products, key=lambda x: x['price'])
    expensive = max(products, key=lambda x: x['price'])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

#  In-stock products
@app.get('/products/instock')
def get_instock_products():
    result = [p for p in products if p['in_stock']]

    return {
        "in_stock_products": result,
        "count": len(result)
    }

# Get product by ID
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

#  Category filter endpoint
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"category": category_name, "products": result, "count": len(result)}


#  Store summary
@app.get('/store/summary')
def store_summary():
    total = len(products)
    in_stock = len([p for p in products if p['in_stock']])
    out_stock = total - in_stock
    categories = list(set([p['category'] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "categories": categories
    }

#  Search products
@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()]

    if not result:
        return {"message": "No products matched your search"}

    return {
        "matched_products": result,
        "count": len(result)
    }
