# Visualization Utilities for Wuzzuf Job Market Analysis
# Standardized visualization functions with consistent styling

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class WuzzufVisualizer:
    """
    Standardized visualization class for Wuzzuf Job Market Analysis
    Provides consistent styling and reusable chart generation functions
    """
    
    def __init__(self, charts_dir='../assets/charts'):
        """Initialize visualizer with chart output directory"""
        self.charts_dir = Path(charts_dir)
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Set consistent styling
        self._setup_styling()
        
    def _setup_styling(self):
        """Configure consistent styling for all visualizations"""
        # Matplotlib/Seaborn styling
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Custom color palette
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'accent': '#F18F01',
            'success': '#C73E1D',
            'info': '#6A994E',
            'warning': '#F77F00',
            'light': '#F8F9FA',
            'dark': '#212529'
        }
        
        # Chart styling parameters
        self.style_params = {
            'figure_size': (12, 8),
            'title_size': 16,
            'label_size': 12,
            'tick_size': 10,
            'legend_size': 10,
            'dpi': 300,
            'bbox_inches': 'tight'
        }
        
    def create_bar_chart(self, data, x_col, y_col, title, filename, 
                        orientation='vertical', top_n=10, color_col=None):
        """
        Create standardized bar chart
        
        Args:
            data: DataFrame with data to plot
            x_col: Column name for x-axis
            y_col: Column name for y-axis  
            title: Chart title
            filename: Output filename (without extension)
            orientation: 'vertical' or 'horizontal'
            top_n: Number of top items to display
            color_col: Column to use for color coding
        """
        # Limit to top N items
        plot_data = data.head(top_n).copy()
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.style_params['figure_size'])
        
        if orientation == 'horizontal':
            # Horizontal bar chart
            bars = ax.barh(plot_data[x_col], plot_data[y_col], 
                          color=self.colors['primary'], alpha=0.8)
            ax.set_xlabel(y_col.replace('_', ' ').title(), 
                         fontsize=self.style_params['label_size'])
            ax.set_ylabel(x_col.replace('_', ' ').title(), 
                         fontsize=self.style_params['label_size'])
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + max(plot_data[y_col]) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{width:,.0f}', ha='left', va='center', 
                       fontsize=self.style_params['tick_size'])
        else:
            # Vertical bar chart
            bars = ax.bar(plot_data[x_col], plot_data[y_col], 
                         color=self.colors['primary'], alpha=0.8)
            ax.set_xlabel(x_col.replace('_', ' ').title(), 
                         fontsize=self.style_params['label_size'])
            ax.set_ylabel(y_col.replace('_', ' ').title(), 
                         fontsize=self.style_params['label_size'])
            
            # Rotate x-axis labels if needed
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(plot_data[y_col]) * 0.01,
                       f'{height:,.0f}', ha='center', va='bottom', 
                       fontsize=self.style_params['tick_size'])
        
        # Styling
        ax.set_title(title, fontsize=self.style_params['title_size'], fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(self.charts_dir / f'{filename}.png', 
                   dpi=self.style_params['dpi'], 
                   bbox_inches=self.style_params['bbox_inches'])
        plt.close()
        
        print(f"✅ Bar chart saved: {filename}.png")
        
    def create_donut_chart(self, data, labels_col, values_col, title, filename, top_n=10):
        """
        Create standardized donut chart
        
        Args:
            data: DataFrame with data to plot
            labels_col: Column name for labels
            values_col: Column name for values
            title: Chart title
            filename: Output filename (without extension)
            top_n: Number of top items to display
        """
        # Limit to top N items and group others
        plot_data = data.head(top_n).copy()
        
        if len(data) > top_n:
            others_sum = data.iloc[top_n:][values_col].sum()
            others_row = pd.DataFrame({labels_col: ['Others'], values_col: [others_sum]})
            plot_data = pd.concat([plot_data, others_row], ignore_index=True)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.style_params['figure_size'])
        
        # Create donut chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
        wedges, texts, autotexts = ax.pie(plot_data[values_col], 
                                         labels=plot_data[labels_col],
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         pctdistance=0.85,
                                         startangle=90)
        
        # Create donut hole
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        
        # Styling
        ax.set_title(title, fontsize=self.style_params['title_size'], fontweight='bold', pad=20)
        
        # Adjust text properties
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(self.style_params['tick_size'])
            autotext.set_weight('bold')
            
        # Save chart
        plt.tight_layout()
        plt.savefig(self.charts_dir / f'{filename}.png', 
                   dpi=self.style_params['dpi'], 
                   bbox_inches=self.style_params['bbox_inches'])
        plt.close()
        
        print(f"✅ Donut chart saved: {filename}.png")
        
    def create_line_chart(self, data, x_col, y_col, title, filename, 
                         x_label=None, y_label=None, trend_line=False):
        """
        Create standardized line chart
        
        Args:
            data: DataFrame with data to plot
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Chart title
            filename: Output filename (without extension)
            x_label: Custom x-axis label
            y_label: Custom y-axis label
            trend_line: Whether to add trend line
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.style_params['figure_size'])
        
        # Create line chart
        ax.plot(data[x_col], data[y_col], 
               color=self.colors['primary'], linewidth=3, marker='o', markersize=8)
        
        # Add trend line if requested
        if trend_line and len(data) > 2:
            z = np.polyfit(range(len(data)), data[y_col], 1)
            p = np.poly1d(z)
            ax.plot(data[x_col], p(range(len(data))), 
                   color=self.colors['secondary'], linestyle='--', alpha=0.7, linewidth=2)
        
        # Styling
        ax.set_xlabel(x_label or x_col.replace('_', ' ').title(), 
                     fontsize=self.style_params['label_size'])
        ax.set_ylabel(y_label or y_col.replace('_', ' ').title(), 
                     fontsize=self.style_params['label_size'])
        ax.set_title(title, fontsize=self.style_params['title_size'], fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Rotate x-axis labels if needed
        plt.xticks(rotation=45, ha='right')
        
        # Save chart
        plt.tight_layout()
        plt.savefig(self.charts_dir / f'{filename}.png', 
                   dpi=self.style_params['dpi'], 
                   bbox_inches=self.style_params['bbox_inches'])
        plt.close()
        
        print(f"✅ Line chart saved: {filename}.png")
        
    def create_grouped_bar_chart(self, data, x_col, y_cols, title, filename, 
                                x_label=None, y_label=None):
        """
        Create standardized grouped bar chart
        
        Args:
            data: DataFrame with data to plot
            x_col: Column name for x-axis (categories)
            y_cols: List of column names for y-axis (multiple series)
            title: Chart title
            filename: Output filename (without extension)
            x_label: Custom x-axis label
            y_label: Custom y-axis label
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.style_params['figure_size'])
        
        # Set up bar positions
        x_pos = np.arange(len(data))
        bar_width = 0.8 / len(y_cols)
        
        # Create bars for each series
        colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        for i, col in enumerate(y_cols):
            ax.bar(x_pos + i * bar_width, data[col], bar_width, 
                  label=col.replace('_', ' ').title(), 
                  color=colors[i % len(colors)], alpha=0.8)
        
        # Styling
        ax.set_xlabel(x_label or x_col.replace('_', ' ').title(), 
                     fontsize=self.style_params['label_size'])
        ax.set_ylabel(y_label or 'Values', 
                     fontsize=self.style_params['label_size'])
        ax.set_title(title, fontsize=self.style_params['title_size'], fontweight='bold', pad=20)
        ax.set_xticks(x_pos + bar_width * (len(y_cols) - 1) / 2)
        ax.set_xticklabels(data[x_col], rotation=45, ha='right')
        ax.legend(fontsize=self.style_params['legend_size'])
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(self.charts_dir / f'{filename}.png', 
                   dpi=self.style_params['dpi'], 
                   bbox_inches=self.style_params['bbox_inches'])
        plt.close()
        
        print(f"✅ Grouped bar chart saved: {filename}.png")
        
    def create_heatmap(self, data, title, filename, annot=True, cmap='Blues'):
        """
        Create standardized heatmap
        
        Args:
            data: DataFrame or 2D array for heatmap
            title: Chart title
            filename: Output filename (without extension)
            annot: Whether to annotate cells with values
            cmap: Color map to use
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.style_params['figure_size'])
        
        # Create heatmap
        sns.heatmap(data, annot=annot, cmap=cmap, ax=ax, 
                   cbar_kws={'shrink': 0.8}, fmt='.0f' if annot else None)
        
        # Styling
        ax.set_title(title, fontsize=self.style_params['title_size'], fontweight='bold', pad=20)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(self.charts_dir / f'{filename}.png', 
                   dpi=self.style_params['dpi'], 
                   bbox_inches=self.style_params['bbox_inches'])
        plt.close()
        
        print(f"✅ Heatmap saved: {filename}.png")
        
    def create_summary_dashboard(self, charts_info, title="Wuzzuf Job Market Analysis Dashboard"):
        """
        Create a summary dashboard combining multiple charts
        
        Args:
            charts_info: List of dictionaries with chart information
            title: Dashboard title
        """
        # This would create a combined dashboard - placeholder for now
        print(f"📊 Dashboard creation functionality ready for: {title}")
        print(f"   Charts to include: {len(charts_info)} visualizations")
        
    def get_chart_path(self, filename):
        """Get full path to saved chart"""
        return self.charts_dir / f'{filename}.png'
        
    def list_saved_charts(self):
        """List all saved charts"""
        charts = list(self.charts_dir.glob('*.png'))
        print(f"📈 Saved charts ({len(charts)}):")
        for chart in sorted(charts):
            print(f"   - {chart.name}")
        return charts

# Convenience functions for quick chart creation
def create_business_question_charts(db_engine, charts_dir='../assets/charts'):
    """
    Generate all 6 business question charts using standardized functions
    
    Args:
        db_engine: SQLAlchemy database engine
        charts_dir: Directory to save charts
    """
    visualizer = WuzzufVisualizer(charts_dir)
    
    print("🎨 Generating standardized business question charts...")
    print("=" * 60)
    
    # 1. Top Roles and Industries Analysis
    print("\n1️⃣ Creating Top Roles and Industries Charts...")
    
    # Top roles query
    top_roles_query = """
    SELECT 
        job_title,
        COUNT(*) as posting_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
    FROM jobs 
    WHERE job_title IS NOT NULL AND job_title != ''
    GROUP BY job_title 
    ORDER BY posting_count DESC 
    LIMIT 10;
    """
    
    top_roles_df = pd.read_sql(top_roles_query, db_engine)
    visualizer.create_bar_chart(
        data=top_roles_df,
        x_col='job_title',
        y_col='posting_count',
        title='Top 10 Job Titles by Posting Count',
        filename='top_roles_industries',
        orientation='horizontal'
    )
    
    # 2. Skills Demand Analysis
    print("\n2️⃣ Creating Skills Demand Chart...")
    
    skills_query = """
    SELECT 
        s.skill_name,
        COUNT(js.job_id) as demand_count,
        ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 2) as percentage
    FROM skills s
    JOIN job_skills js ON s.skill_id = js.skill_id
    GROUP BY s.skill_id, s.skill_name
    ORDER BY demand_count DESC
    LIMIT 10;
    """
    
    skills_df = pd.read_sql(skills_query, db_engine)
    visualizer.create_bar_chart(
        data=skills_df,
        x_col='skill_name',
        y_col='demand_count',
        title='Top 10 Skills in Demand',
        filename='skills_demand',
        orientation='horizontal'
    )
    
    # 3. Experience Distribution
    print("\n3️⃣ Creating Experience Distribution Chart...")
    
    experience_query = """
    SELECT 
        experience_level,
        COUNT(*) as posting_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs WHERE experience_level IS NOT NULL), 2) as percentage
    FROM jobs 
    WHERE experience_level IS NOT NULL AND experience_level != ''
    GROUP BY experience_level 
    ORDER BY posting_count DESC;
    """
    
    experience_df = pd.read_sql(experience_query, db_engine)
    visualizer.create_donut_chart(
        data=experience_df,
        labels_col='experience_level',
        values_col='posting_count',
        title='Job Postings by Experience Level',
        filename='experience_distribution'
    )
    
    # 4. Salary Insights
    print("\n4️⃣ Creating Salary Insights Chart...")
    
    salary_query = """
    SELECT 
        experience_level,
        ROUND(AVG(salary_min), 0) as avg_min_salary,
        ROUND(AVG(salary_max), 0) as avg_max_salary,
        COUNT(*) as job_count
    FROM jobs 
    WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL 
        AND experience_level IS NOT NULL AND experience_level != ''
    GROUP BY experience_level 
    ORDER BY avg_min_salary DESC;
    """
    
    salary_df = pd.read_sql(salary_query, db_engine)
    if not salary_df.empty:
        visualizer.create_grouped_bar_chart(
            data=salary_df,
            x_col='experience_level',
            y_cols=['avg_min_salary', 'avg_max_salary'],
            title='Average Salary by Experience Level',
            filename='salary_insights',
            y_label='Average Salary'
        )
    
    # 5. Location Trends
    print("\n5️⃣ Creating Location Trends Chart...")
    
    location_query = """
    SELECT 
        COALESCE(city, 'Unknown') as city,
        COUNT(*) as posting_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) as percentage
    FROM jobs 
    GROUP BY city 
    ORDER BY posting_count DESC 
    LIMIT 10;
    """
    
    location_df = pd.read_sql(location_query, db_engine)
    visualizer.create_bar_chart(
        data=location_df,
        x_col='city',
        y_col='posting_count',
        title='Top 10 Cities by Job Postings',
        filename='location_trends',
        orientation='horizontal'
    )
    
    # 6. Time Trends
    print("\n6️⃣ Creating Time Trends Chart...")
    
    time_query = """
    SELECT 
        posting_year,
        posting_month,
        COUNT(*) as posting_count,
        posting_year || '-' || LPAD(posting_month::text, 2, '0') as year_month
    FROM jobs 
    WHERE posting_year IS NOT NULL AND posting_month IS NOT NULL
    GROUP BY posting_year, posting_month 
    ORDER BY posting_year, posting_month;
    """
    
    time_df = pd.read_sql(time_query, db_engine)
    if not time_df.empty:
        visualizer.create_line_chart(
            data=time_df,
            x_col='year_month',
            y_col='posting_count',
            title='Monthly Job Posting Trends Over Time',
            filename='time_trends',
            x_label='Month',
            y_label='Number of Postings',
            trend_line=True
        )
    
    print("\n" + "=" * 60)
    print("✅ All standardized charts generated successfully!")
    
    # List all saved charts
    visualizer.list_saved_charts()
    
    return visualizer

# Example usage and testing functions
if __name__ == "__main__":
    # This would be used for testing the visualization functions
    print("🎨 Wuzzuf Visualization Utils - Ready for use!")
    print("Import this module and use WuzzufVisualizer class or convenience functions")