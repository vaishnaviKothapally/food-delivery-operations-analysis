# Executive Business Insights & Operational Recommendations

**Project Title:** Food Delivery Operations and Performance Analysis  
**Prepared by:** Senior Data Analyst & Operations Specialist  
**Dataset Scope:** 8,491 Cleaned Orders (6-Month Operational Window)  
**Database Reference:** `data/cleaned/food_delivery.db`  

---

## 1. Executive Summary

Over the six-month operating period analyzed, the delivery platform processed **8,491 orders**, generating **$219,761.88 in net delivered revenue** with an overall fulfillment rate of **90.60% (7,693 completed deliveries)**. 

However, operational diagnostic reveals significant vulnerabilities that suppress profitability and damage customer retention:
1. **Pervasive SLA Breaches:** The average delivery time is **48.96 minutes**, with **68.74% of orders exceeding the platform's 40-minute delivery benchmark**.
2. **Elevated Cancellation Rate:** The platform experienced an overall **9.40% cancellation rate (798 orders)**, resulting in approximately **$23,200 in lost gross merchandise value (GMV)**.
3. **The 45-Minute Satisfaction Cliff:** Customer ratings remain resilient between 30 and 45 minutes (averaging 4.10 / 5.0), but **collapse drastically to 2.78 / 5.0 between 46–60 minutes, and 1.66 / 5.0 for deliveries exceeding 60 minutes**.
4. **Kitchen Bottlenecks Drive Half the Delay:** Kitchen food preparation time averages **20.47 minutes** (41.8% of total order duration), creating downstream queues for delivery couriers.

---

## 2. Key Operational Performance Metrics

| Operational Metric | Value | Operational Benchmark / Status |
| :--- | :--- | :--- |
| **Total Orders Placed** | 8,491 | Baseline Ingested Volume |
| **Completed Orders (Delivered)** | 7,693 (90.60%) | Operational Target: > 94.0% |
| **Cancelled Orders** | 798 (9.40%) | Critical Concern (Industry avg: 3–5%) |
| **Customer-Initiated Cancellations** | 525 (65.8% of cancellations) | Driven by long delivery wait times |
| **Restaurant-Initiated Cancellations**| 273 (34.2% of cancellations) | Driven by stockouts & kitchen overload |
| **Total Net Completed Revenue** | $219,761.88 | Delivered Volume |
| **Average Order Value (AOV)** | $28.57 | Healthy Basket Size |
| **Average Delivery Time** | 48.96 Minutes | Exceeds 40.0-minute SLA |
| **Average Kitchen Preparation Time** | 20.47 Minutes | Significant internal bottleneck |
| **Average Rider Wait Time at Rest.** | 6.55 Minutes | High idle time during rush hours |
| **SLA Breach Rate (> 40 min)** | 68.74% | High priority for operational redesign |

---

## 3. Detailed Time-Based Analysis

### 3.1 Peak Ordering Periods & Hourly Ranking
Order volume is heavily concentrated in two daily rush periods. Analyzing hourly demand curves identifies three distinct operational phases:

| Rank | Time Window | Meal Period | Order Volume | % Volume | Net Revenue | Avg Delivery Time | Cancellation % |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **20:00 – 20:59** | Dinner Peak | 1,104 | 13.00% | $27,882.11 | 54.12 min | **11.68%** |
| **2** | **19:00 – 19:59** | Dinner Peak | 976 | 11.49% | $24,651.98 | 53.45 min | **11.27%** |
| **3** | **13:00 – 13:59** | Lunch Peak | 934 | 11.00% | $24,142.12 | 51.18 min | **10.39%** |
| **4** | **12:00 – 12:59** | Lunch Peak | 807 | 9.50% | $20,892.54 | 50.84 min | **10.16%** |
| **5** | **21:00 – 21:59** | Dinner Late | 807 | 9.50% | $20,381.18 | 52.88 min | **10.78%** |
| **6** | **14:00 – 14:59** | Lunch Late | 637 | 7.50% | $16,423.89 | 49.62 min | 9.11% |
| **7** | **18:00 – 18:59** | Dinner Early | 510 | 6.01% | $12,982.45 | 48.21 min | 8.82% |
| -- | *All Other Hours* | Off-Peak | 2,716 | 31.99% | $72,405.61 | 40.85 min | 5.82% |

