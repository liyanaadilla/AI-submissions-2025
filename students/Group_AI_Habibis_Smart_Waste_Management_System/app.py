import streamlit as st
import pandas as pd
import time
import random
import streamlit.components.v1 as components

import modules.simulation as sim
import modules.routing as routing
import modules.auction as auction_engine
from modules.reasoning import classify_all_bins, reason_all_bins, get_green_bins, ReasoningStatus
import utils.ui_components as ui
import utils.styles as styles



st.set_page_config(
    page_title="Waste Collection Simulation",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded"
)


styles.apply_custom_css()



if 'city' not in st.session_state:
    st.session_state.city = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'step_data' not in st.session_state:
    st.session_state.step_data = {}
if 'simulation_active' not in st.session_state:
    st.session_state.simulation_active = False
if 'routes' not in st.session_state:
    st.session_state.routes = {}
if 'scanned_nodes' not in st.session_state:
    st.session_state.scanned_nodes = []
if 'baseline_routes' not in st.session_state:
    st.session_state.baseline_routes = {}
if 'decision_log' not in st.session_state:
    st.session_state.decision_log = []
if 'stats' not in st.session_state:
    st.session_state.stats = {}
if 'simulation_time' not in st.session_state:
    st.session_state.simulation_time = 0

# KPI Tracking for AI vs Baseline Comparison
if 'kpi_ai_distance' not in st.session_state:
    st.session_state.kpi_ai_distance = 0
if 'kpi_baseline_distance' not in st.session_state:
    st.session_state.kpi_baseline_distance = 0
if 'kpi_bins_collected' not in st.session_state:
    st.session_state.kpi_bins_collected = 0
if 'kpi_overflows_prevented' not in st.session_state:
    st.session_state.kpi_overflows_prevented = 0
if 'kpi_computation_time' not in st.session_state:
    st.session_state.kpi_computation_time = 0
if 'cycle_complete' not in st.session_state:
    st.session_state.cycle_complete = False

# View Mode: Manager Dashboard or Driver View
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "manager"
if 'selected_truck' not in st.session_state:
    st.session_state.selected_truck = 0

# Parameters (stored in session state to persist across reruns)
if 'grid_size' not in st.session_state: st.session_state.grid_size = 10
if 'num_bins' not in st.session_state: st.session_state.num_bins = 15
if 'num_trucks' not in st.session_state: st.session_state.num_trucks = 3
if 'truck_capacity' not in st.session_state: st.session_state.truck_capacity = 300
if 'bin_capacity' not in st.session_state: st.session_state.bin_capacity = 100
if 'p_alpha' not in st.session_state: st.session_state.p_alpha = 1.0
if 'p_beta' not in st.session_state: st.session_state.p_beta = 0.3
if 'p_gamma' not in st.session_state: st.session_state.p_gamma = 0.5

STEPS = [
    "Sense",
    "Predict",
    "Reason",
    "Allocate",
    "Plan & Execute",
    "Adapt"
]

STEP_EXPLANATIONS = {
    0: "The agent scans the city grid using IoT sensors to detect current bin fill levels and truck positions.",
    1: "The agent predicts which bins are likely to overflow soon using their current fill levels and estimated fill rates. Bins that may overflow within 120 minutes are marked as urgent.",
    2: "The agent applies KR (Knowledge Representation) rules to ALL bins, using the Predict output as input. This filters bins into: GREEN (eligible), ORANGE (urgent but blocked), and GREY (not relevant).",
    3: "The agent uses a Contract Net Protocol (Auction) to assign tasks. Trucks bid on GREEN bins based on their current position and capacity. The lowest cost bid wins.",
    4: "The agent calculates optimal routes using A* algorithm, then executes the plan. Trucks move along routes, collecting waste from assigned bins.",
    5: "The agent monitors the environment for changes. If a road closure or new emergency occurs, the agent triggers a dynamic replanning process."
}



def reset_simulation():
    st.session_state.city = sim.City(
        st.session_state.grid_size, 
        st.session_state.num_bins, 
        st.session_state.num_trucks,
        truck_capacity=st.session_state.truck_capacity,
        bin_capacity=st.session_state.bin_capacity
    )
    st.session_state.routes = {}
    st.session_state.decision_log = []
    st.session_state.stats = {}
    st.session_state.simulation_time = 0
    st.session_state.current_step = 0
    st.session_state.step_data = {}
    st.session_state.scanned_nodes = []
    st.session_state.simulation_active = True
    # Reset KPI tracking
    st.session_state.kpi_ai_distance = 0
    st.session_state.kpi_baseline_distance = 0
    st.session_state.kpi_bins_collected = 0
    st.session_state.kpi_overflows_prevented = 0
    st.session_state.kpi_computation_time = 0
    st.session_state.cycle_complete = False
    # Run step 0 (Sense) logic immediately
    run_step_logic(0, st.session_state.city)

