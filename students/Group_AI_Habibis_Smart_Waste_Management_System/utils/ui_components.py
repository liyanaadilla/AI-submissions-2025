import streamlit as st
import json

def get_js_animation_html(city, routes, scanned_nodes=None, baseline_routes=None, show_status=True, classifications=None, allocated_bin_ids=None, reasoning_results=None, current_step=0):
    """
    Generates a high-fidelity "Command Center" map visualization.
    Refined for Loop 2: HUD, Iconic Nodes, and A* Path "Floor" Lighting.
    
    Args:
        reasoning_results: List of ReasoningResult objects for Reason phase visualization
                          (GREEN, ORANGE, GREY classification)
    """
    # 1. SERIALIZE DATA
    grid_size = city.grid_size
    depot = city.depot
    
    # Map classifications for easy lookup
    class_map = {}
    if classifications:
        for c in classifications:
            class_map[c.bin_id] = c
    
    # Map reasoning results for easy lookup
    reasoning_map = {}
    if reasoning_results:
        for r in reasoning_results:
            reasoning_map[r.bin_id] = r

    # Bins Data
    bins_data = []
    for b in city.bins.values():
        critical_threshold = b.max_capacity * 0.8 if hasattr(b, 'max_capacity') else 80
        is_critical = (b.fill_level >= critical_threshold) if show_status else False
        urgent_threshold = b.max_capacity * 0.7 if hasattr(b, 'max_capacity') else 70
        eta_status = ("URGENT" if b.fill_level > urgent_threshold else "STABLE") if show_status else "STABLE"
        
        visual_state = 'normal'
        block_reason = ''
        
        # Priority 1: Allocation Phase (Show only allocated bins)
        if allocated_bin_ids is not None:
            if b.bin_id in allocated_bin_ids:
                visual_state = 'eligible' # Green
            else:
                visual_state = 'irrelevant' # Grey out others
                is_critical = False # Suppress red pulse for non-allocated bins
        
        # Priority 2: Reason Phase (Show GREEN/ORANGE/GREY classification)
        elif reasoning_results:
            r = reasoning_map.get(b.bin_id)
            if r:
                # Import here to avoid circular import issues
                from modules.reasoning import ReasoningStatus
                if r.status == ReasoningStatus.GREEN:
                    visual_state = 'eligible'
                elif r.status == ReasoningStatus.ORANGE:
                    visual_state = 'blocked'
                    block_reason = r.block_reason
                else:  # GREY
                    visual_state = 'irrelevant'
                    is_critical = False
                
        # Priority 3: Predict Phase (Show predicted bins as red/critical)
        elif classifications:
            c = class_map.get(b.bin_id)
            if c:
                if c.is_full or c.is_urgent:
                    # Show predicted bins as critical (red)
                    visual_state = 'predicted'
                    is_critical = True
                else:
                    visual_state = 'normal'
                    is_critical = False

        bins_data.append({
            "id": b.bin_id,
            "x": b.position[0],
            "y": b.position[1],
            "fill": b.fill_level,
            "is_full": b.is_full,
            "is_critical": is_critical,
            "eta_status": eta_status,
            "visual_state": visual_state,
            "block_reason": block_reason
        })
        
    # Route Data & A* Metadata
    safe_routes = {}
    truck_targets = {} # Map truck_id -> first target bin
    
    if routes:
        for tid, path in routes.items():
            # Convert tuples to lists
            safe_routes[str(tid)] = [list(p) for p in path]
            
            # Find first non-depot target for HUD
            # Logic: simplistic - just find the first node that is a bin
            for p in path:
                # If p matches any bin location
                for b in bins_data:
                    if b['x'] == p[0] and b['y'] == p[1]:
                        truck_targets[str(tid)] = b['id']
                        break
                if str(tid) in truck_targets: break
            
            if str(tid) not in truck_targets:
                truck_targets[str(tid)] = "DEPOT"

    # Baseline Routes
    safe_baseline = {}
    if baseline_routes:
        for tid, path in baseline_routes.items():
            safe_baseline[str(tid)] = [list(p) for p in path]

    # Max frames
    max_frames = 0
    for path in safe_routes.values():
        max_frames = max(max_frames, len(path))
    if max_frames == 0: max_frames = 1

    data_json = json.dumps({
        "grid_size": grid_size,
        "bins": bins_data,
        "depot": list(depot),
        "routes": safe_routes,
        "baseline_routes": safe_baseline,
        "targets": truck_targets,
        "max_frames": max_frames,
        "initial_trucks": list(city.trucks.keys()),
        "scanned_nodes": scanned_nodes or [],
        "current_step": current_step
    })

    # 2. LOAD HTML TEMPLATE
    try:
        with open("assets/map.html", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        return "<div>Error: assets/map.html not found</div>"

    # 3. INJECT DATA
    # We replace the JS placeholder with the actual JSON string
    html = template.replace("__DATA_JSON__", data_json)
    
    return html

def render_decision_feed(decision_log):
    """
    Renders the decision feed with clean cards.
    """
    if not decision_log:
        st.markdown('<div style="text-align: center; color: #8b949e; padding: 20px;">No activity yet</div>', unsafe_allow_html=True)
        return
    
    # Actual render logic below
def render_decision_feed(decision_log):
    """
    Renders the decision feed using the Enterprise Cobalt design system.
    """
    if not decision_log:
        st.markdown('''
        <div style="text-align: center; padding: 40px; border: 1px dashed var(--border-subtle); border-radius: var(--radius-md);">
            <div style="font-size: 20px; margin-bottom: 8px; opacity: 0.4;">📡</div>
            <div style="color: var(--text-secondary); font-size: 13px;">Waiting for activity...</div>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="feed-container" style="display: flex; flex-direction: column; gap: 0;">', unsafe_allow_html=True)

    for log in reversed(decision_log):
        phase = log.get('phase', 'INFO')
        ltype = log.get('type', 'msg')
        
        # Phase Styles
        phase_config = {
            "SENSE": {"class": "status-info", "label": "SENSE"},
            "PREDICT": {"class": "status-warning", "label": "PREDICT"},
            "REASON": {"class": "status-danger", "label": "REASON"},
            "ALLOCATE": {"class": "status-info", "label": "ALLOCATE"},
            "PLAN": {"class": "status-success", "label": "PLAN"},
            "EXECUTE": {"class": "status-success", "label": "EXECUTE"},
            "ADAPT": {"class": "status-info", "label": "ADAPT"},
            "CYCLE": {"class": "status-info", "label": "CYCLE"},
        }
        
        config = phase_config.get(phase, {"class": "status-info", "label": phase})
        status_class = config["class"]
        
        # Render Summary Card
        if ltype == 'summary':
            metrics_html = ""
            for k, v in log.get('metrics', {}).items():
                metrics_html += f'<span style="background: var(--bg-card); padding: 4px 10px; border-radius: 4px; font-size: 11px; color: var(--text-secondary); border: 1px solid rgba(255,255,255,0.05);">{k}: <b style="color: var(--text-primary);">{v}</b></span>'

            st.markdown(f"""
            <div class="feed-item">
                <div class="feed-marker active"></div>
                <div style="background: var(--bg-panel); border: var(--border-subtle); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <span class="status-pill {status_class}" style="font-size: 10px;">{config['label']}</span>
                        <span style="font-size: 10px; color: var(--text-tertiary); font-family: var(--font-mono);">#{id(log)%1000:03d}</span>
                    </div>
                    <div style="font-size: 13px; color: var(--text-primary); margin-bottom: 12px; line-height: 1.5;">
                        {log.get('msg')}
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        {metrics_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Render Detail Card
        elif ltype == 'detail':
            tags_html = ' '.join([f'<span style="font-size: 10px; font-weight: 500; padding: 2px 6px; border-radius: 3px; background: var(--bg-hover); color: var(--text-secondary);">{t}</span>' for t in log.get('tags', [])])
            
            st.markdown(f"""
            <div class="feed-item">
                <div class="feed-marker"></div>
                <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.03); border-radius: var(--radius-md); padding: 12px; margin-left: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                        <span style="font-size: 12px; font-weight: 500; color: var(--text-primary);">{log.get('title')}</span>
                        <div style="display: flex; gap: 4px;">
                            {tags_html}
                        </div>
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary); font-family: var(--font-mono); white-space: pre-wrap;">{log.get('msg')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
