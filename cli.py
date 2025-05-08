"""
Command-Line Interface for AI Agent

This module implements a command-line interface for the AI agent.
"""

import time

from miu_system import next_states, is_valid_miu_string
from miu_problem import MIUProblem, miu_heuristic
from maze_environment import Maze, MazeProblem, manhattan_distance
from search import breadth_first_search, depth_first_search, a_star_search

class AIAgentCLI:
    """Command-Line Interface for the AI Agent."""

    def __init__(self):
        """Initialize the CLI."""
        pass

    def run(self):
        """Run the CLI."""
        print("=" * 50)
        print("AI Agent Command-Line Interface")
        print("=" * 50)

        while True:
            print("\nSelect an environment:")
            print("1. MIU System")
            print("2. Maze Environment")
            print("0. Exit")

            choice = input("Enter your choice (0-2): ")

            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                self.run_miu_system()
            elif choice == "2":
                self.run_maze_environment()
            else:
                print("Invalid choice. Please try again.")

    def run_miu_system(self):
        """Run the MIU System environment."""
        print("\n" + "=" * 50)
        print("MIU System")
        print("=" * 50)

        # Get input parameters
        initial_state = input("Enter initial state (default: MI): ") or "MI"
        goal_state = input("Enter goal state (default: MU): ") or "MU"

        if not is_valid_miu_string(initial_state) or not is_valid_miu_string(goal_state):
            print("Error: Initial and goal states must be valid MIU strings.")
            return

        print("\nSelect search algorithm:")
        print("1. Breadth-First Search (BFS)")
        print("2. Depth-First Search (DFS)")
        print("3. A* Search")

        algorithm_choice = input("Enter your choice (1-3): ")

        max_iterations = int(input("Enter maximum iterations (default: 1000): ") or "1000")

        # Create the problem
        problem = MIUProblem(initial_state, goal_state)

        # Run the search algorithm
        print(f"\nStarting search from {initial_state} to {goal_state}...")

        if algorithm_choice == "1":
            print("Using Breadth-First Search (BFS)")
            solution, visited_nodes, iterations = breadth_first_search(problem, max_iterations)
        elif algorithm_choice == "2":
            print("Using Depth-First Search (DFS)")
            solution, visited_nodes, iterations = depth_first_search(problem, max_iterations=max_iterations)
        elif algorithm_choice == "3":
            print("Using A* Search")
            solution, visited_nodes, iterations = a_star_search(problem, miu_heuristic, max_iterations)
        else:
            print("Invalid choice. Using BFS as default.")
            solution, visited_nodes, iterations = breadth_first_search(problem, max_iterations)

        # Display results
        if solution:
            print(f"\nSolution found in {iterations} iterations!")
            print("Path:")

            path = solution.path()
            for i, node in enumerate(path):
                if i > 0:
                    print(f"  {i}. {node.action} -> {node.state}")
                else:
                    print(f"  {i}. Start: {node.state}")
        else:
            print(f"\nNo solution found after {iterations} iterations.")

        print("\nNote: Visualization is disabled in this version.")

    def run_maze_environment(self):
        """Run the Maze Environment."""
        print("\n" + "=" * 50)
        print("Maze Environment")
        print("=" * 50)

        # Get maze parameters
        width = int(input("Enter maze width (default: 10): ") or "10")
        height = int(input("Enter maze height (default: 10): ") or "10")
        wall_prob = float(input("Enter wall probability (0-1, default: 0.3): ") or "0.3")
        seed = int(input("Enter random seed (default: 42): ") or "42")

        if width <= 0 or height <= 0 or wall_prob < 0 or wall_prob > 1:
            print("Error: Invalid maze parameters.")
            return

        # Generate the maze
        print("\nGenerating maze...")
        maze = Maze(width, height, wall_prob, seed)

        # Display the maze
        print("\nMaze:")
        print(maze)

        # Get search algorithm
        print("\nSelect search algorithm:")
        print("1. Breadth-First Search (BFS)")
        print("2. Depth-First Search (DFS)")
        print("3. A* Search")

        algorithm_choice = input("Enter your choice (1-3): ")

        # Create the problem
        problem = MazeProblem(maze)

        # Run the search algorithm
        print("\nStarting search...")

        if algorithm_choice == "1":
            print("Using Breadth-First Search (BFS)")
            solution, visited_nodes, iterations = breadth_first_search(problem)
        elif algorithm_choice == "2":
            print("Using Depth-First Search (DFS)")
            solution, visited_nodes, iterations = depth_first_search(problem)
        elif algorithm_choice == "3":
            print("Using A* Search")
            solution, visited_nodes, iterations = a_star_search(problem, manhattan_distance)
        else:
            print("Invalid choice. Using A* as default.")
            solution, visited_nodes, iterations = a_star_search(problem, manhattan_distance)

        # Display results
        if solution:
            print(f"\nSolution found in {iterations} iterations!")
            print(f"Path length: {len(solution.path()) - 1} steps")

            # Ask if user wants to see the path
            show_path = input("\nShow the path? (y/n): ").lower() == 'y'
            if show_path:
                path = solution.path()
                for i, node in enumerate(path):
                    if i > 0:
                        print(f"  {i}. {node.action} -> {node.state}")
                    else:
                        print(f"  {i}. Start: {node.state}")
        else:
            print(f"\nNo solution found after {iterations} iterations.")

        print("\nNote: Visualization is disabled in this version.")


def main():
    """Main function."""
    cli = AIAgentCLI()
    cli.run()


if __name__ == "__main__":
    main()
