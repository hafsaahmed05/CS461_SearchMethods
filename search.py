from collections import deque

# Shared helper — walks the parent dict backwards to build the path
def reconstruct_path(parent, start, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path if path[0] == start else []

def bfs(grid_env):
    start = grid_env.start
    goal  = grid_env.goal
    graph = grid_env.adjacency
    frontier = deque([start])
    visited  = set()
    parent   = {start: None}

    while frontier:
        current = frontier.popleft()

        if current in visited:
            continue

        visited.add(current)

        # hand current state to the visualizer
        yield {
            'current'  : current,
            'frontier' : list(frontier),
            'visited'  : set(visited),
            'parent'   : dict(parent),
            'found'    : current == goal
        }

        if current == goal:
            return

        for neighbor in graph.get(current, []):
            if neighbor not in visited and neighbor not in frontier:
                parent[neighbor] = current
                frontier.append(neighbor)