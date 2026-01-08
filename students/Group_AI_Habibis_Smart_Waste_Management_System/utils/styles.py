import streamlit as st

def apply_custom_css():
    """
    Enterprise Cobalt Design System.
    Focus: Professional, minimal, readable, information-dense.
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

        /* ============================================================
         * DESIGN TOKENS - Enterprise Cobalt
         * ============================================================ */
        :root {
            /* Core Backgrounds */
            --bg-app: #0f172a;       /* Slate 950 */
            --bg-panel: #1e293b;     /* Slate 800 */
            --bg-card: #252e3e;      /* Custom Slate */
            --bg-hover: #334155;     /* Slate 700 */
            
            /* Borders */
            --border-subtle: 1px solid rgba(255, 255, 255, 0.06);
            --border-hover: 1px solid rgba(255, 255, 255, 0.15);
            --radius-md: 6px;
            --radius-lg: 12px;
            
            /* Functional Colors */
            --primary: #6366f1;      /* Indigo 500 */
            --primary-hover: #4f46e5;/* Indigo 600 */
            --primary-dim: rgba(99, 102, 241, 0.15);
            
            --success: #10b981;      /* Emerald 500 */
            --success-bg: rgba(16, 185, 129, 0.15);
            --warning: #f59e0b;      /* Amber 500 */
            --warning-bg: rgba(245, 158, 11, 0.15);
            --danger: #ef4444;       /* Red 500 */
            --danger-bg: rgba(239, 68, 68, 0.15);
            --info: #3b82f6;         /* Blue 500 */
            --info-bg: rgba(59, 130, 246, 0.15);

            /* Typography */
            --font-sans: 'Inter', -apple-system, system-ui, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --text-primary: #f8fafc; /* Slate 50 */
            --text-secondary: #94a3b8; /* Slate 400 */
            --text-tertiary: #64748b; /* Slate 500 */
        }

        /* ============================================================
         * BASE STYLES
         * ============================================================ */
        .stApp {
            background-color: var(--bg-app);
            color: var(--text-primary);
            font-family: var(--font-sans);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary);
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        .stMarkdown p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Hide Streamlit chrome */
        #MainMenu, header, footer { visibility: hidden; }

        /* ============================================================
         * COMPONENTS
         * ============================================================ */
        
        /* Glass/Panel Card */
        .glass-card {
            background: var(--bg-panel);
            border: var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Data Metric Box */
        .metric-box {
            background: var(--bg-panel);
            border: var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-box:hover {
            border: var(--border-hover);
            transform: translateY(-1px);
        }
        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-tertiary);
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            font-feature-settings: "tnum";
            font-variant-numeric: tabular-nums;
        }
        .metric-delta {
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        /* Status Pills */
        .status-pill {
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            border-radius: 99px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .status-success { background: var(--success-bg); color: var(--success); }
        .status-warning { background: var(--warning-bg); color: var(--warning); }
        .status-danger { background: var(--danger-bg); color: var(--danger); }
        .status-info { background: var(--info-bg); color: var(--info); }

        /* Timeline/Feed Items */
        .feed-item {
            position: relative;
            padding-left: 20px;
            border-left: 2px solid var(--bg-hover);
            padding-bottom: 20px;
        }
        .feed-item:last-child { border-left-color: transparent; }
        .feed-marker {
            position: absolute;
            left: -6px;
            top: 0;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--bg-hover);
            border: 2px solid var(--bg-app);
        }
        .feed-marker.active { background: var(--primary); }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-app); /* Matches main app for seamless look, or make slightly darker */
            border-right: var(--border-subtle);
        }
        /* Keep sidebar always visible by hiding the collapse control */
        button[data-testid="stSidebarCollapseButton"] {
            display: none;
        }
        
        /* Buttons */
        .stButton button {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--text-primary);
            border-radius: var(--radius-md);
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.2);
        }
        .stButton button[kind="primary"] {
            background: var(--primary);
            border-color: var(--primary);
            color: white;
            box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
        }
        .stButton button[kind="primary"]:hover {
            background: var(--primary-hover);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: 1px solid var(--bg-hover);
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 6px 6px 0 0;
            background: transparent;
            color: var(--text-secondary);
            border: none;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: var(--bg-panel);
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
        }

    </style>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_color="normal"):
    """
    Renders a custom metric card using HTML/CSS.
    """
    delta_html = ""
    if delta:
        color_class = ""
        if delta_color == "normal":
             # Auto-detect roughly
             if isinstance(delta, str) and "-" in delta: color_class = "text-red-400" 
             else: color_class = "text-green-400"
        
        # Simple styled delta
        color = "var(--success)" if ("+" in str(delta) or "↑" in str(delta) or not "-" in str(delta)) else "var(--danger)"
        delta_html = f'<span class="metric-delta" style="color: {color}">{delta}</span>'

    st.markdown(f"""
<div class="metric-box">
<span class="metric-label">{label}</span>
<div style="display: flex; align-items: baseline; justify-content: space-between;">
<span class="metric-value">{value}</span>
{delta_html}
</div>
</div>
""", unsafe_allow_html=True)