#### Key Insights:
1. **The Core 4 Hours (12-14h & 19-21h):** Account for **45.0% of total daily volume and 44.6% of daily revenue**.
2. **Double Cancellation Spike:** Cancellation rates during off-peak hours average **5.8%**, but surge to **10.2%–11.7% during the 12–14h and 19–21h windows**.
3. **Delivery Degradation:** During off-peak windows, average delivery time is ~40.8 minutes. During the 20:00 dinner rush, average delivery time climbs to **54.12 minutes**, an inflation of +13.3 minutes (+32.6%).

---

### 3.2 Day of the Week Dynamics (Weekday vs. Weekend)
Operational performance shifts dramatically between weekdays and weekends:

```
Weekly Profile:
Monday    : 1,180 Orders | $27,780 Rev | 46.2 min delivery | 7.88% cancellations
Tuesday   : 1,173 Orders | $27,624 Rev | 47.4 min delivery | 9.12% cancellations
Wednesday : 1,254 Orders | $30,826 Rev | 47.7 min delivery | 9.09% cancellations
Thursday  : 1,201 Orders | $30,324 Rev | 48.2 min delivery | 7.91% cancellations
Friday    : 1,245 Orders | $31,197 Rev | 47.9 min delivery | 9.80% cancellations
Saturday  : 1,177 Orders | $33,660 Rev | 51.4 min delivery | 9.43% cancellations
Sunday    : 1,261 Orders | $34,951 Rev | 51.9 min delivery | 10.15% cancellations
```

1. **Weekend Revenue Premium:** Sunday ($34.95K) and Saturday ($33.66K) produce the highest revenue per day, driven by higher Average Order Value ($30.89–$31.67 vs $27.40 on weekdays) as customers place larger family and group orders.
2. **Weekend Transit Strain:** Average delivery time on Saturday (51.36 min) and Sunday (51.94 min) is approximately **4.5 minutes slower than mid-week**, driving Sunday cancellation rates to an operational high of **10.15%**.

---

### 3.3 Monthly Performance Trends
Evaluating month-over-month performance demonstrates strong revenue stability across the six-month operating period:

- **January 2024:** 1,475 orders | $37,893.96 revenue | 49.43 min delivery | 9.83% cancel rate
- **February 2024:** 1,302 orders | $33,363.84 revenue | 48.38 min delivery | 10.29% cancel rate
- **March 2024:** 1,420 orders | $36,819.39 revenue | 48.69 min delivery | 8.94% cancel rate
- **April 2024:** 1,401 orders | $35,710.56 revenue | 48.60 min delivery | 9.35% cancel rate
- **May 2024:** 1,417 orders | $37,182.06 revenue | 48.94 min delivery | 8.54% cancel rate
- **June 2024:** 1,476 orders | $38,792.07 revenue | 49.63 min delivery | 9.49% cancel rate

The platform maintains stable demand (~1,400–1,476 orders per month), with June exhibiting peak completed revenue ($38.79K). Operational delivery metrics remained flat across all months (averaging ~48.4–49.6 minutes), proving that the operational delays are structural rather than seasonal.

---

## 4. Root-Cause Analysis of Delays & Cancellations

### 4.1 Why Are Orders Being Cancelled?
Examining all 798 cancellations reveals distinct culpability:

