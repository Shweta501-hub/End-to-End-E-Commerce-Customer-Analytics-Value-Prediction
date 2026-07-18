import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Database connection details
DB_HOST = "localhost"
DB_USER = "root"      # Change to your MySQL username
DB_PASSWORD = "Pallavi"  # Change to your MySQL password
DB_NAME = "ecommerce_ods"

# Path to the data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_csv_to_df(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

def connect_to_mysql():
    try:
        # Initial connection without database to create it if it doesn't exist
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            conn.database = DB_NAME
            print(f"Connected to MySQL database: {DB_NAME}")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("\n[TIP] Make sure your MySQL Server is running and username/password are correct.")
        return None

def create_tables(conn):
    cursor = conn.cursor()
    
    # 1. dim_promotions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_promotions (
        promotion_id INT PRIMARY KEY,
        promo_name VARCHAR(50) NOT NULL,
        discount_pct DECIMAL(5, 2) NOT NULL DEFAULT 0.00
    );
    """)

    # 2. dim_products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_products (
        product_id INT PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        cost DECIMAL(10, 2) NOT NULL
    );
    """)

    # 3. dim_customers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_customers (
        customer_id INT PRIMARY KEY,
        sign_up_date DATE NOT NULL,
        age INT NOT NULL,
        region VARCHAR(50) NOT NULL,
        acquisition_channel VARCHAR(50) NOT NULL,
        clv_predicted DECIMAL(10, 2) NULL,
        customer_segment VARCHAR(50) NULL
    );
    """)

    # 4. fact_orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_orders (
        order_id INT PRIMARY KEY,
        customer_id INT NOT NULL,
        order_date DATETIME NOT NULL,
        promotion_id INT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id) ON DELETE CASCADE,
        FOREIGN KEY (promotion_id) REFERENCES dim_promotions(promotion_id)
    );
    """)

    # 5. fact_order_items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_order_items (
        order_item_id INT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL DEFAULT 1,
        unit_price DECIMAL(10, 2) NOT NULL,
        discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        FOREIGN KEY (order_id) REFERENCES fact_orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
    );
    """)
    conn.commit()
    print("Database tables verified/created successfully.")

def insert_data(conn):
    cursor = conn.cursor()
    
    # Disable foreign key checks for clean loading
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # 1. Load Promotions
    df_promos = load_csv_to_df('promotions.csv')
    if df_promos is not None:
        cursor.execute("TRUNCATE TABLE dim_promotions;")
        for _, row in df_promos.iterrows():
            cursor.execute("INSERT INTO dim_promotions VALUES (%s, %s, %s)", 
                           (int(row['promotion_id']), row['promo_name'], float(row['discount_pct'])))
        print("Loaded dim_promotions table.")

    # 2. Load Products
    df_prod = load_csv_to_df('products.csv')
    if df_prod is not None:
        cursor.execute("TRUNCATE TABLE dim_products;")
        for _, row in df_prod.iterrows():
            cursor.execute("INSERT INTO dim_products VALUES (%s, %s, %s, %s, %s)", 
                           (int(row['product_id']), row['product_name'], row['category'], float(row['price']), float(row['cost'])))
        print("Loaded dim_products table.")

    # 3. Load Customers (combining with segmentation & CLV prediction outputs if available)
    df_cust = load_csv_to_df('customers.csv')
    df_seg = load_csv_to_df('customer_segments.csv')
    df_clv = load_csv_to_df('clv_predictions.csv')
    
    if df_cust is not None:
        # Merge segmentation and CLV predictions if files exist
        if df_seg is not None:
            df_cust = df_cust.merge(df_seg[['customer_id', 'Segment']], on='customer_id', how='left')
        else:
            df_cust['Segment'] = None
            
        if df_clv is not None:
            df_cust = df_cust.merge(df_clv[['customer_id', 'Predicted_Future_Spend']], on='customer_id', how='left')
            df_cust.rename(columns={'Predicted_Future_Spend': 'clv_predicted'}, inplace=True)
        else:
            df_cust['clv_predicted'] = None
            
        cursor.execute("TRUNCATE TABLE dim_customers;")
        for _, row in df_cust.iterrows():
            clv_val = float(row['clv_predicted']) if pd.notnull(row['clv_predicted']) else None
            seg_val = row['Segment'] if pd.notnull(row['Segment']) else None
            cursor.execute("INSERT INTO dim_customers VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (int(row['customer_id']), row['sign_up_date'], int(row['age']), row['region'], row['acquisition_channel'], clv_val, seg_val))
        print("Loaded dim_customers table.")

    # 4. Load Orders
    df_orders = load_csv_to_df('orders.csv')
    if df_orders is not None:
        cursor.execute("TRUNCATE TABLE fact_orders;")
        for _, row in df_orders.iterrows():
            cursor.execute("INSERT INTO fact_orders VALUES (%s, %s, %s, %s)", 
                           (int(row['order_id']), int(row['customer_id']), row['order_date'], int(row['promotion_id'])))
        print("Loaded fact_orders table.")

    # 5. Load Order Items
    df_items = load_csv_to_df('order_items.csv')
    if df_items is not None:
        cursor.execute("TRUNCATE TABLE fact_order_items;")
        for _, row in df_items.iterrows():
            cursor.execute("INSERT INTO fact_order_items VALUES (%s, %s, %s, %s, %s, %s)", 
                           (int(row['order_item_id']), int(row['order_id']), int(row['product_id']), int(row['quantity']), float(row['unit_price']), float(row['discount_amount'])))
        print("Loaded fact_order_items table.")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    print("--- All Data Successfully Loaded to MySQL ---")

def main():
    conn = connect_to_mysql()
    if conn:
        create_tables(conn)
        insert_data(conn)
        conn.close()

if __name__ == "__main__":
    main()
