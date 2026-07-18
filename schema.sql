-- Create Database
CREATE DATABASE IF NOT EXISTS ecommerce_ods;
USE ecommerce_ods;

-- 1. Table: dim_promotions
CREATE TABLE IF NOT EXISTS dim_promotions (
    promotion_id INT PRIMARY KEY,
    promo_name VARCHAR(50) NOT NULL,
    discount_pct DECIMAL(5, 2) NOT NULL DEFAULT 0.00
);

-- 2. Table: dim_products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    INDEX idx_category (category)
);

-- 3. Table: dim_customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id INT PRIMARY KEY,
    sign_up_date DATE NOT NULL,
    age INT NOT NULL,
    region VARCHAR(50) NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL,
    clv_predicted DECIMAL(10, 2) NULL, -- Filled later by Python ML model
    churn_risk_score DECIMAL(5, 4) NULL, -- Filled later by Python ML model
    customer_segment VARCHAR(50) NULL, -- Filled later by K-Means Clustering
    INDEX idx_region (region),
    INDEX idx_segment (customer_segment)
);

-- 4. Table: fact_orders
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    promotion_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (promotion_id) REFERENCES dim_promotions(promotion_id),
    INDEX idx_customer_order (customer_id),
    INDEX idx_order_date (order_date)
);

-- 5. Table: fact_order_items
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);