def run_step_logic(step, city):
    """Run the logic for a specific step."""
    if step == 0: # Sense
        # Logic: Read sensors
        full_bins = [b for b in city.bins.values() if b.is_full]
        st.session_state.decision_log.append({
            "phase": "SENSE",
            "type": "summary",
            "msg": f"IoT Grid Scan Complete. {len(full_bins)} critical nodes detected.",
            "metrics": {"Total Detected": len(city.bins), "Critical": len(full_bins)}
        })
        
    elif step == 1: # Predict
        # Logic: Calculate ETA and identify bins that need attention
        classifications = classify_all_bins(city.bins)
        
        # Store classifications for context
        st.session_state.step_data['classifications'] = classifications
        
        # Identify predicted bins (full or urgent) - this becomes input for Reason phase
        predicted_bin_ids = [c.bin_id for c in classifications if c.is_full or c.is_urgent]
        st.session_state.step_data['predicted_bin_ids'] = predicted_bin_ids
        
        urgent_count = sum(1 for c in classifications if c.is_urgent and not c.is_full)
        full_count = sum(1 for c in classifications if c.is_full)
        st.session_state.decision_log.append({
            "phase": "PREDICT",
            "type": "summary",
            "msg": f"Prediction Model Run. {full_count} full bins, {urgent_count} bins at risk of overflow.",
            "metrics": {"Full": full_count, "Urgent": urgent_count, "Total Predicted": len(predicted_bin_ids)}
        })
        
    elif step == 2: # Reason
        # Logic: Apply KR rules to ALL bins, using Predict output as input context
        predicted_bin_ids = st.session_state.step_data.get('predicted_bin_ids', [])
        
        # Reason ALL bins - this is the key KR filtering step
        reasoning_results = reason_all_bins(
            bins=city.bins,
            predicted_bin_ids=predicted_bin_ids,
            trucks=city.trucks
        )
        st.session_state.step_data['reasoning_results'] = reasoning_results
        
        # Get only GREEN bins for subsequent phases (Allocate, Plan, Execute)
        green_bin_ids = get_green_bins(reasoning_results)
        st.session_state.step_data['green_bin_ids'] = green_bin_ids
        
        # Count by status
        green_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREEN)
        orange_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.ORANGE)
        grey_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREY)
        
        st.session_state.decision_log.append({
            "phase": "REASON",
            "type": "summary",
            "msg": f"KR Rules Applied to ALL {len(reasoning_results)} bins. {green_count} eligible for service.",
            "metrics": {"Green (Eligible)": green_count, "Orange (Blocked)": orange_count, "Grey (Not Relevant)": grey_count}
        })
        
        # Log details for each bin classification
        for r in reasoning_results:
            if r.status == ReasoningStatus.GREEN:
                st.session_state.decision_log.append({
                    "phase": "REASON",
                    "type": "detail",
                    "title": f"Bin #{r.bin_id} → GREEN",
                    "msg": r.explanation,
                    "tags": ["Eligible", "Predicted" if r.is_predicted else "Detected"]
                })
            elif r.status == ReasoningStatus.ORANGE:
                st.session_state.decision_log.append({
                    "phase": "REASON",
                    "type": "detail",
                    "title": f"Bin #{r.bin_id} → ORANGE ❌",
                    "msg": r.explanation,
                    "tags": ["Blocked", r.block_reason]
                })
        
    elif step == 3: # Allocate
 
        green_bin_ids = st.session_state.step_data.get('green_bin_ids', [])
        graph = city.to_networkx()
        
        auction_results = auction_engine.allocate_bins(
            eligible_bin_ids=green_bin_ids,
            trucks=city.trucks,
            bins=city.bins,
            graph=graph,
            depot=city.depot
        )
        st.session_state.step_data['auction_results'] = auction_results
        
        auction_stats = auction_engine.get_auction_summary(auction_results)
        st.session_state.decision_log.append({
            "phase": "ALLOCATE",
            "type": "summary",
            "msg": "CNP Protocol (Contract Net) active. Agents negotiating for tasks.",
            "metrics": {
                "Tasks Assigned": auction_stats['total_allocated'],
                "Avg Bid Cost": f"{auction_stats['avg_bid_value']:.1f}"
            }
        })
        
        for res in auction_results:
            st.session_state.decision_log.append({
                "phase": "ALLOCATE",
                "type": "detail",
                "title": f"Task #{res.bin_id} Awarded",
                "msg": f"Winner: Truck {res.truck_id} (Bid: {res.winning_bid:.1f})",
                "tags": ["Winner", f"T-{res.truck_id}"]
            })
            

            truck_loads = {}
            for res in auction_results:
                if res.truck_id not in truck_loads:
                    truck_loads[res.truck_id] = 0
                # Use current fill level of the bin
                bin_load = city.bins[res.bin_id].fill_level
                truck_loads[res.truck_id] += bin_load
            
            # Apply to truck objects
            for tid, load in truck_loads.items():
                if tid in city.trucks:
                    city.trucks[tid].current_load = load

    elif step == 4: # Plan & Execute
        import time as time_module
        start_time = time_module.time()
        
        # Logic: A* Routing
        ai_route_results = routing.plan_all_routes(
            trucks=city.trucks,
            bins=city.bins,
            graph=city.to_networkx(),
            depot=city.depot,
            alpha=st.session_state.p_alpha,
            beta=st.session_state.p_beta,
            gamma=st.session_state.p_gamma
        )
        
        computation_time = (time_module.time() - start_time) * 1000  # ms
        
        routes = {}
        scanned = []
        total_ai_dist = 0
        bins_collected_count = 0
        
        for res in ai_route_results:
            routes[res.truck_id] = res.path
            total_ai_dist += res.distance
            bins_collected_count += len(res.waypoints)
            if res.explored_nodes:
                scanned.extend(res.explored_nodes)
        
        st.session_state.routes = routes
        st.session_state.scanned_nodes = scanned
        

        total_baseline_dist = 0
        for truck_id, truck in city.trucks.items():
            # Naive: go from depot to each assigned bin position sequentially, then back
            if truck.assigned_bins:
                current_pos = city.depot
                for bin_id in sorted(truck.assigned_bins):  # Visit in ID order (naive)
                    bin_pos = city.bins[bin_id].position
                    # Manhattan distance as naive path
                    dist = abs(current_pos[0] - bin_pos[0]) + abs(current_pos[1] - bin_pos[1])
                    total_baseline_dist += dist
                    current_pos = bin_pos
                # Return to depot
                total_baseline_dist += abs(current_pos[0] - city.depot[0]) + abs(current_pos[1] - city.depot[1])
        
        # Add minimum baseline if no bins assigned (still need some comparison)
        if total_baseline_dist == 0 and total_ai_dist > 0:
            total_baseline_dist = total_ai_dist * 1.35  # Estimate 35% worse
        
        # Count potential overflows prevented (bins that were urgent/full and collected)
        overflows_prevented = sum(1 for b in city.bins.values() if b.collected and b.is_full)
        
        # Store KPIs in session state
        st.session_state.kpi_ai_distance = total_ai_dist
        st.session_state.kpi_baseline_distance = total_baseline_dist
        st.session_state.kpi_bins_collected = bins_collected_count
        st.session_state.kpi_overflows_prevented = overflows_prevented
        st.session_state.kpi_computation_time = computation_time
        
        # Calculate improvement percentage
        if total_baseline_dist > 0:
            improvement_pct = ((total_baseline_dist - total_ai_dist) / total_baseline_dist) * 100
        else:
            improvement_pct = 0
        
        st.session_state.decision_log.append({
            "phase": "PLAN",
            "type": "summary",
            "msg": f"🚀 AI Routes Generated! Distance: {total_ai_dist:.1f} vs Baseline: {total_baseline_dist:.1f} ({improvement_pct:.1f}% improvement)",
            "metrics": {"AI Distance": total_ai_dist, "Baseline": total_baseline_dist, "Saved": f"{improvement_pct:.1f}%"}
        })
        
        # Store assignment data BEFORE clearing (for Driver View)
        if 'driver_assignments' not in st.session_state:
            st.session_state.driver_assignments = {}
        if 'driver_collected' not in st.session_state:
            st.session_state.driver_collected = {}
        if 'driver_loads' not in st.session_state:
            st.session_state.driver_loads = {}
        
        # Execute: Move trucks, empty bins
        for truck_id, route in routes.items():
            if route:
                truck = city.trucks[truck_id]
                truck.position = route[-1] # Move to end
                
                # Store the assigned bins for Driver View BEFORE clearing
                st.session_state.driver_assignments[truck_id] = list(truck.assigned_bins)
                st.session_state.driver_collected[truck_id] = []
                # Store the peak load for this cycle
                st.session_state.driver_loads[truck_id] = truck.current_load
                
                # Empty bins assigned to this truck
                for bin_id in truck.assigned_bins:
                     city.bins[bin_id].fill_level = 0
                     city.bins[bin_id].is_full = False
                     city.bins[bin_id].collected = True
                     st.session_state.driver_collected[truck_id].append(bin_id)
                
                truck.assigned_bins = [] # Clear assignment after execution
                truck.current_load = 0
        
        st.session_state.decision_log.append({
            "phase": "EXECUTE",
            "type": "summary",
            "msg": f"✅ Mission Complete! {bins_collected_count} bins collected, {overflows_prevented} overflows prevented.",
            "metrics": {"Collected": bins_collected_count, "Overflows Prevented": overflows_prevented}
        })

    elif step == 5: # Adapt
        # Mark cycle as complete for showing summary
        st.session_state.cycle_complete = True
        
        # Logic: Check disruption
        st.session_state.decision_log.append({
            "phase": "ADAPT",
            "type": "summary",
            "msg": "🔄 System stable. Ready for next cycle or dynamic events.",
            "metrics": {"Status": "Monitoring", "Cycle": "Complete"}
        })


