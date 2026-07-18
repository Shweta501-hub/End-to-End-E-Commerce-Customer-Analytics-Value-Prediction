import os
import pandas as pd
import sqlite3

# Path to the data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'ecommerce.db')

def load_csv_to_df(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def main():
    print("--- Connecting to SQLite Database ---")
    # This automatically creates 'ecommerce.db' file in the data folder
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Load Promotions
    df_promos = load_csv_to_df('promotions.csv')
    if df_promos is not None:
        df_promos.to_sql('dim_promotions', conn, if_exists='replace', index=False)
        print("Loaded dim_promotions table.")

    # 2. Load Products
    df_prod = load_csv_to_df('products.csv')
    if df_prod is not None:
        df_prod.to_sql('dim_products', conn, if_exists='replace', index=False)
        print("Loaded dim_products table.")

    # 3. Load Customers (combining with segmentation and CLV predictions if available)
    df_cust = load_csv_to_df('customers.csv')
    df_seg = load_csv_to_df('customer_segments.csv')
    df_clv = load_csv_to_df('clv_predictions.csv')
    
    if df_cust is not None:
        if df_seg is not None:
            df_cust = df_cust.merge(df_seg[['customer_id', 'Segment']], on='customer_id', how='left')
        if df_clv is not None:
            df_cust = df_cust.merge(df_clv[['customer_id', 'Predicted_Future_Spend']], on='customer_id', how='left')
            df_cust.rename(columns={'Predicted_Future_Spend': 'clv_predicted'}, inplace=True)
            
        df_cust.to_sql('dim_customers', conn, if_exists='replace', index=False)
        print("Loaded dim_customers table.")

    # 4. Load Orders
    df_orders = load_csv_to_df('orders.csv')
    if df_orders is not None:
        df_orders.to_sql('fact_orders', conn, if_exists='replace', index=False)
        print("Loaded fact_orders table.")

    # 5. Load Order Items
    df_items = load_csv_to_df('order_items.csv')
    if df_items is not None:
        df_items.to_sql('fact_order_items', conn, if_exists='replace', index=False)
        print("Loaded fact_order_items table.")

    conn.commit()
    conn.close()
    print(f"\n--- SQLite Database Successfully Created at: {DB_PATH} ---")

if __name__ == "__main__":
    main()
