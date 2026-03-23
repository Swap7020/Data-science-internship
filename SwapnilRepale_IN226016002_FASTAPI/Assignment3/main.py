from fastapi import FastAPI, Query, HTTPException, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# -------------------- DATA --------------------
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
    {'id': 5, 'name': 'Laptop Stand', 'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Mechanical Keyboard', 'price': 2499, 'category': 'Electronics', 'in_stock': True},
    {'id': 7, 'name': 'Webcam', 'price': 1599, 'category': 'Electronics', 'in_stock': False},
]

feedback = []
orders = []
order_counter = 1

# -------------------- HELPER --------------------
def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)

# -------------------- MODELS --------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# -------------------- HOME --------------------
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# -------------------- GET ALL --------------------
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# -------------------- AUDIT --------------------
@app.get('/products/audit')
def product_audit():
    in_stock_list = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]

    stock_value = sum(p['price'] * 10 for p in in_stock_list)
    priciest = max(products, key=lambda p: p['price'])

    return {
        'total_products': len(products),
        'in_stock_count': len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value': stock_value,
        'most_expensive': {
            'name': priciest['name'],
            'price': priciest['price']
        }
    }

# -------------------- BULK DISCOUNT --------------------
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99),
):
    updated = []

    for p in products:
        if p['category'].lower() == category.lower():
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {'message': f'No products found in category: {category}'}

    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated),
        'updated_products': updated,
    }

# -------------------- SUMMARY --------------------
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
    }

# -------------------- FILTER --------------------
@app.get('/products/filter')
def filter_products(
    category: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None),
    in_stock: bool = Query(None)
):
    result = products

    if category:
        result = [p for p in result if p['category'] == category]

    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]

    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    return {'filtered_products': result, 'count': len(result)}

# -------------------- CATEGORY --------------------
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found"}
    return {"category": category_name, "products": result}

# -------------------- SEARCH --------------------
@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p['name'].lower()]
    return {"results": result}

# -------------------- ADD PRODUCT --------------------
@app.post("/products", status_code=201)
def add_product(product: NewProduct):
    if any(p["name"].lower() == product.name.lower() for p in products):
        raise HTTPException(status_code=400, detail="Product already exists")

    new_id = max(p["id"] for p in products) + 1

    new_product = product.dict()
    new_product["id"] = new_id

    products.append(new_product)
    return {"message": "Product added", "product": new_product}

# -------------------- UPDATE PRODUCT --------------------
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: Optional[int] = Query(None),
    in_stock: Optional[bool] = Query(None)
):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}

# -------------------- DELETE PRODUCT --------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted"}

# -------------------- PRICE --------------------
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    product = find_product(product_id)
    if product:
        return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

# -------------------- GET SINGLE (ALWAYS LAST) --------------------
@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if product:
        return {'product': product}
    return {'error': 'Product not found'}