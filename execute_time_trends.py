#!/usr/bin/env python3
"""
Execute Time Trends Analysis
This script runs the time trends analysis and generates the required outputs.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os
from pathlib import Path

# Add sql directory to path for database utilities
sys.path.append('sql')
from database_setup import DatabaseManager

# Configure display and warnings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

def main():
    print("🚀 Starting Time Trends Analysis")
    print("=" * 50)
    
    # Create charts directory if it doesn't exist
    charts_dir = Path('assets/charts')
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize database connection
    print("Connecting to PostgreSQL database...")
    
    try:
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        
        # Test connection
        status = db_manager.test_connection()
        print(f"✅ Connected to database: {status['database']}")
        print(f"📊 Tables available: {status['table_count']}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and database is set up correctly")
        return
    
    # SQL query for monthly posting volume trends over time
    time_trends_query = """
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
    ORDER BY posting_count DESC
    LIMIT 10;
    """
    
    print("\n🔍 Analysis: Monthly Posting Volume Trends")
    print("=" * 50)
    print("📈 Executing SQL Query for Time Trends Analysis...")
    
    # Execute query and get results
    time_trends_df = pd.read_sql(time_trends_query, engine)
    
    print(f"\n📊 Time Trends Analysis Results:")
    print(f"Total periods analyzed: {len(time_trends_df)}")
    print("\n💼 Top 10 months by posting volume:")
    print(time_trends_df.to_string(index=False))
    
    # Get complete time series data for visualization
    complete_trends_query = """
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count
    FROM jobs 
    WHERE posting_year IS NOT NULL 
        AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month
    ORDER BY posting_year, posting_month;
    """
    
    complete_trends_df = pd.read_sql(complete_trends_query, engine)
    
    # Create a proper date column for plotting
    complete_trends_df['date'] = pd.to_datetime(
        complete_trends_df['posting_year'].astype(str) + '-' + 
        complete_trends_df['posting_month'].astype(str).str.zfill(2) + '-01'
    )
    complete_trends_df['year_month'] = complete_trends_df['date'].dt.strftime('%Y-%m')
    
    print(f"\n📅 Complete time series data: {len(complete_trends_df)} periods")
    print(f"📊 Date range: {complete_trends_df['date'].min().strftime('%Y-%m')} to {complete_trends_df['date'].max().strftime('%Y-%m')}")
    print(f"📈 Total postings across all periods: {complete_trends_df['posting_count'].sum():,}")
    
    # Additional seasonal analysis
    seasonal_analysis_query = """
    SELECT 
        posting_month,
        COUNT(*) as total_postings,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
        CASE 
            WHEN posting_month IN (12, 1, 2) THEN 'Winter'
            WHEN posting_month IN (3, 4, 5) THEN 'Spring'
            WHEN posting_month IN (6, 7, 8) THEN 'Summer'
            WHEN posting_month IN (9, 10, 11) THEN 'Fall'
        END as season
    FROM jobs 
    WHERE posting_month IS NOT NULL
    GROUP BY posting_month
    ORDER BY posting_month;
    """
    
    seasonal_df = pd.read_sql(seasonal_analysis_query, engine)
    print("\n🌟 Seasonal Posting Patterns:")
    print(seasonal_df.to_string(index=False))
    
    # Create time trends visualization
    print("\n" + "=" * 50)
    print("📈 Creating Time Trends Visualization...")
    
    plt.figure(figsize=(14, 8))
    
    # Line chart for time trends
    plt.plot(complete_trends_df['date'], complete_trends_df['posting_count'], 
             marker='o', linewidth=2.5, markersize=6, color='#2E86AB', alpha=0.8)
    
    plt.title('Job Posting Volume Trends Over Time', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Time Period', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Job Postings', fontsize=12, fontweight='bold')
    
    # Format x-axis
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add trend line
    if len(complete_trends_df) > 1:
        z = np.polyfit(range(len(complete_trends_df)), complete_trends_df['posting_count'], 1)
        p = np.poly1d(z)
        plt.plot(complete_trends_df['date'], p(range(len(complete_trends_df))), 
                 "--", alpha=0.7, color='red', linewidth=2, label='Trend Line')
        plt.legend()
    
    # Improve layout
    plt.tight_layout()
    
    # Save the chart
    chart_path = charts_dir / 'time_trends.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Time trends chart saved to: {chart_path}")
    
    # Calculate key metrics for insights
    print("\n" + "=" * 50)
    print("💡 Business Insights - Time Trends Analysis")
    print("=" * 50)
    
    total_postings = complete_trends_df['posting_count'].sum()
    avg_monthly_postings = complete_trends_df['posting_count'].mean()
    peak_month = complete_trends_df.loc[complete_trends_df['posting_count'].idxmax()]
    lowest_month = complete_trends_df.loc[complete_trends_df['posting_count'].idxmin()]
    
    # Calculate trend direction if we have enough data
    if len(complete_trends_df) > 1:
        z = np.polyfit(range(len(complete_trends_df)), complete_trends_df['posting_count'], 1)
        trend_slope = z[0]
        trend_direction = "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable"
    else:
        trend_direction = "insufficient data"
    
    print("🔍 KEY INSIGHTS:")
    print(f"• Peak hiring month: {peak_month['year_month']} with {peak_month['posting_count']:,} postings")
    print(f"• Lowest activity month: {lowest_month['year_month']} with {lowest_month['posting_count']:,} postings")
    print(f"• Average monthly postings: {avg_monthly_postings:,.0f}")
    print(f"• Overall trend: {trend_direction} over the analyzed period")
    
    # Seasonal insights
    seasonal_summary = seasonal_df.groupby('season')['total_postings'].sum().sort_values(ascending=False)
    print(f"• Most active season: {seasonal_summary.index[0]} with {seasonal_summary.iloc[0]:,} total postings")
    print(f"• Least active season: {seasonal_summary.index[-1]} with {seasonal_summary.iloc[-1]:,} total postings")
    
    # Calculate volatility
    volatility = complete_trends_df['posting_count'].std() / avg_monthly_postings * 100
    print(f"• Market volatility: {volatility:.1f}% (coefficient of variation)")
    
    # Create final summary table
    print("\n" + "=" * 50)
    print("📊 Final Time Trends Analysis Summary")
    print("=" * 50)
    print("📈 Top 10 Months by Posting Volume:")
    print(time_trends_df.to_string(index=False))
    
    print("\n🎯 BUSINESS INSIGHTS SUMMARY:")
    print("The time trends analysis reveals significant seasonal patterns in job posting activity.")
    print(f"Peak hiring occurs in {peak_month['year_month']} with {peak_month['posting_count']:,} postings, while the lowest activity is in {lowest_month['year_month']} with {lowest_month['posting_count']:,} postings.")
    print(f"The {seasonal_summary.index[0].lower()} season shows the highest hiring activity, suggesting companies align recruitment with business cycles and budget planning periods.")
    
    # Close database connection
    engine.dispose()
    print("\n✅ Analysis complete. Database connection closed.")
    print("📊 Time trends analysis has been completed successfully!")

if __name__ == "__main__":
    main()