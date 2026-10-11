# Data Cleaning & Preprocessing Report

**Project:** Food Delivery Operations and Performance Analysis  
**Database/File:** `data/cleaned/food_delivery_cleaned.csv` & `data/cleaned/food_delivery.db`  
**Execution Date:** 2026-10-12  

---

## 1. Executive Summary
Data cleaning was executed on the raw food delivery transaction dataset to ensure structural integrity, remove logging duplicates, rectify negative values and sensor glitches, and enrich the schema with time-based features required for operational analysis.

### Row Count Reconciliation
| Stage | Record Count | Records Dropped | Rationale / Decision |
| :--- | :--- | :--- | :--- |
| **Raw Ingestion** | 8,535 | 0 | Baseline raw ingested transactional records. |
| **Deduplication** | 8,500 | 35 | Removed duplicate records sharing identical `order_id` values resulting from retry logging. Retained first occurrence. |
| **Negative Order Values** | 8,495 | 5 | Dropped rows containing negative `order_value` (data entry / reversal errors). |
| **Extreme Time Outliers** | 8,491 | 4 | Dropped records where `delivery_time_minutes` exceeded 180 minutes (450-minute GPS tracking glitches). |
| **Final Cleaned Dataset** | **8,491** | **Total: 44** | **Net retention rate: 99.48%** |

---

## 2. Column-by-Column Audit and Handling Decisions

### 2.1 String & Text Standardization
1. **`cuisine_type`**:
   - *Issue:* Leading/trailing whitespaces (e.g., `' Indian '`) and mixed lowercasing (`'indian'`).
   - *Fix:* Stripped whitespace and applied title-casing (`str.title()`). Standardized multi-word labels (e.g., `'Bakery & Desserts'`).
2. **`order_status`**:
   - *Issue:* Inconsistent casing (`'delivered'`, `'DELIVERED'`, `'cancelled by customer '`).
   - *Fix:* Stripped whitespace and standardized into three canonical categories:
     - `'Delivered'`
     - `'Cancelled by Customer'`
     - `'Cancelled by Restaurant'`

### 2.2 Datetime Transformation & Feature Engineering
- **Source Column:** `order_timestamp` (string format `YYYY-MM-DD HH:MM:SS`).
- **Engineered Attributes:**
  - `order_date`: `YYYY-MM-DD` string for daily grouping.
  - `order_time`: `HH:MM:SS` string for precise timing.
  - `order_hour`: Integer `[0, 23]` for hourly peak load analysis.
  - `day_of_week`: String (`Monday` to `Sunday`).
  - `day_of_week_num`: Integer (`0` = Monday, `6` = Sunday) for sorting.
  - `is_weekend`: Binary flag (`1` for Saturday/Sunday, `0` for Monday-Friday).
  - `month_name` & `year_month`: Grouping attributes for monthly revenue and volume trends.
  - `meal_period`: Categorical bin:
    - *Breakfast:* 06:00 – 10:59
    - *Lunch:* 11:00 – 14:59
    - *Afternoon:* 15:00 – 17:59
    - *Dinner:* 18:00 – 22:59
    - *Late Night:* 23:00 – 05:59

### 2.3 Numerical Validation & Integrity Checks
1. **`order_value`**:
   - Validated that values are positive floats. Removed 5 negative values (`-$XX.XX`).
2. **`delivery_time_minutes`**:
   - Verified that for Cancelled orders, `delivery_time_minutes` is `NaN` (no delivery occurred).
   - For Delivered orders, values outside standard delivery thresholds (> 180 mins) were identified as tracking disconnections and removed.
3. **`preparation_time_minutes` & `distance_km`**:
   - Confirmed all remaining rows have strictly positive prep times (range: 8.0 to 38.5 mins) and distances (range: 0.8 to 14.8 km).
4. **`customer_rating`**:
   - Range strictly bounded between 1.0 and 5.0.
   - 3,491 delivered orders have missing ratings. **Decision:** Preserved `NaN` values without artificial mean/median imputation. In food delivery operations, imputation severely distorts customer satisfaction metrics and satisfaction-vs-delay correlations.
5. **`cancellation_reason`**:
   - Validated that delivered orders have `NaN` for cancellation reason.
   - Any cancelled orders without an explicit reason were labeled as `'Reason Unspecified'`.

### 2.4 Operational Performance Flags
- **`is_delayed`**: Binary indicator where `delivery_time_minutes > 40.0` minutes (standard company SLA).
- **`delivery_time_bucket`**: Categorical binned feature:
  - `<=30 min (Fast)`
  - `31-45 min (Standard)`
  - `46-60 min (Delayed)`
  - `>60 min (Severe Delay)`

---

## 3. Storage and Database Schema
The cleaned dataset was exported to:
1. **CSV:** `data/cleaned/food_delivery_cleaned.csv`
2. **SQLite Database:** `data/cleaned/food_delivery.db` (table: `orders`)

Indexed columns in SQLite:
- `order_id` (Primary Key logical lookup)
- `order_status`
- `order_hour`
- `day_of_week`
- `cuisine_type`

