import os
import sqlite3
import pandas as pd

# Path to the SQLite database
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'ecommerce.db')

def run_query(title, query, conn):
    print(f"\n==========================================================================")
    print(f"RUNNING: {title}")
    print(f"==========================================================================")
    try:
        df = pd.read_sql_query(query, conn)
        # Configure pandas to show all columns nicely in terminal
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error running query: {e}")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at: {DB_PATH}")
        print("Please run load_to_sqlite.py first to create the database.")
        return

    conn = sqlite3.connect(DB_PATH)

    # QUERY 1: Month-over-Month (MoM) Net Sales Growth
    # (Note: SQLite uses strftime instead of DATE_FORMAT)
    query_1 = """
    WITH MonthlySales AS (
        SELECT 
            strftime('%Y-%m', o.order_date) AS sales_month,
            SUM((oi.quantity * oi.unit_price) - oi.discount_amount) AS net_sales
        FROM fact_orders o
        JOIN fact_order_items oi ON o.order_id = oi.order_id
        GROUP BY strftime('%Y-%m', o.order_date)
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
    """
    run_query("Month-over-Month (MoM) Net Sales Growth (CTEs & LAG Window Function)", query_1, conn)

    # QUERY 2: Top 3 Best-Selling Products per Category
    # (Note: SQLite supports DENSE_RANK() window functions)
    query_2 = """
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
    """
    run_query("Top 3 Best-Selling Products per Category (CTEs & DENSE_RANK Window Function)", query_2, conn)

    # QUERY 3: Customer Purchase Intervals (Time between purchases)
    query_3 = """
    WITH OrderIntervals AS (
        SELECT 
            customer_id,
            order_date,
            LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
        FROM fact_orders
    )
    SELECT 
        customer_id,
        ROUND(AVG(julianday(order_date) - julianday(prev_order_date)), 1) AS avg_days_between_orders,
        COUNT(order_date) AS total_orders
    FROM OrderIntervals
    WHERE prev_order_date IS NOT NULL
    GROUP BY customer_id
    ORDER BY total_orders DESC, avg_days_between_orders ASC
    LIMIT 10;
    """
    run_query("Average Days Between Customer Purchases (CTEs & LAG Window Function)", query_3, conn)

    # QUERY 4: Customer Segmentation Revenue Contribution
    query_4 = """
    SELECT 
        c.Segment AS customer_segment,
        COUNT(DISTINCT c.customer_id) AS total_customers,
        ROUND(SUM((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS total_revenue,
        ROUND(AVG((oi.quantity * oi.unit_price) - oi.discount_amount), 2) AS avg_order_item_value
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    GROUP BY c.Segment
    ORDER BY total_revenue DESC;
    """
    run_query("Revenue Contribution by Customer Segment (Clustering Join)", query_4, conn)

    conn.close()

if __name__ == "__main__":
    main()
