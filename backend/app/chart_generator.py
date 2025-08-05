"""
Chart generation service for PDF export functionality.
Creates matplotlib charts that match the frontend dashboard styling.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side generation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
from typing import List, Dict, Any
from datetime import datetime, date
from collections import Counter, defaultdict
import calendar

from .models import Asset

# Color scheme matching frontend dashboard
COLORS = {
    'primary': '#3b82f6',       # Blue (main brand color)
    'success': '#10b981',       # Green (active status)
    'warning': '#f59e0b',       # Orange (pending)
    'danger': '#ef4444',        # Red (error/retired)
    'info': '#06b6d4',          # Cyan (info)
    'purple': '#8b5cf6',        # Purple (stock)
    'gray': '#6b7280',          # Gray (default)
    'dark': '#1f2937',          # Dark gray (text)
}

# Status colors matching frontend StatusPieChart component
STATUS_COLORS = {
    'active': '#10b981',
    'damaged': '#641E16',
    'stock': '#3498DB',
    'disposed': '#ef4444',
    'pending rebuild': '#DC7633',
    'pre-disposal': '#808b96',
    'allocated': '#2c3e50',
    'broken': '#808b96',
    'lost': '#808b96',
    'repair': '#808b96',
    'stolen': '#808b96'
}

# Chart style configuration
plt.style.use('default')


class ChartGenerator:
    """Generate charts for PDF export matching frontend styling."""
    
    def __init__(self, dpi: int = 300, figsize: tuple = (10, 6)):
        """
        Initialize chart generator.
        
        Args:
            dpi: Chart resolution for PDF
            figsize: Default figure size (width, height) in inches
        """
        self.dpi = dpi
        self.figsize = figsize
        
    def generate_category_chart(self, assets: List[Asset]) -> BytesIO:
        """
        Generate bar chart showing asset count by category.
        Matches frontend AssetChart component.
        """
        # Group data by category
        category_counts = Counter()
        for asset in assets:
            category = (asset.category or 'Unknown').title()
            category_counts[category] += 1
        
        if not category_counts:
            return self._generate_empty_chart("No category data available")
        
        # Prepare data for plotting
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bars = ax.bar(categories, counts, color=COLORS['primary'], alpha=0.8)
        
        # Styling to match frontend
        ax.set_title('Assets by Category', fontsize=16, fontweight='bold', 
                    color=COLORS['dark'], pad=20)
        ax.set_xlabel('Category', fontsize=12, color=COLORS['dark'])
        ax.set_ylabel('Asset Count', fontsize=12, color=COLORS['dark'])
        
        # Grid styling
        ax.grid(True, linestyle='--', alpha=0.3, color=COLORS['gray'])
        ax.set_axisbelow(True)
        
        # Rotate x-axis labels if too many categories
        if len(categories) > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(COLORS['gray'])
        ax.spines['bottom'].set_color(COLORS['gray'])
        
        plt.tight_layout()
        
        return self._save_chart_to_buffer(fig)
    
    def generate_status_pie_chart(self, assets: List[Asset]) -> BytesIO:
        """
        Generate pie chart showing status distribution.
        Matches frontend StatusPieChart component.
        """
        # Filter to match dashboard (Active, Stock, Pending Rebuild only)
        filtered_assets = [a for a in assets if a.status in ['Active', 'Stock', 'Pending Rebuild']]
        
        # Group data by status
        status_counts = Counter()
        for asset in filtered_assets:
            status = (asset.status or 'Unknown').lower()
            status_counts[status] += 1
        
        if not status_counts:
            return self._generate_empty_chart("No status data available")
        
        # Prepare data
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        colors = [STATUS_COLORS.get(status, COLORS['gray']) for status in statuses]
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create pie chart with donut style (matches frontend)
        pie_parts = ax.pie(
            counts, 
            labels=[s.title() for s in statuses],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,  # Move percentage labels outward
            wedgeprops=dict(width=0.4)  # Create donut hole
        )
        _, texts, autotexts = pie_parts  # type: ignore
        
        # Styling
        ax.set_title('Status Distribution', fontsize=16, fontweight='bold', 
                    color=COLORS['dark'], pad=20)
        
        # Style the text
        for text in texts:
            text.set_fontsize(10)
            text.set_color(COLORS['dark'])
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        plt.tight_layout()
        
        return self._save_chart_to_buffer(fig)
    
    def generate_trends_chart(self, assets: List[Asset]) -> BytesIO:
        """
        Generate area chart showing monthly asset trends by status.
        Matches frontend TrendChart component.
        """
        # Filter to match dashboard (Active, Stock, Pending Rebuild only)
        filtered_assets = [a for a in assets if a.status in ['Active', 'Stock', 'Pending Rebuild']]
        
        # Group assets by month and status
        monthly_data = defaultdict(lambda: {'active': 0, 'pending': 0, 'stock': 0})
        
        for asset in filtered_assets:
            if not asset.created_at:
                continue
                
            try:
                # Parse the created_at date
                if isinstance(asset.created_at, str):
                    created_date = datetime.fromisoformat(asset.created_at.replace('Z', '+00:00'))
                else:
                    created_date = asset.created_at
                
                month_key = created_date.strftime('%Y-%m')
                month_label = created_date.strftime('%b %Y')
                
                # Categorize status
                status = (asset.status or '').lower()
                if 'active' in status:
                    monthly_data[month_key]['active'] += 1
                elif 'pending' in status and 'rebuild' in status:
                    monthly_data[month_key]['pending'] += 1
                elif 'stock' in status:
                    monthly_data[month_key]['stock'] += 1
                    
            except (ValueError, AttributeError):
                continue
        
        if not monthly_data:
            return self._generate_empty_chart("No trend data available")
        
        # Sort by month and prepare data
        sorted_months = sorted(monthly_data.keys())
        months = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months]
        
        active_counts = [monthly_data[m]['active'] for m in sorted_months]
        pending_counts = [monthly_data[m]['pending'] for m in sorted_months]
        stock_counts = [monthly_data[m]['stock'] for m in sorted_months]
        
        # Create chart
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create stacked area chart
        ax.fill_between(range(len(months)), stock_counts, 
                       color=COLORS['purple'], alpha=0.9, label='Stock')
        
        ax.fill_between(range(len(months)), stock_counts, 
                       [s + p for s, p in zip(stock_counts, pending_counts)],
                       color=COLORS['warning'], alpha=0.9, label='Pending Rebuild')
        
        ax.fill_between(range(len(months)), 
                       [s + p for s, p in zip(stock_counts, pending_counts)],
                       [s + p + a for s, p, a in zip(stock_counts, pending_counts, active_counts)],
                       color=COLORS['success'], alpha=0.9, label='Active')
        
        # Styling
        ax.set_title('Monthly Asset Trends', fontsize=16, fontweight='bold', 
                    color=COLORS['dark'], pad=20)
        ax.set_xlabel('Month', fontsize=12, color=COLORS['dark'])
        ax.set_ylabel('Asset Count', fontsize=12, color=COLORS['dark'])
        
        # X-axis labels - reduce density for readability
        ax.set_xticks(range(len(months)))
        if len(months) > 6:
            # Show every 3rd month if more than 6 months
            labels = [months[i] if i % 3 == 0 else '' for i in range(len(months))]
            ax.set_xticklabels(labels, rotation=45, ha='right')
        else:
            ax.set_xticklabels(months, rotation=45, ha='right')
        
        # Grid and spines
        ax.grid(True, linestyle='--', alpha=0.3, color=COLORS['gray'])
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Legend
        ax.legend(loc='upper left', frameon=False)
        
        plt.tight_layout()
        
        return self._save_chart_to_buffer(fig)
    
    def generate_warranty_expiration_chart(self, assets: List[Asset]) -> BytesIO:
        """
        Generate bar chart showing warranty expiration trends.
        Matches frontend LaptopExpirationChart component.
        """
        # Filter for laptops with warranty expiration dates
        laptop_assets = [a for a in assets if a.category and 'laptop' in a.category.lower()]
        
        # Group by quarter and model
        quarterly_data = defaultdict(lambda: defaultdict(int))
        
        for asset in laptop_assets:
            if not asset.warranty_expires:
                continue
                
            try:
                # Parse warranty expiration date
                if isinstance(asset.warranty_expires, str):
                    exp_date = datetime.strptime(asset.warranty_expires, '%Y-%m-%d').date()
                else:
                    exp_date = asset.warranty_expires
                
                # Get quarter
                quarter = f"Q{((exp_date.month - 1) // 3) + 1} {exp_date.year}"
                
                # Get model key
                manufacturer = (asset.manufacturer or '').lower()
                model = asset.model or 'Unknown'
                
                if 'apple' in manufacturer:
                    model_key = 'Apple'
                elif 'lenovo' in manufacturer:
                    model_key = f"Lenovo - {model}"
                else:
                    model_key = model
                
                quarterly_data[quarter][model_key] += 1
                
            except (ValueError, AttributeError):
                continue
        
        if not quarterly_data:
            return self._generate_empty_chart("No warranty expiration data available")
        
        # Prepare data for plotting
        quarters = sorted(quarterly_data.keys(), 
                         key=lambda q: (int(q.split()[1]), int(q[1])))
        all_models = set()
        for quarter_data in quarterly_data.values():
            all_models.update(quarter_data.keys())
        all_models = sorted(all_models)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Generate colors for different models
        model_colors = {}
        color_list = [COLORS['primary'], COLORS['success'], COLORS['warning'], 
                     COLORS['danger'], COLORS['info'], COLORS['purple']]
        for i, model in enumerate(all_models):
            model_colors[model] = color_list[i % len(color_list)]
        
        # Create grouped bar chart
        x = range(len(quarters))
        bar_width = 0.15
        
        for i, model in enumerate(all_models):
            values = [quarterly_data[q].get(model, 0) for q in quarters]
            offset = (i - len(all_models)/2 + 0.5) * bar_width
            bars = ax.bar([xi + offset for xi in x], values, bar_width, 
                         label=model, color=model_colors[model], alpha=0.8)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        # Styling
        ax.set_title('Warranty Expiration Trends', fontsize=16, fontweight='bold', 
                    color=COLORS['dark'], pad=20)
        ax.set_xlabel('Quarter', fontsize=12, color=COLORS['dark'])
        ax.set_ylabel('Expiring Assets', fontsize=12, color=COLORS['dark'])
        
        # X-axis labels - reduce density for readability
        ax.set_xticks(x)
        if len(quarters) > 4:
            # Show every other quarter if more than 4 quarters
            labels = [quarters[i] if i % 2 == 0 else '' for i in range(len(quarters))]
            ax.set_xticklabels(labels, rotation=45, ha='right')
        else:
            ax.set_xticklabels(quarters, rotation=45, ha='right')
        
        # Grid and styling
        ax.grid(True, linestyle='--', alpha=0.3, color=COLORS['gray'])
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Legend
        if all_models:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
        
        plt.tight_layout()
        
        return self._save_chart_to_buffer(fig)
    
    def _generate_empty_chart(self, message: str) -> BytesIO:
        """Generate a simple chart with a message for empty data."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.text(0.5, 0.5, message, ha='center', va='center', 
               fontsize=14, color=COLORS['gray'], 
               transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        return self._save_chart_to_buffer(fig)
    
    def _save_chart_to_buffer(self, fig) -> BytesIO:
        """Save matplotlib figure to BytesIO buffer."""
        buffer = BytesIO()
        try:
            fig.savefig(buffer, format='png', dpi=self.dpi, 
                       bbox_inches='tight', facecolor='white', 
                       edgecolor='none', pad_inches=0.2)
            buffer.seek(0)
        finally:
            plt.close(fig)  # Always free memory
            plt.clf()       # Clear the current figure
            # Force garbage collection for matplotlib objects
            import gc
            gc.collect()
        return buffer 