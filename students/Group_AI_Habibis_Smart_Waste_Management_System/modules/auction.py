"""
Auction-Based Task Allocation Module for Smart Waste Management System

This module implements auction mechanisms for assigning bins to trucks:
- Each truck computes a bid based on marginal route cost
- Bins are assigned to the lowest bidder
- Supports multi-truck coordination

AI Component: Distributed decision-making via auction protocols
This satisfies FR-8, FR-9, and FR-10 from the SRS.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
import math


@dataclass
class Bid:
    """
    Represents a truck's bid for a bin.
    
    Attributes:
        truck_id: Bidding truck identifier
        bin_id: Target bin identifier
        bid_value: Marginal cost to collect this bin
        current_route_cost: Cost of truck's current route
        new_route_cost: Cost if bin is added
        explanation: Human-readable bid explanation
    """
    truck_id: int
    bin_id: int
    bid_value: float
    current_route_cost: float
    new_route_cost: float
    explanation: str


@dataclass
class AllocationResult:
    """
    Result of bin-to-truck allocation.
    
    Attributes:
        bin_id: Allocated bin
        truck_id: Winning truck
        winning_bid: Winning bid value
        all_bids: All bids received for this bin
    """
    bin_id: int
    truck_id: int
    winning_bid: float
    all_bids: List[Bid]


def compute_marginal_cost(truck_position: Tuple[int, int],
                          current_route: List[Tuple[int, int]],
                          new_bin_position: Tuple[int, int],
                          graph: nx.Graph,
                          depot: Tuple[int, int]) -> Tuple[float, float, float]:
    """
    Compute marginal cost of adding a bin to a truck's route.
    
    The marginal cost is the increase in total route distance
    when the new bin is inserted optimally into the current route.
    
    AI Component: This forms the basis of truthful bidding in auctions
    
    Args:
        truck_position: Current truck position
        current_route: List of positions to visit
        new_bin_position: Position of new bin to potentially add
        graph: Road network graph
        depot: Depot position for return trip
    
    Returns:
        Tuple of (marginal_cost, current_total, new_total)
    """
    try:
        # Calculate current route cost
        if not current_route:
            current_cost = 0.0
            # Cost to go to new bin and back
            dist_to_bin = nx.shortest_path_length(
                graph, truck_position, new_bin_position, weight='weight'
            )
            dist_to_depot = nx.shortest_path_length(
                graph, new_bin_position, depot, weight='weight'
            )
            new_cost = dist_to_bin + dist_to_depot
        else:
            # Current cost: truck -> all route points -> depot
            current_cost = calculate_route_cost(
                truck_position, current_route, depot, graph
            )
            
            # Find best insertion point for new bin
            new_cost = float('inf')
            
            # Try inserting new bin at each position
            for i in range(len(current_route) + 1):
                test_route = current_route[:i] + [new_bin_position] + current_route[i:]
                test_cost = calculate_route_cost(
                    truck_position, test_route, depot, graph
                )
                new_cost = min(new_cost, test_cost)
        
        marginal_cost = new_cost - current_cost
        return marginal_cost, current_cost, new_cost
    
    except nx.NetworkXNoPath:
        # No path exists (e.g., due to road closure)
        return float('inf'), float('inf'), float('inf')


def calculate_route_cost(start: Tuple[int, int], 
                         waypoints: List[Tuple[int, int]],
                         end: Tuple[int, int],
                         graph: nx.Graph) -> float:
    """
    Calculate total cost of a route through waypoints.
    
    Args:
        start: Starting position
        waypoints: List of positions to visit in order
        end: Final destination
        graph: Road network graph
    
    Returns:
        Total route cost (distance)
    """
    if not waypoints:
        try:
            return nx.shortest_path_length(graph, start, end, weight='weight')
        except nx.NetworkXNoPath:
            return float('inf')
    
    total = 0.0
    current = start
    
    for wp in waypoints:
        try:
            total += nx.shortest_path_length(graph, current, wp, weight='weight')
            current = wp
        except nx.NetworkXNoPath:
            return float('inf')
    
    # Return to end (depot)
    try:
        total += nx.shortest_path_length(graph, current, end, weight='weight')
    except nx.NetworkXNoPath:
        return float('inf')
    
    return total


def compute_bid(truck, bin_obj, graph: nx.Graph, depot: Tuple[int, int]) -> Bid:
    """
    Compute a truck's bid for a specific bin.
    
    AI Component: Auction-based multi-agent coordination
    
    Args:
        truck: Truck object (from city module)
        bin_obj: WasteBin object to bid on
        graph: Road network graph
        depot: Depot position
    
    Returns:
        Bid object with bid value and explanation
    """
    # Get current route as list of positions
    current_route = list(truck.route) if truck.route else []
    
    # Compute marginal cost
    marginal, current_cost, new_cost = compute_marginal_cost(
        truck_position=truck.position,
        current_route=current_route,
        new_bin_position=bin_obj.position,
        graph=graph,
        depot=depot
    )
    
    # Generate explanation
    if marginal == float('inf'):
        explanation = f"Truck {truck.id}: Cannot reach Bin {bin_obj.id} (no path)"
    else:
        explanation = (
            f"Truck {truck.id} bids {marginal:.2f} for Bin {bin_obj.id} "
            f"(route: {current_cost:.1f}→{new_cost:.1f})"
        )
    
    return Bid(
        truck_id=truck.id,
        bin_id=bin_obj.id,
        bid_value=marginal,
        current_route_cost=current_cost,
        new_route_cost=new_cost,
        explanation=explanation
    )


def allocate_single_bin(bin_obj, trucks: Dict, bins: Dict,
                        graph: nx.Graph, depot: Tuple[int, int]) -> Optional[AllocationResult]:
    """
    Allocate a single bin to the best-suited truck via auction.
    
    AI Component: Winner determination in single-item auction
    
    Args:
        bin_obj: WasteBin to allocate
        trucks: Dictionary of truck_id -> Truck objects
        bins: Dictionary of bin_id -> WasteBin objects
        graph: Road network graph
        depot: Depot position
    
    Returns:
        AllocationResult if allocation successful, None otherwise
    """
    all_bids = []
    
    for truck_id, truck in trucks.items():
        # Skip trucks that can't accommodate this bin
        if truck.current_load + bin_obj.fill_level > truck.capacity:
            continue
        
        bid = compute_bid(truck, bin_obj, graph, depot)
        all_bids.append(bid)
    
    if not all_bids:
        return None
    
    # Find lowest bid (winner)
    winning_bid = min(all_bids, key=lambda b: b.bid_value)
    
    if winning_bid.bid_value == float('inf'):
        return None  # No feasible allocation
    
    return AllocationResult(
        bin_id=bin_obj.id,
        truck_id=winning_bid.truck_id,
        winning_bid=winning_bid.bid_value,
        all_bids=all_bids
    )


def allocate_bins(eligible_bin_ids: List[int], trucks: Dict, bins: Dict,
                  graph: nx.Graph, depot: Tuple[int, int]) -> List[AllocationResult]:
    """
    Allocate all eligible bins to trucks using sequential auctions.
    
    AI Component: Multi-item auction with sequential allocation
    
    The algorithm:
    1. For each eligible bin (in priority order)
    2. Conduct auction among all trucks
    3. Assign bin to lowest bidder
    4. Update truck's route for next auction
    
    Args:
        eligible_bin_ids: List of bin IDs to allocate
        trucks: Dictionary of truck_id -> Truck objects
        bins: Dictionary of bin_id -> WasteBin objects
        graph: Road network graph
        depot: Depot position
    
    Returns:
        List of AllocationResult objects
    """
    allocations = []
    
    # Create working copy of truck routes
    truck_routes = {tid: list(truck.route) for tid, truck in trucks.items()}
    truck_loads = {tid: truck.current_load for tid, truck in trucks.items()}
    
    for bin_id in eligible_bin_ids:
        if bin_id not in bins:
            continue
        
        bin_obj = bins[bin_id]
        all_bids = []
        
        for truck_id, truck in trucks.items():
            # Check capacity with current allocated load
            if truck_loads[truck_id] + bin_obj.fill_level > truck.capacity:
                continue
            
            # Create temporary truck-like object with current route
            class TempTruck:
                def __init__(self, tid, pos, route):
                    self.id = tid
                    self.position = pos
                    self.route = route
            
            temp_truck = TempTruck(truck_id, truck.position, truck_routes[truck_id])
            bid = compute_bid(temp_truck, bin_obj, graph, depot)
            all_bids.append(bid)
        
        if not all_bids:
            continue
        
        # Find winner
        winning_bid = min(all_bids, key=lambda b: b.bid_value)
        
        if winning_bid.bid_value == float('inf'):
            continue
        
        # Update winner's state for next iteration
        winner_id = winning_bid.truck_id
        truck_routes[winner_id].append(bin_obj.position)
        truck_loads[winner_id] += bin_obj.fill_level
        
        # Also update actual truck object
        trucks[winner_id].assigned_bins.append(bin_id)
        trucks[winner_id].route.append(bin_obj.position)
        
        allocations.append(AllocationResult(
            bin_id=bin_id,
            truck_id=winner_id,
            winning_bid=winning_bid.bid_value,
            all_bids=all_bids
        ))
    
    return allocations


def get_auction_summary(allocations: List[AllocationResult]) -> Dict:
    """
    Summarize auction results for display.
    
    Args:
        allocations: List of AllocationResult objects
    
    Returns:
        Dictionary with auction statistics
    """
    if not allocations:
        return {
            'total_allocated': 0,
            'total_bid_value': 0,
            'avg_bid_value': 0,
            'bids_per_bin': 0
        }
    
    total_bids = sum(len(a.all_bids) for a in allocations)
    
    return {
        'total_allocated': len(allocations),
        'total_bid_value': round(sum(a.winning_bid for a in allocations), 2),
        'avg_bid_value': round(sum(a.winning_bid for a in allocations) / len(allocations), 2),
        'bids_per_bin': round(total_bids / len(allocations), 1) if allocations else 0
    }