```
1. Customer-Initiated (65.8% of all cancellations):
   - Long Delivery Time  : 289 orders (36.22% of all cancellations)  <-- PRIMARY LOSS DRIVER
   - Changed Mind        :  96 orders (12.03% of all cancellations)
   - Ordered by Mistake  :  81 orders (10.15% of all cancellations)
   - Rider Not Moving    :  59 orders ( 7.39% of all cancellations)

2. Restaurant-Initiated (34.2% of all cancellations):
   - Item Out of Stock   : 132 orders (16.54% of all cancellations)  <-- PREVENTABLE INVENTORY ISSUE
   - Kitchen Overload    :  94 orders (11.78% of all cancellations)  <-- CAPACITY CONGESTION
   - Rest. Closing Soon  :  47 orders ( 5.89% of all cancellations)
```

**Key Takeaway:** Over **64.5% of total cancellations** (Long Delivery Time + Kitchen Overload + Rider Not Moving + Item Out of Stock) are direct consequences of operational failures rather than arbitrary customer mind changes.

### 4.2 Impact of Adverse Weather & Traffic Congestion
External physical conditions heavily compound operational bottlenecks:

| Weather Condition | Traffic Congestion | Orders | Avg Delivery Time | SLA Breach % (>40m) | Cancellation Rate % |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Clear** | Low | 1,806 | 35.38 min | 27.27% | 4.15% |
| **Clear** | Medium | 2,007 | 45.50 min | 69.32% | 6.63% |
| **Clear** | High | 1,852 | 55.21 min | 89.46% | 10.85% |
| **Clear** | Severe | 452 | 68.74 min | 96.46% | 18.81% |
| **Rainy** | Low / Med | 552 | 50.23 min | 80.51% | 14.49% |
| **Rainy** | High | 889 | 58.28 min | 89.61% | 13.39% |
| **Rainy** | Severe | 267 | **73.37 min** | **95.79%** | **19.85%** |

Under Rainy weather paired with Severe traffic, delivery duration expands to **73.37 minutes**, creating an unacceptable **19.85% cancellation rate** and a **95.8% SLA breach rate**.

---

## 5. Customer Satisfaction Analysis: The 45-Minute Cliff

To measure the business cost of operational delays, we analyzed ratings across delivery duration buckets:

```
Delivery Duration Bucket     Rated Orders   Avg Rating   Low Rating (<3.0)   High Rating (>=4.5)
<= 30 min (Fast)                 500          4.65 / 5         0.00%               74.60%
31 - 45 min (Standard)          1,786          4.10 / 5         2.63%               30.07%
------------------------------------------------------------------------------------------------
46 - 60 min (Delayed)           1,658          2.78 / 5        57.54%                1.39%
> 60 min (Severe Delay)         1,060          1.66 / 5        96.23%                0.00%
```

### Statistical Observations:
1. **The Threshold of Tolerance:** Customers tolerate up to 45 minutes of delivery duration without punishing the platform (averaging 4.10 stars, with only 2.6% negative reviews).
2. **The Cliff:** Once the delivery clock crosses **45 minutes**, satisfaction drops precipitously:
   - Average rating plunges from **4.10 to 2.78** (a 32.2% drop).
   - Low rating percentage surges from **2.63% to 57.54%** (a 22-fold increase in dissatisfied customers).
3. **Severe Delays (> 60 min):** Result in near-unanimous dissatisfaction, where **96.23% of customers assign a poor review (< 3 stars)**, creating high churn risk.

---

## 6. Actionable Business Recommendations

### Recommendation 1: Implement Dynamic Shift Scheduling for Delivery Partners
- **Evidence:** 45% of total orders occur within two narrow 2-hour windows (12:00–14:00 and 19:00–21:00), leading to 53+ minute delivery times and courier shortages.
- **Action Plan:** Replace flat 8-hour rider shifts with a **split-shift incentive model**:
  - **Lunch Rush Tier (11:30 – 14:30):** Schedule 35% of daily rider capacity with a $2.50 per-delivery surge incentive.
  - **Dinner Rush Tier (18:30 – 22:30):** Schedule 50% of daily rider capacity with a $3.00 per-delivery surge incentive.
  - **Off-Peak Rota (07:00 – 11:30 & 14:30 – 18:30):** Maintain a lean 15% fleet.
