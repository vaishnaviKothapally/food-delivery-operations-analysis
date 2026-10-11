"""
Food Delivery Operations Dataset Generator
Generates a realistic, synthetic food delivery operational dataset
modeled after production delivery platforms (Zomato/Swiggy/DoorDash).

Includes deliberate real-world data imperfections to showcase data cleaning:
- Inconsistent casing and whitespace
- Duplicate entries
- Realistic missing values (unrated orders, cancellation reasons)
- Outliers and boundary cases
- Explicitly labeled as synthetic data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def generate_synthetic_data(num_records=8500, random_seed=42):
    np.random.seed(random_seed)
    random.seed(random_seed)

    print(f"Generating {num_records} synthetic food delivery order records...")

    # Define restaurant and cuisine entities
    restaurants_by_cuisine = {
        'Indian': ['Biryani Blues', 'Punjab Grill', 'Spice Hub', 'Curry Kingdom', 'Tandoor Express'],
        'Italian': ['Pasta Fresca', 'Luigi Pizzeria', 'Olive & Basil', 'Trattoria Bella'],
        'American': ['Burger Barn', 'Smash Patty Co', 'Crispy Wings', 'Route 66 Diner'],
        'Chinese': ['Dragon Wok', 'Golden Chopsticks', 'Dim Sum House', 'Peking Feast'],
        'Mexican': ['Taco Fiesta', 'El Burrito Loco', 'Salsa & Guac', 'Cantina Mexicana'],
        'Japanese': ['Sushi Zen', 'Tokyo Ramen Bar', 'Oishii Bento'],
        'Bakery & Desserts': ['Sweet Treats', 'Crumbs & Crust', 'Frosting Co', 'The Daily Bake']
    }

    cuisines = list(restaurants_by_cuisine.keys())
    cuisine_weights = [0.28, 0.16, 0.18, 0.14, 0.10, 0.08, 0.06]

    # Pre-generate flat list of restaurants with their cuisine
    restaurant_list = []
    for c, r_list in restaurants_by_cuisine.items():
        for r in r_list:
            restaurant_list.append((r, c))

    # Time frame: 6 months (2024-01-01 to 2024-06-30)
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    total_days = 182

    # Hour probability distribution:
    # Off-peak (0-10): low
    # Lunch peak (12-14): high
    # Afternoon dip (15-17): moderate
    # Dinner peak (19-22): highest
    # Late night (23): low
    hour_weights = [
        0.005, 0.003, 0.002, 0.001, 0.001, 0.002, 0.006, 0.015, # 00:00 - 07:00
        0.025, 0.035, 0.045, 0.070,                             # 08:00 - 11:00
        0.095, 0.110, 0.075, 0.040,                             # 12:00 - 15:00 (Lunch peak)
        0.035, 0.040, 0.060, 0.115,                             # 16:00 - 19:00
        0.130, 0.095, 0.055, 0.020                              # 20:00 - 23:00 (Dinner peak)
    ]
    hour_weights = np.array(hour_weights) / sum(hour_weights)

    data = []
    order_id_counter = 10001
    customer_pool = [f"CUST_{i:04d}" for i in range(1, 1201)]
    rider_pool = [f"RIDER_{i:03d}" for i in range(1, 251)]

    for _ in range(num_records):
        order_id = f"ORD_{order_id_counter}"
        order_id_counter += 1

        customer_id = random.choice(customer_pool)

        # Select cuisine & restaurant
        chosen_cuisine = np.random.choice(cuisines, p=cuisine_weights)
        restaurant_name = random.choice(restaurants_by_cuisine[chosen_cuisine])
        restaurant_id = f"REST_{abs(hash(restaurant_name)) % 1000:03d}"

        # Select timestamp
        day_offset = random.randint(0, total_days - 1)
        hour = np.random.choice(range(24), p=hour_weights)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        order_time = start_date + timedelta(days=day_offset, hours=int(hour), minutes=minute, seconds=second)

        # Weekend indicator
        is_weekend = order_time.weekday() >= 5
        # Weekend boost to delivery distance / value
        dist_mean = 5.2 if not is_weekend else 6.0
        distance_km = round(max(0.8, np.random.normal(dist_mean, 2.2)), 2)

        # Order value based on cuisine
        base_val_map = {
            'Indian': 28.5, 'Italian': 32.0, 'American': 22.0,
            'Chinese': 26.0, 'Mexican': 24.0, 'Japanese': 42.0,
            'Bakery & Desserts': 16.5
        }
        order_val_mean = base_val_map[chosen_cuisine] * (1.15 if is_weekend else 1.0)
        order_value = round(max(5.0, np.random.normal(order_val_mean, 8.5)), 2)

        # Weather and traffic conditions
        # Weather: 70% Clear, 20% Rainy, 10% Foggy
        weather = np.random.choice(['Clear', 'Rainy', 'Foggy'], p=[0.72, 0.20, 0.08])

        # Traffic depends on hour and weather
        is_rush_hour = hour in [12, 13, 19, 20, 21]
        if is_rush_hour or weather == 'Rainy':
            traffic = np.random.choice(['Medium', 'High', 'Severe'], p=[0.35, 0.50, 0.15])
        else:
            traffic = np.random.choice(['Low', 'Medium', 'High'], p=[0.60, 0.30, 0.10])

        # Operational metrics: Preparation time (Kitchen)
        base_prep = 16.0
        if is_rush_hour:
            base_prep += 7.0
        if chosen_cuisine in ['Italian', 'Japanese']:
            base_prep += 4.0
        prep_time = round(max(8.0, np.random.normal(base_prep, 4.5)), 1)

        # Operational metrics: Rider transit time
        transit_speed_kmh = 24.0 # base speed
        if traffic == 'Medium':
            transit_speed_kmh = 18.0
        elif traffic == 'High':
            transit_speed_kmh = 13.0
        elif traffic == 'Severe':
            transit_speed_kmh = 9.0
        if weather == 'Rainy':
            transit_speed_kmh *= 0.80

        transit_time = (distance_km / transit_speed_kmh) * 60.0
        transit_time = round(max(5.0, np.random.normal(transit_time, 3.0)), 1)

        # Rider pickup wait time
        rider_wait_time = round(max(1.0, np.random.normal(4.5 if not is_rush_hour else 8.5, 2.5)), 1)

        total_delivery_time = round(prep_time + rider_wait_time + transit_time, 1)

        # Cancellation logic
        # Orders have higher cancellation rate if prep time is huge, weather is rainy, or severe traffic
        cancel_prob = 0.035 # base 3.5%
        if is_rush_hour:
            cancel_prob += 0.035
        if weather == 'Rainy':
            cancel_prob += 0.040
        if total_delivery_time > 55.0:
            cancel_prob += 0.080
        if traffic == 'Severe':
            cancel_prob += 0.050

        is_cancelled = np.random.rand() < cancel_prob

        if is_cancelled:
            # 65% Cancelled by customer, 35% Cancelled by restaurant
            if np.random.rand() < 0.65:
                status = 'Cancelled by Customer'
                reasons = ['Long Delivery Time', 'Changed Mind', 'Ordered by Mistake', 'Rider Not Moving']
                reason_weights = [0.55, 0.20, 0.15, 0.10]
            else:
                status = 'Cancelled by Restaurant'
                reasons = ['Item Out of Stock', 'Kitchen Overload', 'Restaurant Closing Soon']
                reason_weights = [0.50, 0.35, 0.15]
            
            cancellation_reason = np.random.choice(reasons, p=reason_weights)
            delivery_time_final = np.nan
            rating = np.nan
            rider_id = random.choice(rider_pool) if np.random.rand() > 0.3 else np.nan
        else:
            status = 'Delivered'
            cancellation_reason = np.nan
            delivery_time_final = total_delivery_time
            rider_id = random.choice(rider_pool)

            # Rating behavior:
            # ~35% of delivered orders are not rated (NaN)
            if np.random.rand() < 0.35:
                rating = np.nan
            else:
                # Ratings depend heavily on total delivery time!
                # Target SLA is 40 minutes.
                if delivery_time_final <= 30:
                    rating = round(min(5.0, max(1.0, np.random.normal(4.7, 0.4))), 1)
                elif delivery_time_final <= 45:
                    rating = round(min(5.0, max(1.0, np.random.normal(4.1, 0.6))), 1)
                elif delivery_time_final <= 60:
                    rating = round(min(5.0, max(1.0, np.random.normal(2.8, 0.8))), 1)
                else: # severe delay > 60 mins
                    rating = round(min(5.0, max(1.0, np.random.normal(1.6, 0.7))), 1)

        # Inject intentional dirty data variations into some records
        # Inconsistent status casing
        if random.random() < 0.04:
            if status == 'Delivered':
                status = random.choice(['delivered', 'DELIVERED', 'Delivered '])
            elif status == 'Cancelled by Customer':
                status = 'cancelled by customer '
        
        # Inconsistent cuisine casing/whitespace
        cuisine_val = chosen_cuisine
        if random.random() < 0.03:
            cuisine_val = f" {chosen_cuisine} "
        elif random.random() < 0.02:
            cuisine_val = chosen_cuisine.lower()

        # Date string formats
        date_str = order_time.strftime('%Y-%m-%d %H:%M:%S')

        data.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'restaurant_id': restaurant_id,
            'restaurant_name': restaurant_name,
            'cuisine_type': cuisine_val,
            'order_timestamp': date_str,
            'order_status': status,
            'order_value': order_value,
            'delivery_time_minutes': delivery_time_final,
            'preparation_time_minutes': prep_time,
            'rider_wait_time_minutes': rider_wait_time,
            'distance_km': distance_km,
            'rider_id': rider_id,
            'customer_rating': rating,
            'cancellation_reason': cancellation_reason,
            'weather': weather,
            'traffic_level': traffic
        })

    df = pd.DataFrame(data)

    # Inject 35 duplicate rows to simulate double logging
    dup_indices = random.sample(range(len(df)), 35)
    duplicates = df.iloc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # Inject a few invalid/outlier records to clean
    # 5 negative order values
    bad_val_idx = random.sample(range(len(df)), 5)
    for idx in bad_val_idx:
        df.at[idx, 'order_value'] = -round(abs(df.at[idx, 'order_value']), 2)

    # 4 extreme delivery time errors (>300 mins)
    bad_time_idx = random.sample(range(len(df)), 4)
    for idx in bad_time_idx:
        if df.at[idx, 'order_status'] in ['Delivered', 'delivered']:
            df.at[idx, 'delivery_time_minutes'] = 450.0

    print(f"Total raw rows generated (including duplicates & anomalies): {len(df)}")
    return df

if __name__ == '__main__':
    raw_df = generate_synthetic_data(num_records=8500, random_seed=42)
    output_dir = os.path.abspath(r'c:\Users\vyshu\OneDrive\Desktop\project2\food-delivery-operations-analysis\data\raw')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'food_delivery_raw.csv')
    raw_df.to_csv(output_path, index=False)
    print(f"Saved raw dataset to: {output_path}")

