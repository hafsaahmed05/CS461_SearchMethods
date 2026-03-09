import numpy as np
import random

'''
ChatGPT Prompt:
Based on the chat about the path search, how should I go about this project. 
Let's start with grid.py. What functions should I have in the grid class to create the 
grid environment?

The functions used in this class were given by ChatGPT.
'''

EMPTY    = 0
OBSTACLE = 1
START    = 2
GOAL     = 3

class GridEnvironment:
    def __init__(self, rows=10, cols=10, obstacle_pct=0.25):
        self.rows = rows
        self.cols = cols
        self.obstacle_pct = obstacle_pct  # should be between 0.20 and 0.30
        self.grid = None        # 2D numpy array of cell values
        self.obstacles = set()  # set of (r, c) tuples for O(1) lookup
        self.start = None       # (r, c) tuple
        self.goal  = None       # (r, c) tuple
        self.adjacency = {}     # {(r,c): [(r2,c2), ...]}

        self.initialize_grid()  # build everything on construction

    # Top-level builder - calls phases in the correct order
    def initialize_grid(self):
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.assign_obstacles()
        self.place_nodes()
        self.build_adjacency()

    # Phase 1 - Scatter obstacles across the grid
    def assign_obstacles(self):
        total_cells  = self.rows * self.cols
        num_obstacles = int(total_cells * self.obstacle_pct)

        # Build a flat list of all positions, shuffle, take the first N
        all_positions = [(r, c) for r in range(self.rows)
                                  for c in range(self.cols)]
        random.shuffle(all_positions)

        for r, c in all_positions[:num_obstacles]:
            self.obstacles.add((r, c))
            self.grid[r][c] = OBSTACLE

    # Phase 2 - Place start and goal on valid (non-obstacle) cells
    def place_nodes(self):
        valid_cells = [(r, c) for r in range(self.rows)
                              for c in range(self.cols)
                              if (r, c) not in self.obstacles]

        if len(valid_cells) < 2:
            raise ValueError("Not enough open cells to place start and goal.")

        # Sample 2 distinct positions without replacement
        self.start, self.goal = random.sample(valid_cells, 2)

        self.grid[self.start[0]][self.start[1]] = START
        self.grid[self.goal[0]][self.goal[1]]   = GOAL

    '''
    Claude Prompt:
    Help give adjacency code based on the following GridEnvironment class and functions
    '''
    # Phase 3 - Build adjacency list (4-cardinal neighbors only)
    def build_adjacency(self):
        # Cardinal direction offsets: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.obstacles:
                    continue  # blocked nodes have no edges

                neighbors = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if self.is_valid(nr, nc):
                        neighbors.append((nr, nc))

                self.adjacency[(r, c)] = neighbors

    # Helper - bounds check + not an obstacle
    def is_valid(self, r, c):
        in_bounds = (0 <= r < self.rows) and (0 <= c < self.cols)
        return in_bounds and (r, c) not in self.obstacles

    # Helper - BFS connectivity check (can start reach goal?)
    def is_connected(self):
        if self.start is None or self.goal is None:
            return False

        visited = set()
        queue   = [self.start]

        while queue:
            node = queue.pop(0)
            if node == self.goal:
                return True
            if node in visited:
                continue
            visited.add(node)
            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        return False  # exhausted all reachable nodes, goal not found

    # Debug helper - print to console
    def print_grid(self):
        symbols = {EMPTY: '.', OBSTACLE: '#', START: 'S', GOAL: 'G'}
        for r in range(self.rows):
            row_str = ''
            for c in range(self.cols):
                row_str += symbols[self.grid[r][c]] + ' '
            print(row_str)
        print(f"Start: {self.start}  |  Goal: {self.goal}")
        print(f"Obstacles: {len(self.obstacles)} / {self.rows * self.cols} cells")
