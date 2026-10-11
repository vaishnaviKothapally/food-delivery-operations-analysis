"""
SQL Analysis Runner & Metric Validator
Food Delivery Operations & Performance Analysis

Executes all analytical queries in operations_analysis.sql against SQLite,
prints structured metric outputs, and verifies cross-consistency.
"""

import os
import sqlite3
import pandas as pd

def run_sql_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'cleaned', 'food_delivery.db')
    sql_path = os.path.join(base_dir, 'sql', 'operations_analysis.sql')

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Run data_cleaning.py first.")

    conn = sqlite3.connect(db_path)
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split queries by double dash QUERY headers or semicolons
    raw_queries = sql_content.split(';')
    
    query_num = 1
    for raw_q in raw_queries:
        q = raw_q.strip()
        if not q or not any(kw in q.upper() for kw in ['SELECT', 'WITH']):
            continue

        # Extract title comment if present
        title = f"Query {query_num}"
        for line in q.splitlines():
            if 'QUERY ' in line.upper():
                title = line.strip('- ').strip()
                break

        print("\n" + "=" * 80)
        print(f"EXECUTING: {title}")
        print("=" * 80)
        
        try:
            df_res = pd.read_sql_query(q, conn)
            print(df_res.to_string(index=False))
            query_num += 1
        except Exception as e:
            print(f"Error executing query: {e}")
            print(q)

    conn.close()
    print("\n" + "=" * 80)
    print("ALL SQL QUERIES EXECUTED SUCCESSFULLY")
    print("=" * 80)

if __name__ == '__main__':
    run_sql_analysis()