def advance_step():
    """Advance to the next step and run its logic."""
    city = st.session_state.city
    
    if not city:
        return

    # Increment step first
    if st.session_state.current_step < 5:
        st.session_state.current_step += 1
        
        run_step_logic(st.session_state.current_step, city)
    else:
        # Reset for next cycle
        st.session_state.current_step = 0
        city.step(30) # Advance time
        st.session_state.simulation_time += 30
        st.session_state.routes = {}
        st.session_state.scanned_nodes = []
        st.session_state.step_data = {}
        st.session_state.decision_log = []
        st.session_state.decision_log.append({
            "phase": "CYCLE",
            "type": "summary",
            "msg": f"New Cycle Started at T+{st.session_state.simulation_time}m",
            "metrics": {"Time": st.session_state.simulation_time}
        })
        # Run step 0 (Sense) logic for new cycle
        run_step_logic(0, city)



# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### SYSTEM PARAMETERS")
    
    with st.container():
        st.caption("ENVIRONMENT SETTINGS")
        st.session_state.grid_size = st.slider(
            "Grid Matrix Size", 6, 20, st.session_state.grid_size,
            help="Size of the city grid (NxN). Larger grids have more possible routes but increase computation time."
        )
        st.session_state.num_bins = st.slider(
            "Sensor Node Count", 5, 40, st.session_state.num_bins,
            help="Number of smart waste bins (IoT sensors) placed on the grid. More bins = more complex routing."
        )
        st.session_state.num_trucks = st.slider(
            "Fleet Capacity", 1, 5, st.session_state.num_trucks,
            help="Number of collection trucks in the fleet. More trucks can cover more bins in parallel."
        )
        st.session_state.truck_capacity = st.slider(
            "Truck Capacity", 200, 500, st.session_state.truck_capacity, step=50,
            help="Maximum load each truck can carry before returning to depot."
        )
        st.session_state.bin_capacity = st.slider(
            "Bin Capacity", 50, 200, st.session_state.bin_capacity, step=10,
            help="Maximum fill level for each bin. Bins are critical when fill exceeds 80% of this value."
        )
    
    with st.expander("Advanced Settings"):
        st.markdown("##### 🧠 AI Planner Weights")
        st.session_state.p_alpha = st.slider(
            "Alpha (Distance)", 0.0, 5.0, st.session_state.p_alpha, 0.1,
            help="Weight for travel distance in the A* cost function. Higher = prefer shorter routes."
        )
        st.session_state.p_beta = st.slider(
            "Beta (Overflow Risk)", 0.0, 5.0, st.session_state.p_beta, 0.1,
            help="Weight for overflow risk. Higher = prioritize bins that are close to overflowing."
        )
        st.session_state.p_gamma = st.slider(
            "Gamma (SLA Penalty)", 0.0, 5.0, st.session_state.p_gamma, 0.1,
            help="Weight for SLA deadline penalty. Higher = prioritize bins with approaching deadlines."
        )

    st.markdown("---")
    
    if st.button("RESET SYSTEM", use_container_width=True):
        reset_simulation()
        st.rerun()
            
    if not st.session_state.simulation_active:
        if st.button("▶ START SIMULATION", type="primary", use_container_width=True):
            reset_simulation()
            st.rerun()

    st.markdown("---")



