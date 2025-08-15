# Chart Styling Configuration for Wuzzuf Job Market Analysis
# Centralized styling parameters for consistent branding across all visualizations

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

class WuzzufChartStyle:
    """
    Centralized chart styling configuration for consistent branding
    """
    
    # Color Palette - Professional and accessible
    COLORS = {
        'primary': '#2E86AB',      # Professional blue
        'secondary': '#A23B72',    # Deep magenta
        'accent': '#F18F01',       # Warm orange
        'success': '#6A994E',      # Forest green
        'warning': '#F77F00',      # Bright orange
        'danger': '#C73E1D',       # Deep red
        'light': '#F8F9FA',        # Light gray
        'dark': '#212529',         # Dark gray
        'muted': '#6C757D'         # Muted gray
    }
    
    # Extended color palette for multi-series charts
    PALETTE = [
        '#2E86AB', '#A23B72', '#F18F01', '#6A994E', 
        '#F77F00', '#C73E1D', '#8E44AD', '#16A085',
        '#E67E22', '#E74C3C', '#3498DB', '#2ECC71'
    ]
    
    # Typography settings
    FONTS = {
        'title_size': 16,
        'subtitle_size': 14,
        'label_size': 12,
        'tick_size': 10,
        'legend_size': 10,
        'annotation_size': 9
    }
    
    # Figure settings
    FIGURE = {
        'size': (12, 8),
        'dpi': 300,
        'facecolor': 'white',
        'edgecolor': 'none'
    }
    
    # Layout settings
    LAYOUT = {
        'bbox_inches': 'tight',
        'pad_inches': 0.2,
        'transparent': False
    }
    
    # Grid and axis settings
    GRID = {
        'alpha': 0.3,
        'linestyle': '-',
        'linewidth': 0.5,
        'color': '#CCCCCC'
    }
    
    # Chart-specific settings
    BAR_CHART = {
        'alpha': 0.8,
        'edgecolor': 'white',
        'linewidth': 0.5
    }
    
    LINE_CHART = {
        'linewidth': 3,
        'marker': 'o',
        'markersize': 8,
        'alpha': 0.9
    }
    
    PIE_CHART = {
        'startangle': 90,
        'autopct': '%1.1f%%',
        'pctdistance': 0.85,
        'explode_max': 0.05
    }
    
    @classmethod
    def apply_style(cls):
        """Apply global matplotlib styling"""
        # Set matplotlib parameters
        rcParams.update({
            'figure.figsize': cls.FIGURE['size'],
            'figure.dpi': cls.FIGURE['dpi'],
            'figure.facecolor': cls.FIGURE['facecolor'],
            'figure.edgecolor': cls.FIGURE['edgecolor'],
            
            'font.size': cls.FONTS['label_size'],
            'axes.titlesize': cls.FONTS['title_size'],
            'axes.labelsize': cls.FONTS['label_size'],
            'xtick.labelsize': cls.FONTS['tick_size'],
            'ytick.labelsize': cls.FONTS['tick_size'],
            'legend.fontsize': cls.FONTS['legend_size'],
            
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.spines.left': True,
            'axes.spines.bottom': True,
            'axes.linewidth': 0.8,
            'axes.edgecolor': cls.COLORS['muted'],
            
            'grid.alpha': cls.GRID['alpha'],
            'grid.linestyle': cls.GRID['linestyle'],
            'grid.linewidth': cls.GRID['linewidth'],
            'grid.color': cls.GRID['color'],
            
            'savefig.bbox': cls.LAYOUT['bbox_inches'],
            'savefig.pad_inches': cls.LAYOUT['pad_inches'],
            'savefig.transparent': cls.LAYOUT['transparent'],
            'savefig.dpi': cls.FIGURE['dpi']
        })
        
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette(cls.PALETTE)
        
    @classmethod
    def get_color_palette(cls, n_colors=None):
        """Get color palette for charts"""
        if n_colors is None:
            return cls.PALETTE
        return cls.PALETTE[:n_colors] if n_colors <= len(cls.PALETTE) else cls.PALETTE * (n_colors // len(cls.PALETTE) + 1)
    
    @classmethod
    def format_axis_labels(cls, ax, x_label=None, y_label=None, title=None):
        """Apply consistent axis formatting"""
        if title:
            ax.set_title(title, fontsize=cls.FONTS['title_size'], 
                        fontweight='bold', pad=20, color=cls.COLORS['dark'])
        
        if x_label:
            ax.set_xlabel(x_label, fontsize=cls.FONTS['label_size'], 
                         color=cls.COLORS['dark'])
        
        if y_label:
            ax.set_ylabel(y_label, fontsize=cls.FONTS['label_size'], 
                         color=cls.COLORS['dark'])
        
        # Format tick labels
        ax.tick_params(axis='both', which='major', 
                      labelsize=cls.FONTS['tick_size'],
                      colors=cls.COLORS['muted'])
        
        # Add grid
        ax.grid(True, **cls.GRID)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(cls.COLORS['muted'])
        ax.spines['bottom'].set_color(cls.COLORS['muted'])
    
    @classmethod
    def add_value_labels(cls, ax, bars, format_string='{:,.0f}', offset_factor=0.01):
        """Add value labels to bar charts"""
        for bar in bars:
            if hasattr(bar, 'get_height'):  # Vertical bars
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., 
                       height + ax.get_ylim()[1] * offset_factor,
                       format_string.format(height), 
                       ha='center', va='bottom',
                       fontsize=cls.FONTS['annotation_size'],
                       color=cls.COLORS['dark'])
            else:  # Horizontal bars
                width = bar.get_width()
                ax.text(width + ax.get_xlim()[1] * offset_factor,
                       bar.get_y() + bar.get_height()/2,
                       format_string.format(width),
                       ha='left', va='center',
                       fontsize=cls.FONTS['annotation_size'],
                       color=cls.COLORS['dark'])

