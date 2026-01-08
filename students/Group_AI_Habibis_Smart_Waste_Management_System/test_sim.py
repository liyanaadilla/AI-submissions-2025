from modules.simulation import City
import networkx as nx

def test_simulation_dynamics():
    print("Testing Simulation Dynamics...")
    
    # Initialize City
    city = City(grid_size=10, num_bins=5, num_trucks=1)
    
    # 1. Verify Time Step
    print("\n[1] Testing Time Step...")
    initial_fills = {b.id: b.fill_level for b in city.bins.values()}
    print(f"Initial Fills: {initial_fills}")
    
    # Advance time by 60 minutes
    city.step(60)
    print("Step(60) called.")
    
    final_fills = {b.id: b.fill_level for b in city.bins.values()}
    print(f"Final Fills: {final_fills}")
    
    # Check if fills increased
    for bid, val in initial_fills.items():
        assert final_fills[bid] >= val, f"Bin {bid} fill level decreased or same!"
        if final_fills[bid] > val:
            print(f"Bin {bid} increased by {final_fills[bid] - val:.2f}")
            
    # 2. Verify Event Trigger
    print("\n[2] Testing Event Trigger...")
    initial_edges = len(city.to_networkx().edges())
    print(f"Initial Graph Edges: {initial_edges}")
    
    msg = city.trigger_random_event()
    print(f"Event Triggered: {msg}")
    
    final_edges = len(city.to_networkx().edges())
    print(f"Final Graph Edges: {final_edges}")
    
    assert final_edges < initial_edges, "Edge was not removed from NetworkX graph view!"
    assert len(city.closed_roads) == 1, "Closed road not recorded!"
    
    print("\nAll Tests Passed!")

if __name__ == "__main__":
    test_simulation_dynamics()
