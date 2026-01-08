"""
City Simulation Module for Smart Waste Management System

This module provides the core simulation components:
- City: Road network represented as a grid graph
- WasteBin: Waste containers with dynamic fill levels
- Truck: Collection vehicles with capacity constraints

AI Component: Environment representation for the agent loop (Sense phase)
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import random


@dataclass
class WasteBin:
    """
    Represents a waste bin in the city.
    
    Attributes:
        id: Unique identifier
        position: (x, y) coordinates on the city grid
        fill_level: Current fill percentage (0-100)
        fill_rate: Waste accumulation rate per time step (% per step)
        capacity: Maximum capacity in abstract units
        collected: Whether bin has been collected this cycle
    """
    id: int
    position: Tuple[int, int]
    fill_level: float = 0.0
    fill_rate: float = 1.0  # % increase per time step
    capacity: float = 100.0
    collected: bool = False
    
    def update(self, time_steps: int = 1) -> None:
        """Simulate waste accumulation over time steps."""
        if not self.collected:
            self.fill_level = min(100.0, self.fill_level + self.fill_rate * time_steps)
    
    def collect(self) -> float:
        """Collect waste from bin. Returns amount collected."""
        amount = self.fill_level
        self.fill_level = 0.0
        self.collected = True
        return amount
    
    def reset_collection_flag(self) -> None:
        """Reset collection flag for new cycle."""
        self.collected = False
    
    def is_overflowing(self) -> bool:
        """Check if bin has reached 100% capacity (overflow)."""
        return self.fill_level >= 100.0


@dataclass
class Truck:
    """
    Represents a waste collection truck.
    
    Attributes:
        id: Unique identifier
        position: Current (x, y) coordinates
        depot: Home depot position
        capacity: Maximum load capacity
        current_load: Current waste load
        assigned_bins: List of bin IDs assigned for collection
        route: Planned route as list of positions
        distance_traveled: Total distance covered
    """
    id: int
    position: Tuple[int, int]
    depot: Tuple[int, int]
    capacity: float = 100.0
    current_load: float = 0.0
    assigned_bins: List[int] = field(default_factory=list)
    route: List[Tuple[int, int]] = field(default_factory=list)
    distance_traveled: float = 0.0
    
    def can_collect(self, amount: float) -> bool:
        """Check if truck can accommodate additional waste."""
        return self.current_load + amount <= self.capacity
    
    def load(self, amount: float) -> bool:
        """Load waste onto truck. Returns success status."""
        if self.can_collect(amount):
            self.current_load += amount
            return True
        return False
    
    def empty(self) -> float:
        """Empty truck at depot. Returns amount emptied."""
        amount = self.current_load
        self.current_load = 0.0
        return amount
    
    def move_to(self, new_position: Tuple[int, int], distance: float) -> None:
        """Move truck to new position and track distance."""
        self.position = new_position
        self.distance_traveled += distance
    
    def remaining_capacity(self) -> float:
        """Get remaining load capacity."""
        return self.capacity - self.current_load
    
    def reset_for_new_cycle(self) -> None:
        """Reset truck for a new collection cycle."""
        self.assigned_bins = []
        self.route = []


class City:
    """
    City simulation environment with road network, bins, and trucks.
    
    The city is represented as a grid where:
    - Nodes are intersections
    - Edges are roads connecting adjacent intersections
    - Bins are placed at various intersections
    - Trucks navigate the road network
    
    AI Component: This is the environment that agents perceive and act upon.
    """
    
    def __init__(self, grid_size: int = 10, num_bins: int = 15, 
                 num_trucks: int = 2, truck_capacity: float = 100.0,
                 seed: Optional[int] = None):
        """
        Initialize city simulation.
        
        Args:
            grid_size: Size of the city grid (grid_size x grid_size)
            num_bins: Number of waste bins to place
            num_trucks: Number of collection trucks
            truck_capacity: Capacity of each truck
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.grid_size = grid_size
        self.graph = self._create_road_network()
        self.depot = (0, 0)  # Depot at origin
        
        # Create bins at random positions (excluding depot)
        self.bins: Dict[int, WasteBin] = {}
        self._place_bins(num_bins)
        
        # Create trucks at depot
        self.trucks: Dict[int, Truck] = {}
        self._create_trucks(num_trucks, truck_capacity)
        
        # Simulation state
        self.time_step = 0
        self.closed_roads: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        self.overflow_count = 0
        self.collections_made = 0
    
    def _create_road_network(self) -> nx.Graph:
        """Create a grid-based road network graph."""
        G = nx.grid_2d_graph(self.grid_size, self.grid_size)
        
        # Add edge weights (distances) - default is 1 for adjacent nodes
        for u, v in G.edges():
            G[u][v]['weight'] = 1.0
            G[u][v]['closed'] = False
        
        return G
    
    def _place_bins(self, num_bins: int) -> None:
        """Place waste bins at random positions on the grid."""
        available_positions = [
            (x, y) for x in range(self.grid_size) 
            for y in range(self.grid_size)
            if (x, y) != self.depot
        ]
        
        # Ensure we don't try to place more bins than available positions
        num_bins = min(num_bins, len(available_positions))
        
        positions = random.sample(available_positions, num_bins)
        
        for i, pos in enumerate(positions):
            # Randomize initial fill level and fill rate for variety
            initial_fill = random.uniform(10, 60)
            fill_rate = random.uniform(0.5, 3.0)  # % per time step
            
            self.bins[i] = WasteBin(
                id=i,
                position=pos,
                fill_level=initial_fill,
                fill_rate=fill_rate
            )
    
    def _create_trucks(self, num_trucks: int, capacity: float) -> None:
        """Create trucks at the depot."""
        for i in range(num_trucks):
            self.trucks[i] = Truck(
                id=i,
                position=self.depot,
                depot=self.depot,
                capacity=capacity
            )
    
    def step(self, time_steps: int = 1) -> Dict:
        """
        Advance simulation by given time steps.
        
        Returns:
            Dict with simulation state updates
        """
        self.time_step += time_steps
        
        overflows_this_step = 0
        
        # Update all bins
        for bin_obj in self.bins.values():
            was_overflowing = bin_obj.is_overflowing()
            bin_obj.update(time_steps)
            
            # Count new overflows
            if bin_obj.is_overflowing() and not was_overflowing:
                overflows_this_step += 1
                self.overflow_count += 1
        
        return {
            'time_step': self.time_step,
            'new_overflows': overflows_this_step,
            'total_overflows': self.overflow_count
        }
    
    def close_road(self, node1: Tuple[int, int], node2: Tuple[int, int]) -> bool:
        """
        Close a road segment (dynamic event).
        
        AI Component: Demonstrates dynamic re-planning capability.
        """
        if self.graph.has_edge(node1, node2):
            self.graph[node1][node2]['closed'] = True
            self.closed_roads.append((node1, node2))
            return True
        return False
    
    def open_road(self, node1: Tuple[int, int], node2: Tuple[int, int]) -> bool:
        """Reopen a previously closed road."""
        if self.graph.has_edge(node1, node2):
            self.graph[node1][node2]['closed'] = False
            if (node1, node2) in self.closed_roads:
                self.closed_roads.remove((node1, node2))
            elif (node2, node1) in self.closed_roads:
                self.closed_roads.remove((node2, node1))
            return True
        return False
    
    def trigger_waste_spike(self, bin_id: int, spike_amount: float = 30.0) -> bool:
        """
        Trigger a sudden waste spike at a bin (dynamic event).
        
        AI Component: Demonstrates handling unexpected changes.
        """
        if bin_id in self.bins:
            self.bins[bin_id].fill_level = min(
                100.0, 
                self.bins[bin_id].fill_level + spike_amount
            )
            return True
        return False
    
    def get_active_graph(self) -> nx.Graph:
        """Get road network with closed roads removed."""
        active_graph = self.graph.copy()
        
        for node1, node2 in self.closed_roads:
            if active_graph.has_edge(node1, node2):
                active_graph.remove_edge(node1, node2)
        
        return active_graph
    
    def collect_bin(self, truck_id: int, bin_id: int) -> bool:
        """
        Execute collection of a bin by a truck.
        
        Returns:
            Success status of collection
        """
        if truck_id not in self.trucks or bin_id not in self.bins:
            return False
        
        truck = self.trucks[truck_id]
        bin_obj = self.bins[bin_id]
        
        # Check if truck can accommodate the waste
        if truck.can_collect(bin_obj.fill_level):
            amount = bin_obj.collect()
            truck.load(amount)
            self.collections_made += 1
            return True
        
        return False
    
    def reset_collection_cycle(self) -> None:
        """Reset for a new collection cycle."""
        for bin_obj in self.bins.values():
            bin_obj.reset_collection_flag()
        
        for truck in self.trucks.values():
            truck.reset_for_new_cycle()
    
    def get_state_summary(self) -> Dict:
        """Get current state summary for display."""
        bin_states = []
        for bin_obj in self.bins.values():
            bin_states.append({
                'id': bin_obj.id,
                'position': bin_obj.position,
                'fill_level': round(bin_obj.fill_level, 1),
                'fill_rate': round(bin_obj.fill_rate, 2),
                'collected': bin_obj.collected,
                'overflowing': bin_obj.is_overflowing()
            })
        
        truck_states = []
        for truck in self.trucks.values():
            truck_states.append({
                'id': truck.id,
                'position': truck.position,
                'load': round(truck.current_load, 1),
                'capacity': truck.capacity,
                'assigned_bins': truck.assigned_bins.copy(),
                'distance': round(truck.distance_traveled, 1)
            })
        
        return {
            'time_step': self.time_step,
            'bins': bin_states,
            'trucks': truck_states,
            'closed_roads': self.closed_roads.copy(),
            'overflow_count': self.overflow_count,
            'collections_made': self.collections_made
        }
