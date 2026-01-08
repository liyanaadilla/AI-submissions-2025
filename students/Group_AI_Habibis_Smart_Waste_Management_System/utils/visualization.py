"""
Visualization Utilities for Smart Waste Management System

This module provides visualization functions for:
- City map with bins, trucks, and routes
- KPI charts and comparisons
- Interactive elements for Streamlit

Uses matplotlib for static visualizations that integrate well with Streamlit.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import numpy as np
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# Color scheme
COLORS = {
    'depot': '#2E86AB',        # Blue
    'bin_normal': '#A4C639',   # Green
    'bin_full': '#E94F37',     # Red
    'bin_urgent': '#F39C12',   # Orange
    'bin_eligible': '#9B59B6', # Purple
    'bin_collected': '#95A5A6', # Gray
    'truck_colors': ['#3498DB', '#E74C3C', '#2ECC71', '#9B59B6', '#F39C12'],
    'road': '#BDC3C7',
    'road_closed': '#E74C3C',
    'background': '#ECF0F1'
}


def draw_city_map(city, classifications: List = None, 
                  route_results: List = None,
                  figsize: Tuple[int, int] = (10, 10)) -> plt.Figure:
    """
    Draw the city map with bins, trucks, and routes.
    
    Args:
        city: City object from simulation
        classifications: List of RuleResult objects for bin coloring
        route_results: List of RouteResult objects for route drawing
        figsize: Figure size in inches
    
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    
    # Set up grid
    grid_size = city.grid_size
    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(-0.5, grid_size - 0.5)
    ax.set_aspect('equal')
    ax.set_facecolor(COLORS['background'])
    
    # Draw grid lines (roads)
    for i in range(grid_size):
        ax.axhline(y=i, color=COLORS['road'], linewidth=0.5, alpha=0.5)
        ax.axvline(x=i, color=COLORS['road'], linewidth=0.5, alpha=0.5)
    
    # Draw road edges
    for u, v in city.graph.edges():
        x_coords = [u[0], v[0]]
        y_coords = [u[1], v[1]]
        
        edge_data = city.graph[u][v]
        if edge_data.get('closed', False):
            ax.plot(x_coords, y_coords, color=COLORS['road_closed'], 
                   linewidth=3, alpha=0.8, linestyle='--')
        else:
            ax.plot(x_coords, y_coords, color=COLORS['road'], 
                   linewidth=1, alpha=0.3)
    
    # Draw closed roads with X mark
    for node1, node2 in city.closed_roads:
        mid_x = (node1[0] + node2[0]) / 2
        mid_y = (node1[1] + node2[1]) / 2
        ax.scatter(mid_x, mid_y, marker='x', s=100, c='red', zorder=5)
    
    # Draw routes if provided
    if route_results:
        for i, route in enumerate(route_results):
            if route.path and len(route.path) > 1:
                color = COLORS['truck_colors'][i % len(COLORS['truck_colors'])]
                path = route.path
                
                # Draw path as lines with arrows
                for j in range(len(path) - 1):
                    x_coords = [path[j][0], path[j+1][0]]
                    y_coords = [path[j][1], path[j+1][1]]
                    ax.annotate('', xy=(path[j+1][0], path[j+1][1]), 
                               xytext=(path[j][0], path[j][1]),
                               arrowprops=dict(arrowstyle='->', color=color, 
                                             lw=2, alpha=0.7))
    
    # Build classification lookup
    class_lookup = {}
    if classifications:
        for c in classifications:
            class_lookup[c.bin_id] = c
    
    # Draw bins
    for bin_id, bin_obj in city.bins.items():
        x, y = bin_obj.position
        
        # Determine color based on classification
        if bin_id in class_lookup:
            c = class_lookup[bin_id]
            if c.status.value == 'Collected':
                color = COLORS['bin_collected']
            elif c.is_eligible:
                color = COLORS['bin_eligible']
            elif c.is_full:
                color = COLORS['bin_full']
            elif c.is_urgent:
                color = COLORS['bin_urgent']
            else:
                color = COLORS['bin_normal']
        else:
            # Color based on fill level (use max_capacity if available)
            max_cap = bin_obj.max_capacity if hasattr(bin_obj, 'max_capacity') else 100
            if bin_obj.fill_level >= max_cap * 0.8:
                color = COLORS['bin_full']
            elif bin_obj.fill_level >= max_cap * 0.6:
                color = COLORS['bin_urgent']
            else:
                color = COLORS['bin_normal']
        
        # Draw bin as circle with fill level indicator
        circle = plt.Circle((x, y), 0.3, color=color, alpha=0.8, zorder=10)
        ax.add_patch(circle)
        
        # Add fill level text
        ax.annotate(f'{bin_obj.fill_level:.0f}%', (x, y), 
                   ha='center', va='center', fontsize=7, 
                   color='white', fontweight='bold', zorder=11)
    
    # Draw depot
    depot_x, depot_y = city.depot
    depot_marker = plt.Rectangle((depot_x - 0.35, depot_y - 0.35), 0.7, 0.7,
                                  color=COLORS['depot'], zorder=12)
    ax.add_patch(depot_marker)
    ax.annotate('DEPOT', (depot_x, depot_y), ha='center', va='center',
               fontsize=6, color='white', fontweight='bold', zorder=13)
    
    # Draw trucks
    for truck_id, truck in city.trucks.items():
        x, y = truck.position
        color = COLORS['truck_colors'][truck_id % len(COLORS['truck_colors'])]
        
        # Draw truck as triangle
        triangle = plt.Polygon([
            (x - 0.2, y - 0.2),
            (x + 0.2, y - 0.2),
            (x, y + 0.3)
        ], color=color, zorder=15)
        ax.add_patch(triangle)
        ax.annotate(f'T{truck_id}', (x, y + 0.45), ha='center', va='bottom',
                   fontsize=8, color=color, fontweight='bold', zorder=16)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color=COLORS['depot'], label='Depot'),
        mpatches.Patch(color=COLORS['bin_normal'], label='Normal Bin'),
        mpatches.Patch(color=COLORS['bin_full'], label='Full Bin (≥80%)'),
        mpatches.Patch(color=COLORS['bin_urgent'], label='Urgent Bin'),
        mpatches.Patch(color=COLORS['bin_eligible'], label='Eligible (to collect)'),
        mpatches.Patch(color=COLORS['bin_collected'], label='Collected'),
        plt.Line2D([0], [0], marker='x', color='red', linestyle='', 
                   markersize=10, label='Road Closed'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)
    
    # Labels
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('City Map - Smart Waste Management System')
    
    plt.tight_layout()
    return fig


