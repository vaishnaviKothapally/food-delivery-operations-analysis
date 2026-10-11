"""
Visualization Generator for Food Delivery Operations Analysis
Food Delivery Operations & Performance Analysis

Generates 8 publication-grade, high-resolution charts for the portfolio project:
1. 01_order_status_distribution.png
2. 02_delivery_time_distribution.png
3. 03_hourly_demand_and_cancellations.png
4. 04_day_of_week_performance.png
5. 05_cuisine_performance_matrix.png
6. 06_ratings_vs_delivery_time.png
7. 07_cancellation_reasons_breakdown.png
8. 08_peak_period_staffing_heatmap.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def generate_all_visuals():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_csv = os.path.join(base_dir, 'data', 'cleaned', 'food_delivery_cleaned.csv')
    visuals_dir = os.path.join(base_dir, 'visuals')
    os.makedirs(visuals_dir, exist_ok=True)

    print(f"Loading cleaned dataset from {cleaned_csv}...")
    df = pd.read_csv(cleaned_csv)
    print(f"Loaded {len(df)} records. Generating visualizations...")

    # Color Palette definitions
    PRIMARY_COLOR = '#1f77b4'
    ACCENT_COLOR = '#ff7f0e'
    SUCCESS_COLOR = '#2ca02c'
    DANGER_COLOR = '#d62728'
    NEUTRAL_COLOR = '#7f7f7f'

    # -------------------------------------------------------------------------
    # CHART 1: Order Status Distribution (Donut Chart & Counts)
    # -------------------------------------------------------------------------
    print("Generating 01_order_status_distribution.png...")
    plt.figure(figsize=(9, 6))
    status_counts = df['order_status'].value_counts()
    colors = [SUCCESS_COLOR, '#e377c2', DANGER_COLOR]
    
    wedges, texts, autotexts = plt.pie(
        status_counts, 
        labels=status_counts.index, 
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        explode=(0.04, 0.08, 0.1),
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        pctdistance=0.75,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    plt.setp(autotexts, size=11, weight='bold', color='white')
    
    # Add center text
    total_orders = len(df)
    plt.text(0, 0, f"Total Orders\n{total_orders:,}", ha='center', va='center', fontsize=13, weight='bold', color='#333333')
    plt.title("Order Fulfillment vs. Cancellation Distribution\n(Overall Operational Completion Rate: 90.6%)", fontsize=14, weight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '01_order_status_distribution.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 2: Delivery Time Distribution & SLA Threshold
    # -------------------------------------------------------------------------
    print("Generating 02_delivery_time_distribution.png...")
    plt.figure(figsize=(10, 6))
    delivered_df = df[df['order_status'] == 'Delivered'].copy()
    
    sns.histplot(
        delivered_df['delivery_time_minutes'], 
        bins=35, 
        kde=True, 
        color=PRIMARY_COLOR, 
        edgecolor='white',
        alpha=0.65
    )
    
    # SLA Line at 40 mins
    plt.axvline(40.0, color=DANGER_COLOR, linestyle='--', linewidth=2.2, label='Target SLA Limit (40 Mins)')
    mean_val = delivered_df['delivery_time_minutes'].mean()
    median_val = delivered_df['delivery_time_minutes'].median()
    plt.axvline(mean_val, color='#ff7f0e', linestyle='-', linewidth=2.0, label=f'Mean Delivery Time ({mean_val:.1f} Mins)')
    plt.axvline(median_val, color='#2ca02c', linestyle=':', linewidth=2.0, label=f'Median Delivery Time ({median_val:.1f} Mins)')
    
    # Annotation for SLA breach
    sla_breach_pct = (delivered_df['delivery_time_minutes'] > 40.0).mean() * 100
    plt.annotate(
        f'SLA Breach: {sla_breach_pct:.1f}% of orders\nexceed 40 minutes',
        xy=(45, 450), xytext=(65, 550),
        arrowprops=dict(arrowstyle="->", color=DANGER_COLOR, lw=1.5),
        fontsize=11, weight='bold', color=DANGER_COLOR,
        bbox=dict(boxstyle="round,pad=0.4", fc="#ffeeee", ec=DANGER_COLOR, lw=1)
    )

    plt.title("Delivered Orders Duration Distribution vs. 40-Minute SLA Benchmark", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Delivery Time (Minutes)", fontsize=12, labelpad=8)
    plt.ylabel("Number of Orders", fontsize=12, labelpad=8)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '02_delivery_time_distribution.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 3: Hourly Demand and Cancellation Rate (Dual Axis)
    # -------------------------------------------------------------------------
    print("Generating 03_hourly_demand_and_cancellations.png...")
    hourly_df = df.groupby('order_hour').agg(
        total_orders=('order_id', 'count'),
        cancelled_orders=('order_status', lambda s: (s.str.startswith('Cancelled')).sum()),
        avg_deliv=('delivery_time_minutes', 'mean')
    ).reset_index()
    hourly_df['cancel_rate_pct'] = (hourly_df['cancelled_orders'] / hourly_df['total_orders']) * 100

    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Bar chart for volume
    color = '#2b5c8f'
    bars = ax1.bar(hourly_df['order_hour'], hourly_df['total_orders'], color=color, alpha=0.75, width=0.7, label='Order Volume')
    ax1.set_xlabel('Hour of the Day (0:00 - 23:00)', fontsize=12, labelpad=8)
    ax1.set_ylabel('Total Order Volume', color=color, fontsize=12, labelpad=8)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(range(0, 24))
    
    # Highlight peak windows
    ax1.axvspan(11.5, 14.5, color='#fff3cd', alpha=0.5, label='Lunch Peak (12-14h)')
    ax1.axvspan(18.5, 22.5, color='#f8d7da', alpha=0.5, label='Dinner Peak (19-22h)')

    # Line chart for cancellation rate
    ax2 = ax1.twinx()
    color2 = '#d9534f'
    line = ax2.plot(hourly_df['order_hour'], hourly_df['cancel_rate_pct'], color=color2, linewidth=2.8, marker='o', markersize=6, label='Cancellation Rate (%)')
    ax2.set_ylabel('Cancellation Rate (%)', color=color2, fontsize=12, labelpad=8)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.grid(False) # Turn off second grid to avoid clutter
    
    plt.title("Hourly Order Demand & Cancellation Dynamics: Identifying Operational Bottlenecks", fontsize=14, weight='bold', pad=15)
    
    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', frameon=True, facecolor='white', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '03_hourly_demand_and_cancellations.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 4: Day of Week Operational Performance (Volume, Revenue, Avg Time)
    # -------------------------------------------------------------------------
    print("Generating 04_day_of_week_performance.png...")
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_df = df.groupby('day_of_week').agg(
        total_orders=('order_id', 'count'),
        total_revenue=('order_value', lambda v: v[df.loc[v.index, 'order_status'] == 'Delivered'].sum()),
        avg_delivery_time=('delivery_time_minutes', 'mean'),
        cancellation_rate=('order_status', lambda s: (s.str.startswith('Cancelled')).mean() * 100)
    ).reindex(dow_order).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot 1: Volume and Net Revenue
    x = np.arange(len(dow_order))
    width = 0.38
    rects1 = ax1.bar(x - width/2, dow_df['total_orders'], width, label='Order Volume', color='#3274a1')
    
    ax1_twin = ax1.twinx()
    rects2 = ax1_twin.bar(x + width/2, dow_df['total_revenue'] / 1000, width, label='Net Revenue ($K)', color='#e1812c')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels([d[:3] for d in dow_order], fontsize=11)
    ax1.set_ylabel('Order Count', fontsize=11, color='#3274a1')
    ax1_twin.set_ylabel('Net Revenue ($ in Thousands)', fontsize=11, color='#e1812c')
    ax1_twin.grid(False)
    ax1.set_title("Order Volume and Net Revenue by Day of Week", fontsize=12, weight='bold')

    # Subplot 2: Average Delivery Time and Cancellation Rate
    ax2.plot(dow_order, dow_df['avg_delivery_time'], marker='s', color='#2ca02c', linewidth=2.5, label='Avg Delivery Time (min)')
    ax2.set_ylabel('Avg Delivery Duration (Minutes)', fontsize=11, color='#2ca02c')
    ax2.set_xticks(range(len(dow_order)))
    ax2.set_xticklabels([d[:3] for d in dow_order], fontsize=11)
    ax2.axhline(40.0, color='red', linestyle='--', alpha=0.7, label='40-Min SLA Benchmark')

    ax2_twin = ax2.twinx()
    ax2_twin.plot(dow_order, dow_df['cancellation_rate'], marker='^', color='#d62728', linewidth=2.5, linestyle=':', label='Cancellation Rate (%)')
    ax2_twin.set_ylabel('Cancellation Rate (%)', fontsize=11, color='#d62728')
    ax2_twin.grid(False)
    ax2.set_title("Delivery Speed vs. Cancellation Frequency by Day of Week", fontsize=12, weight='bold')

    lines_a, labels_a = ax2.get_legend_handles_labels()
    lines_b, labels_b = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_a + lines_b, labels_a + labels_b, loc='upper left', fontsize=9)

    plt.suptitle("Weekly Operational Rhythm: Volume Surge & Delivery Degradation on Weekends", fontsize=14, weight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '04_day_of_week_performance.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 5: Cuisine Performance Matrix (Revenue vs Rating vs Cancellation)
    # -------------------------------------------------------------------------
    print("Generating 05_cuisine_performance_matrix.png...")
    cuisine_df = df.groupby('cuisine_type').agg(
        total_orders=('order_id', 'count'),
        total_revenue=('order_value', lambda v: v[df.loc[v.index, 'order_status'] == 'Delivered'].sum()),
        avg_rating=('customer_rating', 'mean'),
        avg_deliv=('delivery_time_minutes', 'mean'),
        cancel_rate=('order_status', lambda s: (s.str.startswith('Cancelled')).mean() * 100)
    ).reset_index().sort_values(by='total_revenue', ascending=False)

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        cuisine_df['avg_deliv'],
        cuisine_df['cancel_rate'],
        s=cuisine_df['total_revenue'] / 80, # Bubble size proportional to revenue
        c=cuisine_df['avg_rating'],
        cmap='viridis',
        alpha=0.85,
        edgecolors='black',
        linewidth=1.2
    )
    cbar = plt.colorbar(scatter)
    cbar.set_label('Average Customer Rating (1.0 - 5.0)', fontsize=11, labelpad=10)

    for _, row in cuisine_df.iterrows():
        plt.annotate(
            f"{row['cuisine_type']}\n(${row['total_revenue']/1000:.1f}k)",
            xy=(row['avg_deliv'], row['cancel_rate']),
            xytext=(row['avg_deliv'] + 0.15, row['cancel_rate'] + 0.15),
            fontsize=9.5, weight='bold',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#bbbbbb", alpha=0.8)
        )

    plt.title("Cuisine Operational Matrix\n(X: Delivery Time | Y: Cancellation % | Size: Revenue | Color: Rating)", fontsize=13, weight='bold', pad=15)
    plt.xlabel("Average Delivery Time (Minutes)", fontsize=11, labelpad=8)
    plt.ylabel("Cancellation Rate (%)", fontsize=11, labelpad=8)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '05_cuisine_performance_matrix.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 6: Customer Rating vs Delivery Time (The Satisfaction Cliff)
    # -------------------------------------------------------------------------
    print("Generating 06_ratings_vs_delivery_time.png...")
    rated_df = df[(df['order_status'] == 'Delivered') & (df['customer_rating'].notnull())].copy()
    
    plt.figure(figsize=(10, 6))
    # Boxplot across delivery time buckets
    order_buckets = ['<=30 min (Fast)', '31-45 min (Standard)', '46-60 min (Delayed)', '>60 min (Severe Delay)']
    colors_bucket = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
    
    sns.boxplot(
        x='delivery_time_bucket',
        y='customer_rating',
        hue='delivery_time_bucket',
        legend=False,
        data=rated_df,
        order=order_buckets,
        palette=colors_bucket,
        width=0.45,
        boxprops=dict(alpha=0.8),
        fliersize=3
    )

    # Add mean points and annotations
    means = rated_df.groupby('delivery_time_bucket', observed=True)['customer_rating'].mean()
    for idx, bucket in enumerate(order_buckets):
        mean_rating = means[bucket]
        plt.text(idx, mean_rating + 0.22, f"Mean: {mean_rating:.2f} / 5", ha='center', fontsize=11, weight='bold', color='#111111')

    plt.title("The '45-Minute Cliff': Severe Rating Degradation Beyond SLA Benchmark", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Delivery Duration Category", fontsize=12, labelpad=8)
    plt.ylabel("Customer Rating (1.0 to 5.0 Stars)", fontsize=12, labelpad=8)
    plt.ylim(0.5, 5.5)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '06_ratings_vs_delivery_time.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 7: Cancellation Reasons Root-Cause Breakdown
    # -------------------------------------------------------------------------
    print("Generating 07_cancellation_reasons_breakdown.png...")
    cancel_df = df[df['order_status'].str.startswith('Cancelled')].copy()
    reason_counts = cancel_df.groupby(['cancellation_reason', 'order_status']).size().unstack(fill_value=0)
    reason_counts['Total'] = reason_counts.sum(axis=1)
    reason_counts = reason_counts.sort_values(by='Total', ascending=True)
    
    plt.figure(figsize=(10, 6))
    ax = reason_counts[['Cancelled by Customer', 'Cancelled by Restaurant']].plot(
        kind='barh', 
        stacked=True, 
        figsize=(10, 6),
        color=['#d62728', '#ff7f0e'],
        edgecolor='white',
        alpha=0.85
    )

    for p in ax.patches:
        width = p.get_width()
        if width > 15:
            ax.annotate(f"{int(width)}", (p.get_x() + width / 2, p.get_y() + p.get_height() / 2),
                        ha='center', va='center', color='white', weight='bold', fontsize=10)

    plt.title("Root-Cause Breakdown of Order Cancellations\n(Customer vs. Restaurant Initiated)", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Number of Cancelled Orders", fontsize=12, labelpad=8)
    plt.ylabel("Cancellation Root Cause", fontsize=12, labelpad=8)
    plt.legend(title="Initiated By", frameon=True, facecolor='white', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '07_cancellation_reasons_breakdown.png'), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # CHART 8: Peak Period Demand Intensity Heatmap (Staffing & Allocation)
    # -------------------------------------------------------------------------
    print("Generating 08_peak_period_staffing_heatmap.png...")
    plt.figure(figsize=(13, 6.5))
    heatmap_data = df.pivot_table(
        index='day_of_week', 
        columns='order_hour', 
        values='order_id', 
        aggfunc='count',
        fill_value=0
    ).reindex(dow_order)

    sns.heatmap(
        heatmap_data, 
        cmap='YlOrRd', 
        annot=True, 
        fmt='d', 
        cbar_kws={'label': 'Hourly Order Volume'},
        linewidths=0.5,
        linecolor='#e0e0e0'
    )
    plt.title("Operational Dispatch Heatmap: Hourly Demand Intensity Across Weekdays\n(Critical for Rider Scheduling & Kitchen Staff Allocation)", fontsize=13, weight='bold', pad=15)
    plt.xlabel("Hour of the Day (24-Hour Military Time)", fontsize=12, labelpad=8)
    plt.ylabel("Day of the Week", fontsize=12, labelpad=8)
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '08_peak_period_staffing_heatmap.png'), dpi=300)
    plt.close()

    print("All 8 visualizations successfully generated in 'visuals/'!")

if __name__ == '__main__':
    generate_all_visuals()
