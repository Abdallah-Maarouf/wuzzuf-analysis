#!/usr/bin/env python3
"""
Time Trends Analysis Script
Executes the time trends analysis and generates required deliverables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os
from pathlib import Path
from datetime import datetime

# Add sql directory to path for database utilities
sys.path.append('sql')
from database_setup import DatabaseManager

# Configure display and warnings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette('husl')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def main():
    print("=== Time Trends Analysis ===")
    print("Analyzing temporal patterns in job postings...")
    
    # Set up paths
    charts_dir = Path('assets/charts')
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Charts will be saved to: {charts_dir.absolute()}")
    
    # Database connection
    try:
        db_manager = DatabaseManager()
        engine = db_manager.get_engine()
        print("✅ Connected to PostgreSQL database")
        
        # Test connection
        status = db_manager.test_connection()
        print(f"Database: {status['database']}")
        print(f"Tables available: {status['table_count']}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        # SQL query for monthly posting volume trends (max 10 rows as required)
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
        
        print("\n=== SQL Query for Time Trends Analysis ===")
        print(time_trends_query)
        
        # Execute query and get results
        time_trends_df = pd.read_sql_query(time_trends_query, engine)
        
        print(f"\n=== Time Trends Analysis Results ===")
        print(f"Total periods analyzed: {len(time_trends_df)}")
        print("\nTop 10 months by posting volume:")
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
        
        complete_trends_df = pd.read_sql_query(complete_trends_query, engine)
        
        # Create a proper date column for plotting
        complete_trends_df['date'] = pd.to_datetime(
            complete_trends_df[['posting_year', 'posting_month']].assign(day=1)
        )
        complete_trends_df['year_month'] = complete_trends_df['date'].dt.strftime('%Y-%m')
        
        print(f"\nComplete time series data: {len(complete_trends_df)} periods")
        print(f"Date range: {complete_trends_df['date'].min()} to {complete_trends_df['date'].max()}")
        
        # Create time trends visualization
        plt.figure(figsize=(14, 8))
        
        # Line chart for time trends
        plt.plot(complete_trends_df['date'], complete_trends_df['posting_count'], 
                 marker='o', linewidth=2, markersize=6, color='#2E86AB')
        
        plt.title('Job Posting Volume Trends Over Time', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Time Period', fontsize=12)
        plt.ylabel('Number of Job Postings', fontsize=12)
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(range(len(complete_trends_df)), complete_trends_df['posting_count'], 1)
        p = np.poly1d(z)
        plt.plot(complete_trends_df['date'], p(range(len(complete_trends_df))), 
                 "--", alpha=0.7, color='red', label='Trend Line')
        
        plt.legend()
        plt.tight_layout()
        
        # Save the chart
        chart_path = charts_dir / 'time_trends.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Time trends chart saved to {chart_path}")
        
        # Additional seasonal analysis
        seasonal_analysis_query = """
        SELECT 
            posting_month,
            COUNT(*) as total_postings,
            ROUND(AVG(COUNT(*)) OVER(), 0) as avg_monthly_postings,
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
        
        seasonal_df = pd.read_sql_query(seasonal_analysis_query, engine)
        print("\n=== Seasonal Posting Patterns ===")
        print(seasonal_df.to_string(index=False))
        
        # Calculate key metrics for insights
        total_postings = complete_trends_df['posting_count'].sum()
        avg_monthly_postings = complete_trends_df['posting_count'].mean()
        peak_month = complete_trends_df.loc[complete_trends_df['posting_count'].idxmax()]
        lowest_month = complete_trends_df.loc[complete_trends_df['posting_count'].idxmin()]
        
        # Calculate trend direction
        trend_slope = z[0]  # From the trend line calculation above
        trend_direction = "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable"
        
        print("\n=== KEY BUSINESS INSIGHTS ===")
        print(f"• Peak hiring month: {peak_month['year_month']} with {peak_month['posting_count']:,} postings")
        print(f"• Lowest activity month: {lowest_month['year_month']} with {lowest_month['posting_count']:,} postings")
        print(f"• Average monthly postings: {avg_monthly_postings:,.0f}")
        print(f"• Overall trend: {trend_direction} over the analyzed period")
        
        # Seasonal insights
        seasonal_summary = seasonal_df.groupby('season')['total_postings'].sum().sort_values(ascending=False)
        print(f"• Most active season: {seasonal_summary.index[0]} with {seasonal_summary.iloc[0]:,} total postings")
        print(f"• Least active season: {seasonal_summary.index[-1]} with {seasonal_summary.iloc[-1]:,} total postings")
        
        # Month-over-month analysis
        if len(complete_trends_df) > 1:
            complete_trends_df['mom_change'] = complete_trends_df['posting_count'].pct_change() * 100
            avg_mom_change = complete_trends_df['mom_change'].mean()
            print(f"• Average month-over-month change: {avg_mom_change:.1f}%")
            
            # Find biggest increases and decreases
            biggest_increase = complete_trends_df.loc[complete_trends_df['mom_change'].idxmax()]
            biggest_decrease = complete_trends_df.loc[complete_trends_df['mom_change'].idxmin()]
            
            if not pd.isna(biggest_increase['mom_change']):
                print(f"• Biggest month-over-month increase: {biggest_increase['year_month']} (+{biggest_increase['mom_change']:.1f}%)")
            if not pd.isna(biggest_decrease['mom_change']):
                print(f"• Biggest month-over-month decrease: {biggest_decrease['year_month']} ({biggest_decrease['mom_change']:.1f}%)")
        
        # Close database connection
        db_manager.close()
        print("\n✅ Analysis complete. Database connection closed.")
        
        return True
        
    except Exception as e:
      