def draw_kpi_comparison_chart(ai_kpis: Dict, baseline_kpis: Dict) -> go.Figure:
    """
    Create a comparison chart of AI vs Baseline KPIs.
    
    Args:
        ai_kpis: Dictionary of AI mode KPIs
        baseline_kpis: Dictionary of Baseline mode KPIs
    
    Returns:
        Plotly Figure object
    """
    metrics = ['overflow_count', 'total_distance', 'collections_made', 'sla_violations']
    display_names = ['Overflows', 'Distance', 'Collections', 'SLA Violations']
    
    ai_values = [ai_kpis.get(m, 0) for m in metrics]
    baseline_values = [baseline_kpis.get(m, 0) for m in metrics]
    
    fig = go.Figure(data=[
        go.Bar(name='AI Mode', x=display_names, y=ai_values, 
               marker_color='#3498DB'),
        go.Bar(name='Baseline', x=display_names, y=baseline_values, 
               marker_color='#E74C3C')
    ])
    
    fig.update_layout(
        barmode='group',
        title='AI vs Baseline Performance Comparison',
        xaxis_title='Metric',
        yaxis_title='Value',
        legend=dict(x=0.7, y=0.95),
        template='plotly_white',
        height=400
    )
    
    return fig


def draw_kpi_dashboard(kpis: Dict) -> go.Figure:
    """
    Create a KPI dashboard with gauges and indicators.
    
    Args:
        kpis: Dictionary of current KPIs
    
    Returns:
        Plotly Figure object
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Overflow Count', 'Total Distance', 
                       'SLA Compliance', 'Collections Made'],
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'indicator'}, {'type': 'indicator'}]]
    )
    
    # Overflow count (lower is better)
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=kpis.get('overflow_count', 0),
        title={'text': 'Overflows'},
        delta={'reference': 5, 'relative': False, 'increasing': {'color': 'red'}},
        domain={'row': 0, 'column': 0}
    ), row=1, col=1)
    
    # Total distance
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('total_distance', 0),
        title={'text': 'Distance'},
        number={'suffix': ' units'},
        domain={'row': 0, 'column': 1}
    ), row=1, col=2)
    
    # SLA Compliance (gauge)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=kpis.get('sla_compliance_rate', 100),
        title={'text': 'SLA %'},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#2ECC71'},
            'steps': [
                {'range': [0, 50], 'color': '#E74C3C'},
                {'range': [50, 80], 'color': '#F39C12'},
                {'range': [80, 100], 'color': '#A4C639'}
            ]
        },
        domain={'row': 1, 'column': 0}
    ), row=2, col=1)
    
    # Collections made
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('collections_made', 0),
        title={'text': 'Collections'},
        domain={'row': 1, 'column': 1}
    ), row=2, col=2)
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        title_text='KPI Dashboard'
    )
    
    return fig


def draw_bin_status_pie(classifications: List) -> go.Figure:
    """
    Create a pie chart showing bin status distribution.
    
    Args:
        classifications: List of RuleResult objects
    
    Returns:
        Plotly Figure object
    """
    if not classifications:
        return go.Figure()
    
    status_counts = {}
    for c in classifications:
        status = c.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    
    color_map = {
        'Normal': COLORS['bin_normal'],
        'Full': COLORS['bin_full'],
        'Urgent': COLORS['bin_urgent'],
        'Eligible': COLORS['bin_eligible'],
        'Collected': COLORS['bin_collected']
    }
    colors = [color_map.get(l, '#95A5A6') for l in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        marker=dict(colors=colors),
        hole=0.4
    )])
    
    fig.update_layout(
        title='Bin Status Distribution',
        height=350,
        template='plotly_white'
    )
    
    return fig


def draw_fill_level_histogram(bins: Dict) -> go.Figure:
    """
    Create a histogram of bin fill levels.
    
    Args:
        bins: Dictionary of bin_id -> WasteBin objects
    
    Returns:
        Plotly Figure object
    """
    fill_levels = [b.fill_level for b in bins.values()]
    
    fig = go.Figure(data=[go.Histogram(
        x=fill_levels,
        nbinsx=10,
        marker_color='#3498DB',
        opacity=0.75
    )])
    
    fig.add_vline(x=80, line_dash="dash", line_color="red", 
                  annotation_text="Full threshold (80%)")
    
    fig.update_layout(
        title='Bin Fill Level Distribution',
        xaxis_title='Fill Level (%)',
        yaxis_title='Number of Bins',
        height=300,
        template='plotly_white'
    )
    
    return fig


def format_eta_table(predictions: List) -> List[Dict]:
    """
    Format predictions for display in a table.
    
    Args:
        predictions: List of PredictionResult objects
    
    Returns:
        List of dictionaries for table display
    """
    table_data = []
    
    for p in predictions:
        eta_display = f"{p.eta_minutes:.0f} min" if p.eta_minutes != float('inf') else "∞"
        
        # Urgency indicator
        if p.eta_minutes <= 60:
            urgency = "🔴 Critical"
        elif p.eta_minutes <= 120:
            urgency = "🟠 Urgent"
        elif p.eta_minutes <= 240:
            urgency = "🟡 Watch"
        else:
            urgency = "🟢 Normal"
        
        table_data.append({
            'Bin ID': p.bin_id,
            'Fill Level': f"{p.current_fill:.1f}%",
            'Fill Rate': f"{p.fill_rate:.2f}%/step",
            'ETA': eta_display,
            'Urgency': urgency
        })
    
    return table_data


def format_classification_table(classifications: List) -> List[Dict]:
    """
    Format rule classifications for display.
    
    Args:
        classifications: List of RuleResult objects
    
    Returns:
        List of dictionaries for table display
    """
    table_data = []
    
    for c in classifications:
        table_data.append({
            'Bin ID': c.bin_id,
            'Full (≥80%)': '✓' if c.is_full else '',
            'Urgent (≤120min)': '✓' if c.is_urgent else '',
            'Eligible': '✓' if c.is_eligible else '',
            'Status': c.status.value
        })
    
    return table_data


def format_auction_table(allocations: List) -> List[Dict]:
    """
    Format auction results for display.
    
    Args:
        allocations: List of AllocationResult objects
    
    Returns:
        List of dictionaries for table display
    """
    table_data = []
    
    for a in allocations:
        all_bids_str = ", ".join([
            f"T{b.truck_id}:{b.bid_value:.1f}" 
            for b in a.all_bids
        ])
        
        table_data.append({
            'Bin ID': a.bin_id,
            'Winner': f"Truck {a.truck_id}",
            'Winning Bid': f"{a.winning_bid:.2f}",
            'All Bids': all_bids_str
        })
    
    return table_data