# Chart templates for specific business questions
CHART_TEMPLATES = {
    'top_roles': {
        'title': 'Top 10 Job Titles by Posting Count',
        'x_label': 'Job Title',
        'y_label': 'Number of Postings',
        'orientation': 'horizontal',
        'color': WuzzufChartStyle.COLORS['primary']
    },
    
    'skills_demand': {
        'title': 'Top 10 Skills in Demand',
        'x_label': 'Skill Name', 
        'y_label': 'Demand Count',
        'orientation': 'horizontal',
        'color': WuzzufChartStyle.COLORS['secondary']
    },
    
    'experience_distribution': {
        'title': 'Job Postings by Experience Level',
        'chart_type': 'donut',
        'colors': WuzzufChartStyle.get_color_palette(5)
    },
    
    'salary_insights': {
        'title': 'Average Salary by Experience Level',
        'x_label': 'Experience Level',
        'y_label': 'Average Salary',
        'chart_type': 'grouped_bar',
        'colors': [WuzzufChartStyle.COLORS['primary'], WuzzufChartStyle.COLORS['accent']]
    },
    
    'location_trends': {
        'title': 'Top 10 Cities by Job Postings',
        'x_label': 'City',
        'y_label': 'Number of Postings', 
        'orientation': 'horizontal',
        'color': WuzzufChartStyle.COLORS['success']
    },
    
    'time_trends': {
        'title': 'Monthly Job Posting Trends Over Time',
        'x_label': 'Month (YYYY-MM)',
        'y_label': 'Number of Postings',
        'chart_type': 'line',
        'color': WuzzufChartStyle.COLORS['primary'],
        'trend_color': WuzzufChartStyle.COLORS['secondary']
    }
}

# Export styling function for easy import
def apply_wuzzuf_style():
    """Apply Wuzzuf chart styling globally"""
    WuzzufChartStyle.apply_style()
    print("✅ Wuzzuf chart styling applied successfully")

if __name__ == "__main__":
    # Test the styling configuration
    print("🎨 Wuzzuf Chart Style Configuration")
    print("=" * 40)
    print(f"Primary Color: {WuzzufChartStyle.COLORS['primary']}")
    print(f"Color Palette: {len(WuzzufChartStyle.PALETTE)} colors")
    print(f"Figure Size: {WuzzufChartStyle.FIGURE['size']}")
    print(f"DPI: {WuzzufChartStyle.FIGURE['dpi']}")
    print(f"Chart Templates: {len(CHART_TEMPLATES)} templates")
    print("✅ Configuration loaded successfully")