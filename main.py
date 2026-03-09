import argparse
from grid import GridEnvironment
from search import bfs, reconstruct_path
from visualization import Visualizer

def get_args():
    parser = argparse.ArgumentParser(description="2D Path Search Visualizer")
    parser.add_argument("--rows",      type=int,   default=10,    help="Number of rows (default: 10)")
    parser.add_argument("--cols",      type=int,   default=10,    help="Number of cols (default: 10)")
    parser.add_argument("--obstacles", type=float, default=0.25,  help="Obstacle density 0.20-0.30 (default: 0.25)")
    parser.add_argument("--method",    type=str,   default="bfs", choices=["bfs", "dfs"], help="Search method (default: bfs)")
    parser.add_argument("--speed",     type=float, default=1.0,   help="Seconds between frames (default: 1.0)")
    return parser.parse_args()

def main():
    args = get_args()

    # Clamp obstacle density to assignment range
    if not (0.20 <= args.obstacles <= 0.30):
        print(f"Warning: obstacle density {args.obstacles} outside 0.20-0.30. Clamping.")
        args.obstacles = max(0.20, min(0.30, args.obstacles))

    print(f"\nGenerating {args.rows}x{args.cols} grid | "
          f"Obstacles: {args.obstacles:.0%} | "
          f"Method: {args.method.upper()}")

    # Build environment
    env = GridEnvironment(rows=args.rows, cols=args.cols, obstacle_pct=args.obstacles)
    env.print_grid()
    print(f"\nStart: {env.start}  |  Goal: {env.goal}")

    # Pick search generator
    search_gen = bfs(env)

    # Run visualizer - blocks until window is closed
    viz = Visualizer(env, speed=args.speed)
    final_state = viz.run(search_gen)

    # Report results
    print("\n--- Search Complete ---")
    if final_state and final_state['found']:
        path = reconstruct_path(final_state['parent'], env.start, env.goal)
        print(f"Goal found!")
        print(f"Path length   : {len(path)} steps")
        print(f"Nodes explored: {len(final_state['visited'])}")
        print(f"Path          : {path}")
    else:
        print("Goal not reachable. No valid path exists.")
        if final_state:
            print(f"Nodes explored: {len(final_state['visited'])}")

if __name__ == "__main__":
    main()