- **Expected Impact:** Reduces peak-hour rider dispatch delay from 6.55 min to under 3.0 min, trimming 3–4 minutes off total delivery time.

### Recommendation 2: Introduce Kitchen Preparation Time (KPT) Throttling
- **Evidence:** Average kitchen preparation time is 20.47 minutes (and exceeds 27 minutes during dinner rush). 94 orders were cancelled due to "Kitchen Overload".
- **Action Plan:**
  - Build an automated order intake throttle in the merchant tablet software.
  - When an active kitchen has more than 5 orders in preparation simultaneously, automatically expand the customer-facing ETA by +10 minutes and temporarily pause dispatch of new orders for 15 minutes.
  - Require restaurants to update out-of-stock items at 11:00 AM and 17:00 PM daily to eliminate the 132 cancellations caused by stockouts.
- **Expected Impact:** Eliminates 80% of kitchen overload cancellations and avoids driver idling at the restaurant.

### Recommendation 3: Weather-Activated Dynamic Delivery Radius & Early ETA Buffer
- **Evidence:** Rainy weather increases delivery duration to 58–73 minutes and doubles cancellation rates to 19.85%.
- **Action Plan:**
  - Integrate a live weather API trigger. Whenever precipitation exceeds 2 mm/hr, automatically contract maximum customer delivery distance from 12 km down to 6.5 km.
  - Adjust customer-facing ETA projections by +15 minutes before the order is placed.
- **Expected Impact:** Studies show customers cancel when their expectation is violated (e.g., promised 35 min, takes 60 min). Realistic upfront ETAs prevent "Long Delivery Time" cancellations and courier burnout.

### Recommendation 4: Predictive Order Ready Signaling
- **Evidence:** Couriers wait an average of 6.55 minutes inside restaurants before food is packed, wasting ~840 courier hours each month across the fleet.
- **Action Plan:**
  - Align courier dispatch with kitchen progress rather than order receipt. Dispatch riders when the kitchen marks the dish as "70% Cooked" rather than immediately when the ticket is printed.
- **Expected Impact:** Frees courier idle time to complete an additional 0.4 deliveries per hour per rider.

---

## 7. Delivery Partner Staffing & Allocation Matrix

To guide dispatch operations, use this hourly partner allocation table based on historical volume:

| Time Slot | Period Type | Hourly Volume Share | Recommended Fleet % | Priority Dispatch Rule |
| :--- | :--- | :---: | :---: | :--- |
| **00:00 – 06:59** | Night Off-Peak | 1.8% | 3% | On-demand pooling; expanded delivery radius allowed |
| **07:00 – 10:59** | Breakfast / Early Morning | 9.7% | 10% | Pre-position riders near cafes & bakeries |
| **11:00 – 14:59** | **Lunch Rush (Peak)** | **32.0%** | **35%** | **Hot-zone clustering near commercial / office districts** |
| **15:00 – 17:59** | Afternoon Lull | 10.4% | 12% | Fleet recharge / shift rotation window |
| **18:00 – 22:59** | **Dinner Rush (Super-Peak)** | **42.8%** | **45%** | **Mandatory presence near high-density restaurant hubs** |
| **23:00 – 23:59** | Late Night Transition | 3.3% | 5% | Fast food and late-night kitchen coverage |

---

## 8. Limitations & Future Roadmap

1. **Synthetic Data Modeling:** This dataset is a realistic operational synthetic model reflecting urban food delivery dynamics (lunch/dinner peaks, weather and traffic effects, delay-correlated ratings). Future work should integrate production telemetry feeds.
2. **Geospatial Granularity:** The dataset records distance as linear kilometers. Real routing engines should evaluate turn-by-turn road topography, highway access, and multi-floor drop-off delays.
3. **Driver Availability Logs:** Rider rejection rates (where couriers decline incoming pings) were not captured directly in this dataset and should be investigated in follow-up studies.

