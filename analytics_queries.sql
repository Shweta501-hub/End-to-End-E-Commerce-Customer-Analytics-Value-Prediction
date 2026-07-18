-- Active: ecommerce_ods database
USE ecommerce_ods;

-- =========================================================================
-- QUERY 1: Month-over-Month (MoM) Net Sales Growth
-- Demonstrates: Window Functions (LAG), CTEs, Math functions
-- =========================================================================
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(o.order_date, '%Y-%m') AS sales_month,
        SUM((oi.quantity * oi.unit_price) - oi.discount_amount) AS net_sales
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
)
SELECT 
    sales_month,
    ROUND(net_sales, 2) AS current_month_sales,
    ROUND(LAG(net_sales, 1) OVER (ORDER BY sales_month), 2) AS previous_month_sales,
    ROUND(
        ((net_sales - LAG(net_sales, 1) OVER (ORDER BY sales_month)) / LAG(net_sales, 1) OVER (ORDER BY sales_month)) * 100, 
        2
    ) AS mom_growth_pct
FROM MonthlySales;


-- =========================================================================
-- QUERY 2: Top 3 Best-Selling Products per Category
-- Demonstrates: DENSE_RANK() OVER (PARTITION BY ...), CTEs, Joins
-- =========================================================================
WITH ProductRankings AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(oi.quantity) AS total_units_sold,
        SUM((oi.quantity * oi.unit_price) - oi.discount_amount) AS total_revenue,
        DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity) DESC) as sales_rank
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    total_units_sold,
    ROUND(total_revenue, 2) AS total_revenue,
    sales_rank
FROM ProductRankings
WHERE sales_rank <= 3;


-- =========================================================================
-- QUERY 3: Customer Purchase Intervals (Time between purchases)
-- Demonstrates: LAG() OVER (PARTITION BY ...), datetime calculations
-- =========================================================================
WITH OrderIntervals AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
    FROM fact_orders
)
SELECT 
    customer_id,
    AVG(DATEDIFF(order_date, prev_order_date)) AS avg_days_between_orders,
    COUNT(order_date) AS total_orders
FROM OrderIntervals
WHERE prev_order_date IS NOT NULL
GROUP BY customer_id
ORDER BY total_orders DESC, avg_days_between_orders ASC
LIMIT 10;


-- =========================================================================
-- QUERY 4: Customer Segmentation Revenue Contribution
-- Demonstrates: CTEs, GROUP BY, subqueries
-- =========================================================================
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    ROUND(SUM((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS total_revenue,
    ROUND(AVG((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS avg_order_item_value
FROM dim_customers c
JOIN fact_orders o ON c.customer_id = o.customer_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;
