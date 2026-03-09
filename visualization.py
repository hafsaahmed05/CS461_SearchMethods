import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import time

# Color palette for grid cells
COLORS = {
    'empty'    : 'white',
    'obstacle' : 'black',
    'visited'  : 'slategray',
    'frontier' : 'dodgerblue',
    'current'  : 'orange',
    'start'    : 'lime',
    'goal'     : 'red',
    'path'     : 'yellow',
    'grid_line': 'lightgray',
}


class Visualizer:
    def __init__(self, env, speed=0.1):
        self.env   = env
        self.speed = speed

        self.tree = nx.DiGraph()
        self.tree.add_node(env.start)

        self.fig, (self.ax_grid, self.ax_tree) = plt.subplots(
            1, 2, figsize=(14, 7)
        )
        self.fig.patch.set_facecolor('white')
        self.fig.suptitle("2D Path Search Visualizer", color='black', fontsize=14)

        plt.ion()

    # Main loop — steps through the generator, redraws each frame
    # Returns the final state snapshot for main.py to use
    def run(self, search_gen):
        final_state = None

        for state in search_gen:
            final_state = state
            self._update_tree(state)
            self._draw(state, path=[])
            plt.pause(self.speed)
            if state['found']:
                break

        if final_state['found']:
            from search import reconstruct_path
            path = reconstruct_path(final_state['parent'], self.env.start, self.env.goal)
        else:
            path = []

        self._draw(final_state, path=path)
        plt.ioff()
        plt.show()
        return final_state

    # Add newly discovered nodes/edges to the search tree
    def _update_tree(self, state):
        parent = state['parent']
        current = state['current']

        # Add current node and its parent edge to tree
        if current and current in parent:
            self.tree.add_node(current)
            if parent[current] is not None:
                self.tree.add_edge(parent[current], current)

        # Add frontier nodes as pending children
        for node in state['frontier']:
            if node in parent and parent[node] is not None:
                self.tree.add_node(node)
                self.tree.add_edge(parent[node], node)

    # Draw both subplots
    def _draw(self, state, path=[], final=False):
        self.ax_grid.cla()
        self.ax_tree.cla()
        self._draw_grid(state, path)
        self._draw_tree(state, path)
        self.fig.tight_layout(rect=[0, 0, 0.85, 1])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    # Left subplot — 2D grid
    def _draw_grid(self, state, path):
        env      = self.env
        ax       = self.ax_grid
        visited  = state['visited']
        frontier = set(state['frontier'])
        current  = state['current']
        path_set = set(path)

        # axis setup
        ax.set_facecolor(COLORS['empty'])
        ax.set_xlim(0, env.cols)
        ax.set_ylim(0, env.rows)
        ax.set_aspect('equal')
        ax.set_title("Grid View", color='black', fontsize=11)
        ax.tick_params(colors='black')

        for r in range(env.rows):
            for c in range(env.cols):
                node = (r, c)

                # figure out what color this cell should be
                if node in env.obstacles:
                    color = COLORS['obstacle']
                elif node == env.start:
                    color = COLORS['start']
                elif node == env.goal:
                    color = COLORS['goal']
                elif node in path_set:
                    color = COLORS['path']
                elif node == current:
                    color = COLORS['current']
                elif node in frontier:
                    color = COLORS['frontier']
                elif node in visited:
                    color = COLORS['visited']
                else:
                    color = COLORS['empty']

                # draw the cell — flip y so row 0 appears at top
                rect = plt.Rectangle(
                    (c, env.rows - r - 1), 1, 1,
                    color=color,
                    ec=COLORS['grid_line'],
                    lw=0.5
                )
                ax.add_patch(rect)

                # label start and goal cells
                if node == env.start:
                    ax.text(c + 0.5, env.rows - r - 0.5, 'S',
                            ha='center', va='center',
                            color='white', fontsize=9, fontweight='bold')
                elif node == env.goal:
                    ax.text(c + 0.5, env.rows - r - 0.5, 'G',
                            ha='center', va='center',
                            color='white', fontsize=9, fontweight='bold')

        # Legend
        legend_items = [
            mpatches.Patch(color=COLORS['start'],    label='Start'),
            mpatches.Patch(color=COLORS['goal'],     label='Goal'),
            mpatches.Patch(color=COLORS['obstacle'], label='Obstacle'),
            mpatches.Patch(color=COLORS['visited'],  label='Visited'),
            mpatches.Patch(color=COLORS['frontier'], label='Frontier'),
            mpatches.Patch(color=COLORS['current'],  label='Current'),
            mpatches.Patch(color=COLORS['path'],     label='Path'),
        ]
        ax.legend(handles=legend_items, loc='upper left',
          bbox_to_anchor=(1.01, 1),    
          fontsize=7, facecolor='white', labelcolor='black',
          framealpha=0.8)

    # Right subplot — inverted search tree
    def _draw_tree(self, state, path):
        ax      = self.ax_tree
        tree    = self.tree
        current = state['current']
        path_set = set(zip(path, path[1:])) if len(path) > 1 else set()

        ax.set_facecolor('whitesmoke')
        ax.set_title("Search Tree", color='white', fontsize=11)
        ax.axis('off')

        if len(tree.nodes) == 0:
            return

        # Compute a top-down hierarchical layout
        pos = self._tree_layout(tree, self.env.start)

        # Color each node
        node_colors = []
        for node in tree.nodes:
            if node == self.env.start:
                node_colors.append(COLORS['start'])
            elif node == self.env.goal:
                node_colors.append(COLORS['goal'])
            elif node == current:
                node_colors.append(COLORS['current'])
            elif node in state['visited']:
                node_colors.append(COLORS['visited'])
            else:
                node_colors.append(COLORS['frontier'])

        # Color path edges differently
        edge_colors = []
        for u, v in tree.edges:
            if (u, v) in path_set or (v, u) in path_set:
                edge_colors.append(COLORS['path'])
            else:
                edge_colors.append('dimgray')

        nx.draw(
            tree, pos, ax=ax,
            node_color=node_colors,
            edge_color=edge_colors,
            node_size=120,
            font_size=5,
            font_color='white',
            arrows=True,
            arrowsize=8,
            width=1.2,
            labels={n: f"{n[0]},{n[1]}" for n in tree.nodes}
        )

    # Hierarchical top-down layout for the tree
    # Assigns (x, y) positions based on depth and sibling order
    def _tree_layout(self, tree, root):
        pos = {}
        # BFS to assign depth levels
        from collections import deque
        queue   = deque([(root, 0)])
        visited = set()
        levels  = {}   # depth -> [nodes]

        while queue:
            node, depth = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            levels.setdefault(depth, []).append(node)
            for child in tree.successors(node):
                if child not in visited:
                    queue.append((child, depth + 1))

        # Assign x evenly across each level, y based on depth (inverted)
        max_depth = max(levels.keys()) if levels else 0
        for depth, nodes in levels.items():
            for i, node in enumerate(nodes):
                x = (i + 1) / (len(nodes) + 1)
                y = 1.0 - (depth / (max_depth + 1))  # inverted: root at top
                pos[node] = (x, y)

        return pos