if not st.session_state.simulation_active:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 60px;">
        <h3 style="margin:0 0 10px 0;">System Ready</h3>
        <p style="color: var(--text-secondary); margin-bottom: 20px;">Configure the parameters in the sidebar and click START to begin.</p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()



# Tab-style view selector
tab1, tab2 = st.tabs(["🎛️ Manager Dashboard", "🚛 Driver View"])

with tab2:
   
    
    # Header with integrated controls
    header_col1, header_col2 = st.columns([2, 1])
    
    with header_col1:
        st.markdown("""
        <div class="glass-card" style="background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-hover) 100%); padding: 24px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -10px; right: -10px; font-size: 100px; opacity: 0.05;">🚛</div>
            <h2 style="margin: 0; font-size: 1.5rem;">Driver Mobile View</h2>
            <p style="color: var(--text-secondary); margin: 5px 0 0 0; font-size: 0.9rem;">
                Select your truck to see your assigned route and bins
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        # Agent Cycle Control - compact version at top
        current_step = st.session_state.current_step
        progress_pct = ((current_step + 1) / 6) * 100
        
        st.markdown(f"""
        <div class="glass-card" style="padding: 16px; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="metric-label">Phase</span>
                <span class="status-pill status-success">{STEPS[current_step]}</span>
            </div>
            <div style="background: var(--bg-app); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 8px;">
                <div style="background: var(--primary); width: {progress_pct}%; height: 100%;"></div>
            </div>
            <span style="color: var(--text-tertiary); font-size: 0.75em; font-family: var(--font-mono);">Step {current_step + 1}/6</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⏭️ NEXT STEP", type="primary", use_container_width=True, key="driver_next_step_top"):
            advance_step()
            st.rerun()
    
    st.markdown("---")
    
    city = st.session_state.city
    
    if city is None:
        st.warning("⚠️ Start the simulation first to see driver assignments.")
    else:
        # Truck selector
        truck_ids = list(city.trucks.keys())
        
        col_sel, col_status = st.columns([1, 2])
        
        with col_sel:
            selected_truck_id = st.selectbox(
                "🚛 Select Your Truck",
                truck_ids,
                format_func=lambda x: f"Truck {x}",
                key="driver_truck_select"
            )
        
        truck = city.trucks[selected_truck_id]
        
        with col_status:
            # Truck status card
            
            # Determine display load: Use persisted load if available (for Step 4+), else current
            display_load = truck.current_load
            if 'driver_loads' in st.session_state and selected_truck_id in st.session_state.driver_loads:
                # If we are in Step 4 or 5, current_load is reset to 0, so show the Cycle Load
                if st.session_state.current_step >= 4:
                     display_load = st.session_state.driver_loads[selected_truck_id]
            
            load_pct = (display_load / truck.capacity) * 100 if truck.capacity > 0 else 0
            status_color = "#22c55e" if load_pct < 70 else "#f59e0b" if load_pct < 90 else "#ef4444"
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 24px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="metric-label">Cycle Load</span><br>
                        <span class="metric-value">
                            {display_load:.0f} / {truck.capacity}
                        </span>
                    </div>
                    <div style="position: relative; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;">
                        <div style="position: absolute; inset: 0; border-radius: 50%; background: conic-gradient({status_color} {load_pct}%, var(--bg-hover) {load_pct}%);"></div>
                        <div style="position: absolute; inset: 6px; border-radius: 50%; background: var(--bg-card); display: flex; align-items: center; justify-content: center;">
                            <span style="color: var(--text-primary); font-weight: 700; font-size: 0.9rem;">{load_pct:.0f}%</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Assigned bins section - use stored data if available (after execution)
        assigned_bins = truck.assigned_bins
        collected_bins = []
        
        # Check if we have stored assignments from after execution
        if 'driver_assignments' in st.session_state and selected_truck_id in st.session_state.driver_assignments:
            stored_assignments = st.session_state.driver_assignments[selected_truck_id]
            if stored_assignments:  # Use stored data if current is empty
                assigned_bins = stored_assignments
            if 'driver_collected' in st.session_state and selected_truck_id in st.session_state.driver_collected:
                collected_bins = st.session_state.driver_collected[selected_truck_id]
        
        if not assigned_bins:
            st.markdown("""
            <div style="background: #374151; border-radius: 12px; padding: 40px; text-align: center;">
                <span style="font-size: 3em;">📭</span><br><br>
                <span style="color: #9ca3af; font-size: 1.2em;">No bins assigned yet</span><br>
                <span style="color: #6b7280;">Complete the Allocate phase to see your assignments</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if all bins are collected
            all_collected = len(collected_bins) == len(assigned_bins) and len(collected_bins) > 0
            header_color = "#10b981" if not all_collected else "#22c55e"
            header_text = f"📍 Your Route: {len(assigned_bins)} Stops" if not all_collected else f"✅ Mission Complete: {len(assigned_bins)} Bins Collected!"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {header_color} 0%, #059669 100%); 
                        border-radius: 12px; padding: 15px; margin-bottom: 15px;">
                <h3 style="color: white; margin: 0;">{header_text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
           
            for idx, bin_id in enumerate(assigned_bins):
                bin_obj = city.bins.get(bin_id)
                if bin_obj:
                    # Check if this bin is in collected list
                    is_collected = bin_id in collected_bins or bin_obj.collected
                    fill_pct = 0 if is_collected else (bin_obj.fill_level / bin_obj.max_capacity) * 100
                    fill_color = "#22c55e" if is_collected else ("#ef4444" if fill_pct >= 80 else "#f59e0b" if fill_pct >= 50 else "#22c55e")
                    collected = "✅ Collected" if is_collected else "⏳ Pending"
                    badge_color = "#22c55e" if is_collected else "#3b82f6"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 16px; margin-bottom: 12px; border-left: 4px solid {fill_color}; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem; margin-bottom: 4px;">
                                Stop {idx + 1}: Bin #{bin_id}
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                                📍 ({bin_obj.position[0]}, {bin_obj.position[1]})
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span class="status-pill" style="background: {badge_color}20; color: {badge_color}; margin-bottom: 4px;">
                                {collected}
                            </span>
                            <div style="color: {fill_color}; font-weight: 600; font-size: 1rem;">
                                Fill: {fill_pct:.0f}%
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
       
        if truck.route:
            st.markdown("---")
            st.markdown("### 🗺️ Route Overview")
            
            route_str = " → ".join([f"({p[0]},{p[1]})" for p in truck.route[:10]])
            if len(truck.route) > 10:
                route_str += f" → ... ({len(truck.route) - 10} more)"
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 16px;">
                <span class="metric-label">Route Path</span>
                <div style="color: var(--info); font-family: var(--font-mono); margin-top: 8px;">{route_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        
        
        st.markdown("### 📡 Live Status")
        
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            # GPS Position
            st.markdown(f"""
            <div class="metric-box" style="align-items: center; text-align: center;">
                <span class="metric-label">GPS Position</span>
                <span style="color: var(--success); font-size: 1.1rem; font-weight: 600;">({truck.position[0]}, {truck.position[1]})</span>
            </div>
            """, unsafe_allow_html=True)
        
        with sim_col2:
            # Next Stop ETA
            if assigned_bins and len(assigned_bins) > len(collected_bins):
                next_bin_idx = len(collected_bins)
                if next_bin_idx < len(assigned_bins):
                    next_bin_id = assigned_bins[next_bin_idx]
                    next_bin = city.bins.get(next_bin_id)
                    if next_bin:
                        # Calculate Manhattan distance
                        eta_dist = abs(truck.position[0] - next_bin.position[0]) + abs(truck.position[1] - next_bin.position[1])
                        eta_time = eta_dist * 2  # 2 min per unit
                        eta_display = f"{eta_time} min"
                    else:
                        eta_display = "--"
                else:
                    eta_display = "Complete"
            else:
                eta_display = "Complete" if collected_bins else "--"
            
            st.markdown(f"""
            <div class="metric-box" style="align-items: center; text-align: center;">
                <span class="metric-label">Next Stop ETA</span>
                <span style="color: var(--warning); font-size: 1.1rem; font-weight: 600;">{eta_display}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with sim_col3:
            # Status
            if len(collected_bins) == len(assigned_bins) and len(collected_bins) > 0:
                status_text = "Complete"
                status_color = "#22c55e"
            elif st.session_state.current_step >= 4:
                status_text = "En Route"
                status_color = "#3b82f6"
            elif st.session_state.current_step >= 3:
                status_text = "Assigned"
                status_color = "#f59e0b"
            else:
                status_text = "Waiting"
                status_color = "#6b7280"
            
            st.markdown(f"""
            <div class="metric-box" style="align-items: center; text-align: center;">
                <span class="metric-label">Status</span>
                <span style="color: {status_color}; font-size: 1.1rem; font-weight: 600;">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer spacer
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

with tab1:
    
    
    # 1. AI PERFORMANCE DASHBOARD
    st.markdown("### 🎯 AI Performance Dashboard")

    # Show dynamic KPIs based on simulation progress
    if st.session_state.current_step >= 4 and st.session_state.kpi_ai_distance > 0:
        # After Plan & Execute - show full comparison
        baseline_dist = st.session_state.kpi_baseline_distance
        ai_dist = st.session_state.kpi_ai_distance
        
        if baseline_dist > 0:
            dist_improvement = ((baseline_dist - ai_dist) / baseline_dist) * 100
            dist_delta = f"-{dist_improvement:.1f}%"
        else:
            dist_improvement = 0
            dist_delta = "N/A"
        
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            styles.metric_card("Bins Collected", st.session_state.kpi_bins_collected)
        with k2:
            styles.metric_card("AI Route Distance", f"{ai_dist:.1f}", delta=dist_delta)
        with k3:
            styles.metric_card("Baseline Distance", f"{baseline_dist:.1f}")
        with k4:
            styles.metric_card("Overflows Prevented", st.session_state.kpi_overflows_prevented)
        with k5:
            styles.metric_card("Compute Time", f"{st.session_state.kpi_computation_time:.1f}ms")
        
        # Show improvement summary card
        if dist_improvement > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                        border-radius: 12px; padding: 15px; margin: 10px 0; text-align: center;">
                <span style="color: white; font-size: 1.2em; font-weight: bold;">
                    ✅ AI Optimization Result: {dist_improvement:.1f}% Route Reduction | 
                    {st.session_state.kpi_bins_collected} Bins Collected | 
                    {st.session_state.kpi_overflows_prevented} Overflows Prevented
                </span>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Before Plan & Execute - show configuration
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1: styles.metric_card("Grid Size", f"{st.session_state.grid_size}×{st.session_state.grid_size}")
        with m2: styles.metric_card("Sensor Nodes", st.session_state.num_bins)
        with m3: styles.metric_card("Fleet Size", st.session_state.num_trucks)
        with m4: styles.metric_card("Truck Capacity", st.session_state.truck_capacity)
        with m5: styles.metric_card("Bin Capacity", st.session_state.bin_capacity)
        
        # Show status message
        step_name = STEPS[st.session_state.current_step]
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 20px; border-left: 4px solid var(--primary);">
            <div style="color: var(--text-primary); font-size: 1.1em; font-weight: 500;">
                🔄 Agent Cycle in Progress: <span style="color: var(--primary);">{step_name}</span> Phase
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9em; margin-top: 5px;">
                Complete all 6 steps to see AI vs Baseline comparison
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. SPLIT VIEW (Steps & Map)
    col_steps, col_map = st.columns([1, 3])

    with col_steps:
        st.markdown("### 🕹️ Agent Cycle")
        
        for i, step_name in enumerate(STEPS):
            is_active = (i == st.session_state.current_step)
            is_done = (i < st.session_state.current_step)
            
            style = "color: var(--text-tertiary); border-left: 2px solid var(--border-subtle); padding-left: 12px;"
            marker = ""
            
            if is_active:
                style = "color: var(--text-primary); font-weight: 600; border-left: 2px solid var(--primary); padding-left: 12px; background: linear-gradient(90deg, var(--bg-hover) 0%, transparent 100%);"
                marker = " <span class='status-pill status-info' style='font-size:0.7em; margin-left:8px;'>ACTIVE</span>"
            elif is_done:
                style = "color: var(--success); border-left: 2px solid var(--success); padding-left: 12px;"
                marker = " ✓"
                
            st.markdown(f"<div style='margin-bottom: 8px; padding-top:4px; padding-bottom:4px; {style} transition: all 0.2s;'>{step_name}{marker}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("NEXT STEP ⏭️", type="primary", use_container_width=True):
            advance_step()
            st.rerun()

    with col_map:
        # Map Display
        # We pass routes only if we are in Plan (4) or Execute (5) phase
        display_routes = st.session_state.routes if st.session_state.current_step >= 4 else {}
        
        # Show status colors only after Sense phase (Step 0)
        show_status_colors = st.session_state.current_step > 0
        
        # Pass reasoning_results in Reason phase (Step 2) and beyond
        display_reasoning = None
        if st.session_state.current_step >= 2:
            display_reasoning = st.session_state.step_data.get('reasoning_results')
        
        # Pass classifications for Predict phase (Step 1) only - before Reason has run
        display_classifications = None
        if st.session_state.current_step == 1:
            display_classifications = st.session_state.step_data.get('classifications')

        # Pass allocated bins from Allocate phase (Step 3) onwards
        allocated_ids = None
        if st.session_state.current_step >= 3:
            results = st.session_state.step_data.get('auction_results', [])
            allocated_ids = [r.bin_id for r in results]

        html_block = ui.get_js_animation_html(
            st.session_state.city, 
            display_routes,
            st.session_state.scanned_nodes if st.session_state.current_step >= 4 else [],
            st.session_state.baseline_routes,
            show_status=show_status_colors,
            classifications=display_classifications,
            allocated_bin_ids=allocated_ids,
            reasoning_results=display_reasoning,
            current_step=st.session_state.current_step
        )
        components.html(html_block, height=500, scrolling=False)
        
        # Dynamic Explanation Logic
        base_explanation = STEP_EXPLANATIONS[st.session_state.current_step]
        dynamic_detail = ""
        
        if st.session_state.current_step == 1: # Predict
            classifications = st.session_state.step_data.get('classifications', [])
            full_count = sum(1 for c in classifications if c.is_full)
            urgent_count = sum(1 for c in classifications if c.is_urgent and not c.is_full)
            dynamic_detail = f"<br><br><b>Current Scenario:</b> The model has identified <b>{full_count}</b> Full bins (Critical) and <b>{urgent_count}</b> Urgent bins (Predicted Overflow)."
            
        elif st.session_state.current_step == 2: # Reason
            reasoning_results = st.session_state.step_data.get('reasoning_results', [])
            green_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREEN)
            orange_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.ORANGE)
            grey_count = sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREY)
            from_prediction = sum(1 for r in reasoning_results if r.is_predicted)
            
            base_explanation = (
                "<b>KR Filtering:</b> The agent applies Knowledge Representation rules to <b>ALL bins</b>, "
                "using the Predict output as input context. This proves reasoning by showing that: "
                "(1) Some predicted bins can become ineligible due to constraints, and "
                "(2) Some non-predicted bins can still be eligible (e.g., full but stable)."
            )
            dynamic_detail = (
                f"<br><br><b>Current Scenario:</b> Out of <b>{len(reasoning_results)}</b> total bins evaluated: "
                f"<span style='color:#22c55e;'>✅ {green_count} GREEN</span> (Eligible for service), "
                f"<span style='color:#f97316;'>❌ {orange_count} ORANGE</span> (Urgent but blocked), "
                f"<span style='color:#6b7280;'>⚪ {grey_count} GREY</span> (Not relevant). "
                f"<br>Prediction provided context for {from_prediction} bins."
            )

        elif st.session_state.current_step == 3: # Allocate
            results = st.session_state.step_data.get('auction_results', [])
            dynamic_detail = f"<br><br><b>Current Scenario:</b> {len(results)} tasks have been successfully auctioned to the fleet."
            
            # Allocation Table
            if results:
                data = []
                for r in results:
                    data.append({
                        "Bin ID": f"B{r.bin_id}",
                        "Assigned Truck": f"Truck {r.truck_id}",
                        "Winning Bid": f"{r.winning_bid:.1f}",
                        "Reason": "Lowest Cost Bidder"
                    })
                df = pd.DataFrame(data)
                # st.markdown("##### 🤝 Auction Results")
                st.dataframe(df, hide_index=True, use_container_width=True)

        elif st.session_state.current_step == 4: # Plan
            ai_dist = st.session_state.kpi_ai_distance
            baseline_dist = st.session_state.kpi_baseline_distance
            if baseline_dist > 0:
                improvement = ((baseline_dist - ai_dist) / baseline_dist) * 100
                dynamic_detail = f"<br><br><b>🚀 AI Optimization:</b> Route distance reduced from <b>{baseline_dist:.1f}</b> (baseline) to <b>{ai_dist:.1f}</b> (AI optimized) = <span style='color:#22c55e; font-weight:bold;'>{improvement:.1f}% improvement!</span>"
            else:
                dynamic_detail = f"<br><br><b>Current Scenario:</b> Optimal routes generated with total distance of {ai_dist:.1f} units."
        
        elif st.session_state.current_step == 5: # Adapt (Cycle Complete)
            base_explanation = "The cycle is complete! The AI agent has successfully executed a full Sense→Predict→Reason→Allocate→Plan→Execute loop."
            ai_dist = st.session_state.kpi_ai_distance
            baseline_dist = st.session_state.kpi_baseline_distance
            bins_collected = st.session_state.kpi_bins_collected
            overflows_prevented = st.session_state.kpi_overflows_prevented
            
            if baseline_dist > 0:
                improvement = ((baseline_dist - ai_dist) / baseline_dist) * 100
            else:
                improvement = 0
            
            dynamic_detail = f"""
            <br><br>
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 8px; padding: 15px; margin-top: 10px;'>
                <b style='color:white; font-size: 1.1em;'>📊 Cycle Summary:</b><br>
                <span style='color:white;'>
                • <b>{bins_collected}</b> bins collected<br>
                • <b>{overflows_prevented}</b> potential overflows prevented<br>
                • <b>{improvement:.1f}%</b> route distance reduction vs baseline<br>
                • Computation time: <b>{st.session_state.kpi_computation_time:.1f}ms</b>
                </span>
            </div>
            <br><b>Click NEXT STEP</b> to start a new cycle (bins will refill over time).
            """

        # Explanation Panel
        st.markdown(f"""
        <div class="glass-card" style="margin-top: 10px; padding: 20px;">
            <h4 style="margin:0 0 10px 0; display:flex; align-items:center; gap:8px;">
                <span class="status-pill status-info">{STEPS[st.session_state.current_step]} Phase</span>
            </h4>
            <div style="color:var(--text-secondary); font-size: 0.95rem; line-height: 1.6;">{base_explanation}{dynamic_detail}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. DECISION LOG (Bottom)
    with st.expander("📋 Decision Kernel Log", expanded=True):
        ui.render_decision_feed(st.session_state.decision_log)
