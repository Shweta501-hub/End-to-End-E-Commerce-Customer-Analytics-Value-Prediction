import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 1. Load the data
print("--- Loading Data ---")
customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))
products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))

# Convert order_date to datetime
orders['order_date'] = pd.to_datetime(orders['order_date'])

# 2. Calculate RFM Metrics (Recency, Frequency, Monetary)
print("--- Calculating RFM Metrics ---")

# Step 2a: Calculate Monetary (total spend per order item, then sum per customer)
order_items['item_spend'] = (order_items['quantity'] * order_items['unit_price']) - order_items['discount_amount']
order_spend = order_items.groupby('order_id')['item_spend'].sum().reset_index()

orders_with_spend = orders.merge(order_spend, on='order_id', how='left').fillna(0)
customer_spend = orders_with_spend.groupby('customer_id')['item_spend'].sum().reset_index()
customer_spend.rename(columns={'item_spend': 'Monetary'}, inplace=True)

# Step 2b: Calculate Frequency (total unique orders per customer)
customer_freq = orders.groupby('customer_id')['order_id'].nunique().reset_index()
customer_freq.rename(columns={'order_id': 'Frequency'}, inplace=True)

# Step 2c: Calculate Recency (days since last order from a reference date)
# We will use the day after the last order in the dataset as our reference point
ref_date = orders['order_date'].max() + pd.Timedelta(days=1)
orders['days_since_order'] = (ref_date - orders['order_date']).dt.days
customer_recency = orders.groupby('customer_id')['days_since_order'].min().reset_index()
customer_recency.rename(columns={'days_since_order': 'Recency'}, inplace=True)

# Merge RFM data together
rfm = customer_recency.merge(customer_freq, on='customer_id')
rfm = rfm.merge(customer_spend, on='customer_id')

# Join with general customer details (Age, Region, Channel)
rfm_full = rfm.merge(customers, on='customer_id')

# 3. K-Means Clustering
print("--- Running K-Means Clustering ---")

# Normalize RFM features (important because scale of Monetary is much larger than Frequency)
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])

# Set up K-Means with 4 clusters
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
rfm_full['Cluster'] = kmeans.fit_predict(rfm_scaled)

# 4. Map Clusters to business-friendly segment names
# Calculate average values of R, F, M for each cluster to identify which is which
cluster_stats = rfm_full.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().reset_index()
print("\nAverage RFM Metrics per Cluster:")
print(cluster_stats)

# We will label clusters logically based on their characteristics
sorted_clusters = cluster_stats.sort_values(by='Monetary', ascending=False)['Cluster'].tolist()

cluster_labels = {
    sorted_clusters[0]: 'Champions / VIPs',
    sorted_clusters[1]: 'Loyal / Regular',
    sorted_clusters[2]: 'Active - Low Spend',
    sorted_clusters[3]: 'At Risk / Churned'
}

rfm_full['Segment'] = rfm_full['Cluster'].map(cluster_labels)

print("\n--- Final Customer Segments Distribution ---")
print(rfm_full['Segment'].value_counts())

# Save results to a CSV file for Power BI or further analysis
output_file = os.path.join(DATA_DIR, 'customer_segments.csv')
rfm_full.to_csv(output_file, index=False)
print(f"\nSaved customer segments to: {output_file}")
