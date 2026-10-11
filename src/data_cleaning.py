"""
Data Cleaning & Preprocessing Pipeline
Food Delivery Operations & Performance Analysis

Performs end-to-end data auditing, standardization, validation, and feature engineering.
Preserves raw data and exports cleaned data to CSV and SQLite database.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def run_data_cleaning():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, 'data', 'raw', 'food_delivery_raw.csv')
    cleaned_dir = os.path.join(base_dir, 'data', 'cleaned')
    os.makedirs(cleaned_dir, exist_ok=True)
    cleaned_csv_path = os.path.join(cleaned_dir, 'food_delivery_cleaned.csv')
    sqlite_db_path = os.path.join(cleaned_dir, 'food_delivery.db')

    print("=" * 70)
    print("STEP 1: LOADING & AUDITING RAW DATASET")
    print("=" * 70)
    df_raw = pd.read_csv(raw_path)
    initial_rows = len(df_raw)
    initial_cols = len(df_raw.columns)
    print(f"Raw dataset shape: {initial_rows} rows, {initial_cols} columns")

    # Audit duplicates
    dup_count = df_raw.duplicated(subset=['order_id']).sum()
    print(f"Identified duplicate order_ids: {dup_count}")

    # Audit missing values
    print("\nInitial Missing Values Count:")
    print(df_raw.isnull().sum())

    print("\n" + "=" * 70)
    print("STEP 2: EXECUTING CLEANING & STANDARDIZATION")
    print("=" * 70)
    df = df_raw.copy()

    # 1. Deduplicate by order_id
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    dedup_rows = len(df)
    print(f"Rows after removing duplicates: {dedup_rows} (Removed: {initial_rows - dedup_rows})")

    # 2. String Cleaning & Text Standardization
    str_cols = ['restaurant_name', 'cuisine_type', 'order_status', 'weather', 'traffic_level', 'cancellation_reason']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})

    # Standardize cuisine_type casing
    # Fix casings like ' indian ' or 'indian' -> 'Indian', 'bakery & desserts' -> 'Bakery & Desserts'
    df['cuisine_type'] = df['cuisine_type'].str.title()
    # Correct specific acronyms or multi-word capitalization if needed
    df['cuisine_type'] = df['cuisine_type'].replace({'Bakery & Desserts': 'Bakery & Desserts'})

    # Standardize order_status
    df['order_status'] = df['order_status'].str.title()
    status_mapping = {
        'Delivered': 'Delivered',
        'Cancelled By Customer': 'Cancelled by Customer',
        'Cancelled By Restaurant': 'Cancelled by Restaurant'
    }
    df['order_status'] = df['order_status'].replace(status_mapping)

    # 3. Datetime Parsing & Feature Engineering
    df['order_timestamp'] = pd.to_datetime(df['order_timestamp'])
    df['order_date'] = df['order_timestamp'].dt.strftime('%Y-%m-%d')
    df['order_time'] = df['order_timestamp'].dt.strftime('%H:%M:%S')
    df['order_hour'] = df['order_timestamp'].dt.hour
    df['day_of_week'] = df['order_timestamp'].dt.day_name()
    df['day_of_week_num'] = df['order_timestamp'].dt.weekday # 0=Monday, 6=Sunday
    df['is_weekend'] = df['day_of_week_num'].apply(lambda x: 1 if x >= 5 else 0)
    df['month_name'] = df['order_timestamp'].dt.month_name()
    df['month_num'] = df['order_timestamp'].dt.month
    df['year_month'] = df['order_timestamp'].dt.strftime('%Y-%m')

    # Assign Meal Period
    def get_meal_period(hour):
        if 6 <= hour < 11:
            return 'Breakfast'
        elif 11 <= hour < 15:
            return 'Lunch'
        elif 15 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 23:
            return 'Dinner'
        else:
            return 'Late Night'

    df['meal_period'] = df['order_hour'].apply(get_meal_period)

    # 4. Validating Numeric Fields & Handling Anomalies
    # Order Value Validation: Must be strictly > 0
    invalid_value_mask = df['order_value'] <= 0
    invalid_values_count = invalid_value_mask.sum()
    df = df[~invalid_value_mask]
    print(f"Removed negative or zero order values: {invalid_values_count}")

    # Delivery Time Validation:
    # Cancelled orders should have delivery_time_minutes as NaN
    df.loc[df['order_status'] != 'Delivered', 'delivery_time_minutes'] = np.nan

    # For Delivered orders, check impossible values (> 180 mins or <= 0)
    invalid_deliv_mask = (df['order_status'] == 'Delivered') & ((df['delivery_time_minutes'] > 180) | (df['delivery_time_minutes'] <= 0))
    invalid_deliv_count = invalid_deliv_mask.sum()
    df = df[~invalid_deliv_mask]
    print(f"Removed extreme delivery time sensor errors (>180 mins): {invalid_deliv_count}")

    # Rating Validation: Range 1.0 to 5.0
    # Retain legitimate NaNs (unrated orders) without artificial imputation to prevent bias
    invalid_rating_mask = (df['customer_rating'].notnull()) & ((df['customer_rating'] < 1.0) | (df['customer_rating'] > 5.0))
    df = df[~invalid_rating_mask]

    # Cancellation Reason Validation:
    # If order is Delivered, cancellation_reason must be NaN
    df.loc[df['order_status'] == 'Delivered', 'cancellation_reason'] = np.nan
    # If order is Cancelled but reason is missing, label as 'Reason Unspecified'
    cancelled_no_reason = (df['order_status'] != 'Delivered') & (df['cancellation_reason'].isnull())
    df.loc[cancelled_no_reason, 'cancellation_reason'] = 'Reason Unspecified'

    # 5. Delivery Performance Flags (SLA = 40 minutes)
    df['is_delayed'] = np.where(
        df['order_status'] == 'Delivered',
        (df['delivery_time_minutes'] > 40.0).astype(int),
        np.nan
    )
    df['delivery_time_bucket'] = pd.cut(
        df['delivery_time_minutes'],
        bins=[0, 30, 45, 60, 180],
        labels=['<=30 min (Fast)', '31-45 min (Standard)', '46-60 min (Delayed)', '>60 min (Severe Delay)']
    )

    final_rows = len(df)
    total_removed = initial_rows - final_rows

    print("\n" + "=" * 70)
    print("STEP 3: SAVING CLEANED DATASET & EXPORTING TO SQLITE")
    print("=" * 70)
    # Save Cleaned CSV
    df.to_csv(cleaned_csv_path, index=False)
    print(f"Saved cleaned CSV to: {cleaned_csv_path}")

    # Export to SQLite database
    conn = sqlite3.connect(sqlite_db_path)
    df.to_sql('orders', conn, if_exists='replace', index=False)
    
    # Create indexes for optimized SQL queries
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_id ON orders(order_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_status ON orders(order_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_hour ON orders(order_hour);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_day_of_week ON orders(day_of_week);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cuisine_type ON orders(cuisine_type);")
    conn.commit()
    conn.close()
    print(f"Successfully exported cleaned data to SQLite database: {sqlite_db_path}")

    print("\n" + "=" * 70)
    print("CLEANING AUDIT SUMMARY")
    print("=" * 70)
    print(f"Raw record count:        {initial_rows:,}")
    print(f"Deduplicated count:      {dedup_rows:,} (Removed {dup_count})")
    print(f"Removed value anomalies: {invalid_values_count}")
    print(f"Removed time anomalies:  {invalid_deliv_count}")
    print(f"Final clean record count:{final_rows:,}")
    print(f"Net records retained:    {(final_rows / initial_rows) * 100:.2f}%")
    print("=" * 70)

    return {
        'initial_rows': initial_rows,
        'final_rows': final_rows,
        'duplicates_removed': dup_count,
        'anomalies_removed': invalid_values_count + invalid_deliv_count,
        'cleaned_csv_path': cleaned_csv_path,
        'sqlite_db_path': sqlite_db_path
    }

if __name__ == '__main__':
    run_data_cleaning()

