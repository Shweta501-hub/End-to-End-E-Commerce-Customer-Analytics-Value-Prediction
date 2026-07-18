import pandas as pd
import os

# Define path to the data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 1. Load the CSV files
print("--- Loading Datasets ---")
customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))
promotions = pd.read_csv(os.path.join(DATA_DIR, 'promotions.csv'))

# 2. Display basic info for each dataset
print(f"Customers shape: {customers.shape} (Rows, Columns)")
print(f"Products shape: {products.shape}")
print(f"Orders shape: {orders.shape}")
print(f"Order Items shape: {order_items.shape}")
print(f"Promotions shape: {promotions.shape}\n")

# 3. Print the first few rows of Customers as an example
print("--- Customer Data Preview ---")
print(customers.head(), "\n")

# 4. Perform a simple analysis: Total Revenue
# Merge order items with product details to get prices
print("--- Calculating Basic Metrics ---")
merged_items = order_items.merge(products, on='product_id', how='left')

# Calculate total sales before discount
merged_items['gross_sales'] = merged_items['quantity'] * merged_items['price']
# Calculate net sales after subtracting discount
merged_items['net_sales'] = merged_items['gross_sales'] - merged_items['discount_amount']

total_net_revenue = merged_items['net_sales'].sum()
print(f"Total Net Revenue Generated: ${total_net_revenue:,.2f}")

# Calculate average items per order
avg_items_per_order = order_items.groupby('order_id')['quantity'].sum().mean()
print(f"Average items per order: {avg_items_per_order:.2f}")
