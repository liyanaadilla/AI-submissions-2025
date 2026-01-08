import random
import heapq
import networkx as nx

class Bin:
    def __init__(self, bin_id, pos, max_capacity=100):
        self.bin_id = bin_id
        self.id = bin_id  # Alias for reasoning.py compatibility
        self.position = pos
        self.max_capacity = max_capacity
        self.fill_level = random.randint(int(max_capacity * 0.3), int(max_capacity * 0.95))
        self.fill_rate = round(random.uniform(0.5, 3.0), 2)  # % per time step (for ETA prediction)
        self.is_full = self.fill_level >= (max_capacity * 0.8)
        self.collected = False  # For reasoning.py compatibility
        self.is_collected = self.collected  # Alias

class Truck:
    def __init__(self, truck_id, start_pos, capacity=300):
        self.id = truck_id
        self.position = start_pos
        self.capacity = capacity
        self.assigned_bins = []
        self.route = [] # List of positions
        self.current_load = 0

class City:
    def to_networkx(self):
        """Convert grid to NetworkX graph for compatibility with auction module"""
        G = nx.grid_2d_graph(self.grid_size, self.grid_size)
        # Add weights
        for u, v in G.edges():
            edge_data = self.graph[u][v]
            if edge_data.get('closed', False):
                 # Effectively remove edge or make weight infinite
                 # Removing edge is safer for A* implementations
                 pass
            else:
                 G.edges[u, v]['weight'] = 1
        
        # Remove closed edges from the view
        for u, v in self.closed_roads:
            if G.has_edge(u, v):
                G.remove_edge(u, v)
                
        return G

    def __init__(self, grid_size=6, num_bins=8, num_trucks=2, truck_capacity=300, bin_capacity=100):
        self.grid_size = grid_size
        self.depot = (0, 0)
        self.bins = {}
        self.trucks = {}
        self.graph = nx.grid_2d_graph(grid_size, grid_size)
        self.closed_roads = [] # List of (u, v) tuples
        self.time_elapsed = 0 # Minutes since start
        self.truck_capacity = truck_capacity
        self.bin_capacity = bin_capacity
        
        # Initialize Bins at random locations
        # Ensure at least 6 bins are critical (fill_level >= 80% of capacity)
        min_critical_bins = 6
        critical_threshold = int(bin_capacity * 0.8)
        used_pos = {self.depot}
        for i in range(num_bins):
            while True:
                pos = (random.randint(0, grid_size-1), random.randint(0, grid_size-1))
                if pos not in used_pos:
                    self.bins[i] = Bin(i, pos, max_capacity=bin_capacity)
                    # Force first 'min_critical_bins' bins to be critical
                    if i < min_critical_bins:
                        self.bins[i].fill_level = random.randint(critical_threshold, int(bin_capacity * 0.95))
                        self.bins[i].is_full = True
                    used_pos.add(pos)
                    break
        
        # Initialize Trucks
        for i in range(num_trucks):
            self.trucks[i] = Truck(i, self.depot, capacity=truck_capacity)

    def get_neighbors(self, pos):
        """Get valid grid neighbors for A* pathfinding"""
        x, y = pos
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        valid = []
        for dx, dy in moves:
            nx_pos, ny_pos = x+dx, y+dy
            if 0 <= nx_pos < self.grid_size and 0 <= ny_pos < self.grid_size:
                valid.append((nx_pos, ny_pos))
        return valid

    def step(self, minutes=30):
        """
        Advance simulation time.
        Updates bin fill levels based on their fill rates.
        
        Args:
            minutes: Number of minutes to advance
        """
        self.time_elapsed += minutes
        
        for bin_obj in self.bins.values():
            # Fill rate is % per 30 minutes (implied by previous logic, let's standardize)
            # reasoning.py uses 30min steps for eta.
            # Let's say fill_rate is % per minute for simplicity or adjust accordingly.
            # Existing code: fill_rate = random.uniform(0.5, 3.0)
            # If that's per step (30 min), then per minute is small. 
            # If that's per minute, then 30*0.5 = 15% increase, which is reasonable.
            
            increase = bin_obj.fill_rate * (minutes / 30.0)
            bin_obj.fill_level = min(bin_obj.max_capacity, bin_obj.fill_level + increase)
            bin_obj.is_full = bin_obj.fill_level >= (bin_obj.max_capacity * 0.8)

    def trigger_random_event(self):
        """
        Simulate a dynamic event: Road Closure.
        Randomly closes an edge in the graph.
        """
        edges = list(self.graph.edges())
        if not edges: return
        
        # Pick a random edge to close
        u, v = random.choice(edges)
        
        # Mark as closed in graph data
        self.graph[u][v]['closed'] = True
        self.closed_roads.append((u, v))
        
        return f"Road Closed between {u} and {v}"

from types import SimpleNamespace

def get_manhattan_path(start, end):
    """Generate a simple L-shaped Manhattan path for baseline visualization"""
    path = [start]
    curr_x, curr_y = start
    end_x, end_y = end
    
    # Move X
    step_x = 1 if end_x > curr_x else -1
    while curr_x != end_x:
        curr_x += step_x
        path.append((curr_x, curr_y))
        
    # Move Y
    step_y = 1 if end_y > curr_y else -1
    while curr_y != end_y:
        curr_y += step_y
        path.append((curr_x, curr_y))
        
    return path

# A* Pathfinding Algorithm (Kept for fallback/visuals, but Auction uses NetworkX)
def a_star_search(city, start, end, return_explored=False):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = set()
    
    while frontier:
        current = heapq.heappop(frontier)[1]
        if return_explored:
            explored.add(current)
        
        if current == end:
            break
        
        for next_node in city.get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(end, next_node)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
                
    path = []
    if end in came_from:
        curr = end
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.append(start)
        path = path[::-1]
    else:
        path = [start]

    if return_explored:
        return SimpleNamespace(path=path, explored_nodes=list(explored))
    else:
        return path
