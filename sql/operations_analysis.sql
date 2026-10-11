-- ==============================================================================
-- Food Delivery Operations & Performance Analysis
-- Database: SQLite (food_delivery.db)
-- Author: Data Analytics Portfolio Project
-- Purpose: Extract operational KPIs, time-based demand patterns, cancellation 
--          root causes, and customer satisfaction metrics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Overall Order Fulfillment & Cancellation Rate
-- Explanation: Computes total volume placed, total completed (delivered), 
-- total cancellations, and overall cancellation percentage.
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_orders_placed,
    SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS total_orders_completed,
    SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1 ELSE 0 END) AS total_orders_cancelled,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(SUM(CASE WHEN order_status = 'Cancelled by Customer' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS customer_cancel_rate_pct,
    ROUND(SUM(CASE WHEN order_status = 'Cancelled by Restaurant' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS restaurant_cancel_rate_pct,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS total_net_revenue
FROM orders;


-- ------------------------------------------------------------------------------
-- QUERY 2: Delivery Performance & SLA Metrics (Delivered Orders Only)
-- Explanation: Evaluates key operational benchmarks: average, min, and max 
-- delivery time, preparation time, rider wait time, and percentage of orders delayed (>40 min).
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS delivered_orders_count,
    ROUND(AVG(delivery_time_minutes), 2) AS avg_delivery_time_min,
    ROUND(MIN(delivery_time_minutes), 2) AS min_delivery_time_min,
    ROUND(MAX(delivery_time_minutes), 2) AS max_delivery_time_min,
    ROUND(AVG(preparation_time_minutes), 2) AS avg_kitchen_prep_time_min,
    ROUND(AVG(rider_wait_time_minutes), 2) AS avg_rider_wait_time_min,
    ROUND(AVG(distance_km), 2) AS avg_delivery_distance_km,
    ROUND(SUM(CASE WHEN delivery_time_minutes > 40.0 THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS sla_breach_rate_pct
FROM orders
WHERE order_status = 'Delivered';


-- ------------------------------------------------------------------------------
-- QUERY 3: Hourly Demand, Revenue, Delivery Duration, and Cancellation Rate
-- Explanation: Dissects operational performance across the 24-hour cycle.
-- Highlights peak hours, revenue spikes, delivery time degradation, and cancellation surges.
-- ------------------------------------------------------------------------------
SELECT 
    order_hour,
    meal_period,
    COUNT(*) AS total_orders,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS total_revenue,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    RANK() OVER (ORDER BY COUNT(*) DESC) AS volume_rank
FROM orders
GROUP BY order_hour, meal_period
ORDER BY order_hour ASC;


-- ------------------------------------------------------------------------------
-- QUERY 4: Meal Period Operational Summary
-- Explanation: Aggregates order volume, revenue contribution, and delivery speed
-- across key dayparts (Breakfast, Lunch, Afternoon, Dinner, Late Night).
-- ------------------------------------------------------------------------------
SELECT 
    meal_period,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS order_share_pct,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS total_revenue,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN customer_rating ELSE NULL END), 2) AS avg_customer_rating
FROM orders
GROUP BY meal_period
ORDER BY total_orders DESC;


-- ------------------------------------------------------------------------------
-- QUERY 5: Day of Week Performance & Weekend vs Weekday Dynamics
-- Explanation: Compares weekday versus weekend demand, operational speed, 
-- and cancellation behavior to guide weekly staffing schedules.
-- ------------------------------------------------------------------------------
SELECT 
    day_of_week,
    day_of_week_num,
    COUNT(*) AS total_orders,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS total_revenue,
    ROUND(AVG(order_value), 2) AS avg_order_value,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN customer_rating ELSE NULL END), 2) AS avg_rating
FROM orders
GROUP BY day_of_week, day_of_week_num
ORDER BY day_of_week_num ASC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Monthly Order Trends & Revenue Trajectory
-- Explanation: Tracks month-over-month volume, completed revenue, and average 
-- delivery speed across the six-month operating window.
-- ------------------------------------------------------------------------------
SELECT 
    year_month,
    month_name,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS monthly_revenue,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM orders
GROUP BY year_month, month_name
ORDER BY year_month ASC;


-- ------------------------------------------------------------------------------
-- QUERY 7: Cuisine Performance & Category Contribution
-- Explanation: Compares performance metrics by cuisine: volume, net revenue,
-- average order value (AOV), average delivery time, customer rating, and cancellation rate.
-- ------------------------------------------------------------------------------
SELECT 
    cuisine_type,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS volume_share_pct,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS total_revenue,
    ROUND(AVG(order_value), 2) AS avg_order_value,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN customer_rating ELSE NULL END), 2) AS avg_customer_rating,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM orders
GROUP BY cuisine_type
ORDER BY total_orders DESC;


-- ------------------------------------------------------------------------------
-- QUERY 8: Top 10 Performing Restaurants by Revenue and Volume
-- Explanation: Ranks the top restaurants by completed order volume, revenue,
-- average rating, and customer cancellation rate.
-- ------------------------------------------------------------------------------
SELECT 
    restaurant_name,
    cuisine_type,
    COUNT(*) AS total_orders_placed,
    SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS orders_completed,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' THEN order_value ELSE 0 END), 2) AS net_revenue,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN customer_rating ELSE NULL END), 2) AS avg_rating,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM orders
GROUP BY restaurant_name, cuisine_type
ORDER BY net_revenue DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 9: Customer Satisfaction vs Delivery Duration
-- Explanation: Demonstrates the correlation between delivery duration buckets 
-- and customer ratings, including the proportion of low ratings (rating < 3.0).
-- ------------------------------------------------------------------------------
SELECT 
    delivery_time_bucket,
    COUNT(*) AS total_rated_orders,
    ROUND(AVG(customer_rating), 2) AS avg_rating,
    ROUND(SUM(CASE WHEN customer_rating < 3.0 THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS low_rating_pct,
    ROUND(SUM(CASE WHEN customer_rating >= 4.5 THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS high_rating_pct
FROM orders
WHERE order_status = 'Delivered' AND customer_rating IS NOT NULL
GROUP BY delivery_time_bucket
ORDER BY delivery_time_bucket ASC;


-- ------------------------------------------------------------------------------
-- QUERY 10: Root Cause Analysis of Order Cancellations
-- Explanation: Breaks down cancellation reasons across customer-initiated and 
-- restaurant-initiated cancellations to identify key operational failure points.
-- ------------------------------------------------------------------------------
SELECT 
    order_status,
    cancellation_reason,
    COUNT(*) AS cancellation_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_status LIKE 'Cancelled%'), 2) AS pct_of_all_cancellations
FROM orders
WHERE order_status LIKE 'Cancelled%'
GROUP BY order_status, cancellation_reason
ORDER BY cancellation_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 11: Impact of External Factors (Weather & Traffic) on Operations
-- Explanation: Analyzes how adverse weather and traffic congestion exacerbate 
-- delivery delays, SLA breaches, and cancellation frequency.
-- ------------------------------------------------------------------------------
SELECT 
    weather,
    traffic_level,
    COUNT(*) AS total_orders,
    ROUND(AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_minutes ELSE NULL END), 2) AS avg_delivery_time_min,
    ROUND(SUM(CASE WHEN order_status = 'Delivered' AND delivery_time_minutes > 40.0 THEN 1.0 ELSE 0.0 END) * 100.0 / 
          SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END), 2) AS sla_breach_pct,
    ROUND(SUM(CASE WHEN order_status LIKE 'Cancelled%' THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM orders
GROUP BY weather, traffic_level
ORDER BY avg_delivery_time_min DESC;

