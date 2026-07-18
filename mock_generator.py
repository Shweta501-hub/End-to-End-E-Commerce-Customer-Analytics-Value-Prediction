import csv
import random
from datetime import datetime, timedelta

# Constants for generating reproducible mock data
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 50
NUM_ORDERS = 5000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 7, 1)

# 1. Generate Promotions
promotions = [
    {"promotion_id": 1, "promo_name": "No Promo", "discount_pct": 0.00},
    {"promotion_id": 2, "promo_name": "WELCOME10", "discount_pct": 0.10},
    {"promotion_id": 3, "promo_name": "SUMMER20", "discount_pct": 0.20},
    {"promotion_id": 4, "promo_name": "FLASH30", "discount_pct": 0.30},
    {"promotion_id": 5, "promo_name": "VIP15", "discount_pct": 0.15},
]

# 2. Generate Products
categories = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Beauty"]
product_names = {
    "Electronics": ["Smartphone", "Laptop", "Wireless Earbuds", "Smartwatch", "Bluetooth Speaker", "Tablet", "Charger", "HDMI Cable", "Power Bank", "Monitor"],
    "Apparel": ["T-Shirt", "Jeans", "Hoodie", "Jacket", "Sneakers", "Socks", "Cap", "Dress", "Skirt", "Belt"],
    "Home & Kitchen": ["Blender", "Coffee Maker", "Air Fryer", "Toaster", "Cookware Set", "Knife Set", "Dinnerware", "Vacuum Cleaner", "Desk Lamp", "Storage Bins"],
    "Books": ["Fiction Novel", "Sci-Fi Trilogy", "Biography", "History Book", "Self-Help Guide", "Cookbook", "Mystery Thriller", "Poetry Collection", "Business Strategy", "Children's Book"],
    "Beauty": ["Moisturizer", "Sunscreen", "Face Wash", "Shampoo", "Conditioner", "Lip Balm", "Perfume", "Mascara", "Foundation", "Eye Palette"]
}

products = []
product_id = 1
for category in categories:
    names = product_names[category]
    for name in names:
        price = round(random.uniform(5.0, 800.0), 2)
        cost = round(price * random.uniform(0.4, 0.6), 2)
        products.append({
            "product_id": product_id,
            "product_name": name,
            "category": category,
            "price": price,
            "cost": cost
        })
        product_id += 1

# 3. Generate Customers
channels = ["Google Search", "Facebook Ad", "Instagram Ad", "Direct Link", "Referral", "Email Campaign"]
regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    max_days = (END_DATE - START_DATE).days - 90
    signup_days = random.randint(0, max_days)
    signup_date = START_DATE + timedelta(days=signup_days)
    
    customers.append({
        "customer_id": i,
        "sign_up_date": signup_date.strftime("%Y-%m-%d"),
        "age": random.randint(18, 75),
        "region": random.choice(regions),
        "acquisition_channel": random.choice(channels)
    })

# 4. Generate Orders & Order Items
orders = []
order_items = []
order_item_id = 1

for i in range(1, NUM_ORDERS + 1):
    customer = random.choice(customers)
    signup_dt = datetime.strptime(customer["sign_up_date"], "%Y-%m-%d")
    max_days = (END_DATE - signup_dt).days
    order_days = random.randint(0, max_days)
    order_date = signup_dt + timedelta(days=order_days)
    
    promo = random.choice(promotions)
    
    orders.append({
        "order_id": i,
        "customer_id": customer["customer_id"],
        "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "promotion_id": promo["promotion_id"]
    })
    
    num_items = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.15, 0.07, 0.03])[0]
    chosen_products = random.sample(products, num_items)
    
    for prod in chosen_products:
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.8, 0.12, 0.05, 0.02, 0.01])[0]
        base_price = prod["price"]
        discount_amount = round(base_price * quantity * promo["discount_pct"], 2)
        
        order_items.append({
            "order_item_id": order_item_id,
            "order_id": i,
            "product_id": prod["product_id"],
            "quantity": quantity,
            "unit_price": base_price,
            "discount_amount": discount_amount
        })
        order_item_id += 1

# Write CSV files
def write_csv(filename, fieldnames, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filename} with {len(data)} rows.")

write_csv("customers.csv", ["customer_id", "sign_up_date", "age", "region", "acquisition_channel"], customers)
write_csv("products.csv", ["product_id", "product_name", "category", "price", "cost"], products)
write_csv("promotions.csv", ["promotion_id", "promo_name", "discount_pct"], promotions)
write_csv("orders.csv", ["order_id", "customer_id", "order_date", "promotion_id"], orders)
write_csv("order_items.csv", ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"], order_items)
