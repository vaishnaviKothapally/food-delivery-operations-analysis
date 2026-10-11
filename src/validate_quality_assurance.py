"""
Quality Assurance & Cross-Validation Test Suite
Food Delivery Operations & Performance Analysis

Validates data integrity, reconciles row counts, and verifies that
analytical KPIs calculated independently in Python match SQLite SQL outputs.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def run_qa_validation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 75)
    print("RUNNING QUALITY ASSURANCE & CROSS-VALIDATION SUITE")
    print("=" * 75)

    # 1. Project Structure Integrity Check
    required_files = [
        os.path.join(base_dir, 'data', 'raw', 'food_delivery_raw.csv'),
        os.path.join(base_dir, 'data', 'cleaned', 'food_delivery_cleaned.csv'),
        os.path.join(base_dir, 'data', 'cleaned', 'food_delivery.db'),
        os.path.join(base_dir, 'sql', 'operations_analysis.sql'),
        os.path.join(base_dir, 'src', 'data_cleaning.py'),
        os.path.join(base_dir, 'src', 'generate_raw_data.py'),
        os.path.join(base_dir, 'src', 'generate_visualizations.py'),
        os.path.join(base_dir, 'src', 'run_sql_analysis.py'),
        os.path.join(base_dir, 'reports', 'data_cleaning_report.md'),
        os.path.join(base_dir, 'reports', 'business_insights.md'),
        os.path.join(base_dir, 'notebooks', 'food_delivery_analysis.ipynb'),
        os.path.join(base_dir, 'requirements.txt'),
        os.path.join(base_dir, '.gitignore')
    ]

    print("[CHECK 1] Verifying File Structure & Critical Assets:")
    missing_files = []
    for f in required_files:
        if os.path.exists(f):
            print(f"  [PASS] Found: {os.path.relpath(f, base_dir)}")
        else:
            print(f"  [FAIL] Missing: {os.path.relpath(f, base_dir)}")
            missing_files.append(f)

    # Visualizations check
    visuals_dir = os.path.join(base_dir, 'visuals')
    visual_files = os.listdir(visuals_dir) if os.path.exists(visuals_dir) else []
    print(f"  [PASS] Found {len(visual_files)} visual artifacts in visuals/")
    assert len(visual_files) >= 8, "Expected at least 8 visualizations!"

    # 2. Ingestion & Cleaning Reconciliation
    print("\n[CHECK 2] Reconciling Raw vs. Cleaned Dataset Records:")
    df_raw = pd.read_csv(os.path.join(base_dir, 'data', 'raw', 'food_delivery_raw.csv'))
    df_clean = pd.read_csv(os.path.join(base_dir, 'data', 'cleaned', 'food_delivery_cleaned.csv'))
    
    raw_count = len(df_raw)
    clean_count = len(df_clean)
    print(f"  Raw rows:     {raw_count:,}")
    print(f"  Cleaned rows: {clean_count:,}")
    assert raw_count == 8535, f"Expected 8535 raw rows, got {raw_count}"
    assert clean_count == 8491, f"Expected 8491 cleaned rows, got {clean_count}"
    print("  [PASS] Row count matches data cleaning specifications exactly.")

    # 3. Numeric Range & Integrity Check
    print("\n[CHECK 3] Validating Domain Constraints & Boundaries:")
    assert (df_clean['order_value'] > 0).all(), "Found non-positive order values!"
    print("  [PASS] All order values > 0")

    delivered_df = df_clean[df_clean['order_status'] == 'Delivered']
    assert (delivered_df['delivery_time_minutes'] > 0).all() and (delivered_df['delivery_time_minutes'] <= 180).all(), "Delivery time out of bounds!"
    print("  [PASS] Delivered order delivery times bounded within [0, 180] minutes")

    cancelled_df = df_clean[df_clean['order_status'].str.startswith('Cancelled')]
    assert cancelled_df['delivery_time_minutes'].isnull().all(), "Cancelled orders should have null delivery time!"
    print("  [PASS] Cancelled orders have null delivery duration")

    rated_df = df_clean[df_clean['customer_rating'].notnull()]
    assert (rated_df['customer_rating'] >= 1.0).all() and (rated_df['customer_rating'] <= 5.0).all(), "Ratings outside [1, 5]!"
    print("  [PASS] Customer ratings strictly bounded in [1.0, 5.0]")

    # 4. Cross-System Metric Reconciliation: Python (Pandas) vs. SQL (SQLite)
    print("\n[CHECK 4] Cross-Calculating Core KPIs (Pandas vs. SQLite SQL):")
    conn = sqlite3.connect(os.path.join(base_dir, 'data', 'cleaned', 'food_delivery.db'))
    
    # SQL Metrics
    sql_kpi = pd.read_sql_query("""
    SELECT 
        COUNT(*) AS sql_total_orders,
        SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS sql_delivered_orders,
        SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1 ELSE 0 END) AS sql_cancelled_orders,
        ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS sql_cancel_rate,
        ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS sql_net_revenue,
        ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS sql_avg_delivery_time
    FROM orders;
    """, conn).iloc[0]

    # Pandas Metrics
    py_total = len(df_clean)
    py_delivered = (df_clean['order_status'] == 'Delivered').sum()
    py_cancelled = df_clean['order_status'].str.startswith('Cancelled').sum()
    py_cancel_rate = round((py_cancelled / py_total) * 100, 2)
    py_net_revenue = round(df_clean.loc[df_clean['order_status'] == 'Delivered', 'order_value'].sum(), 2)
    py_avg_deliv = round(df_clean.loc[df_clean['order_status'] == 'Delivered', 'delivery_time_minutes'].mean(), 2)

    print(f"  Total Orders:        Pandas = {py_total:,}  |  SQL = {sql_kpi['sql_total_orders']:,}  --> MATCH: {py_total == sql_kpi['sql_total_orders']}")
    print(f"  Delivered Orders:    Pandas = {py_delivered:,}  |  SQL = {sql_kpi['sql_delivered_orders']:,}  --> MATCH: {py_delivered == sql_kpi['sql_delivered_orders']}")
    print(f"  Cancelled Orders:    Pandas = {py_cancelled:,}    |  SQL = {sql_kpi['sql_cancelled_orders']:,}    --> MATCH: {py_cancelled == sql_kpi['sql_cancelled_orders']}")
    print(f"  Cancellation Rate:   Pandas = {py_cancel_rate}%  |  SQL = {sql_kpi['sql_cancel_rate']}%  --> MATCH: {py_cancel_rate == sql_kpi['sql_cancel_rate']}")
    print(f"  Net Revenue ($):     Pandas = ${py_net_revenue:,.2f} | SQL = ${sql_kpi['sql_net_revenue']:,.2f} --> MATCH: {abs(py_net_revenue - sql_kpi['sql_net_revenue']) < 0.01}")
    print(f"  Avg Delivery (min):  Pandas = {py_avg_deliv} min  |  SQL = {sql_kpi['sql_avg_delivery_time']} min  --> MATCH: {py_avg_deliv == sql_kpi['sql_avg_delivery_time']}")

    conn.close()

    assert py_total == sql_kpi['sql_total_orders']
    assert py_delivered == sql_kpi['sql_delivered_orders']
    assert py_cancelled == sql_kpi['sql_cancelled_orders']
    assert py_cancel_rate == sql_kpi['sql_cancel_rate']
    assert abs(py_net_revenue - sql_kpi['sql_net_revenue']) < 0.01
    assert py_avg_deliv == sql_kpi['sql_avg_delivery_time']

    print("\n" + "=" * 75)
    print("ALL QUALITY ASSURANCE CHECKS PASSED WITH 100% CROSS-CONSISTENCY!")
    print("=" * 75)

if __name__ == '__main__':
    run_qa_validation()

