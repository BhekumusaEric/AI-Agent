"""
Demo script for the AI Agent.

This script demonstrates the AI agent's capabilities by running predefined examples.
"""

from miu_system import next_states
from miu_problem import MIUProblem, miu_heuristic
from maze_environment import Maze, MazeProblem, manhattan_distance
from search import breadth_first_search, depth_first_search, a_star_search

def demo_miu_system():
    """Demonstrate the MIU system."""
    print("\n" + "=" * 50)
    print("MIU System Demonstration")
    print("=" * 50)
    
    # Demonstrate next_states function
    print("\nDemonstrating next_states function:")
    examples = ["MI", "MIU", "MUI", "MIIII", "MUUII", "MUUUI"]
    
    for example in examples:
        result = next_states(example)
        print(f"next_states(\"{example}\") → {result}")
    
    # Demonstrate search algorithms
    print("\nDemonstrating search algorithms:")
    
    initial_state = "MI"
    goal_state = "MIU"
    
    print(f"\nSearching from {initial_state} to {goal_state}:")
    problem = MIUProblem(initial_state, goal_state)
    
    # BFS
    print("\nUsing Breadth-First Search (BFS):")
    solution, visited_nodes, iterations = breadth_first_search(problem)
    
    if solution:
        print(f"Solution found in {iterations} iterations!")
        print("Path:")
        
        path = solution.path()
        for i, node in enumerate(path):
            if i > 0:
                print(f"  {i}. {node.action} -> {node.state}")
            else:
                print(f"  {i}. Start: {node.state}")
    else:
        print(f"No solution found after {iterations} iterations.")
    
    # Try a more complex example
    initial_state = "MI"
    goal_state = "MIUIU"
    
    print(f"\nSearching from {initial_state} to {goal_state}:")
    problem = MIUProblem(initial_state, goal_state)
    
    # A*
    print("\nUsing A* Search:")
    solution, visited_nodes, iterations = a_star_search(problem, miu_heuristic)
    
    if solution:
        print(f"Solution found in {iterations} iterations!")
        print("Path:")
        
        path = solution.path()
        for i, node in enumerate(path):
            if i > 0:
                print(f"  {i}. {node.action} -> {node.state}")
            else:
                print(f"  {i}. Start: {node.state}")
    else:
        print(f"No solution found after {iterations} iterations.")


def demo_maze_environment():
    """Demonstrate the maze environment."""
    print("\n" + "=" * 50)
    print("Maze Environment Demonstration")
    print("=" * 50)
    
    # Create a small maze
    width, height = 5, 5
    wall_prob = 0.2
    seed = 42
    
    print(f"\nGenerating a {width}x{height} maze with wall probability {wall_prob}...")
    maze = Maze(width, height, wall_prob, seed)
    
    # Display the maze
    print("\nMaze:")
    print(maze)
    
    # Create the problem
    problem = MazeProblem(maze)
    
    # Run different search algorithms
    algorithms = [
        ("Breadth-First Search (BFS)", breadth_first_search),
        ("Depth-First Search (DFS)", depth_first_search),
        ("A* Search", lambda p: a_star_search(p, manhattan_distance))
    ]
    
    for name, algorithm in algorithms:
        print(f"\nUsing {name}:")
        solution, visited_nodes, iterations = algorithm(problem)
        
        if solution:
            print(f"Solution found in {iterations} iterations!")
            print(f"Path length: {len(solution.path()) - 1} steps")
            
            # Show the first few steps of the path
            path = solution.path()
            print("First few steps:")
            for i, node in enumerate(path[:5]):
                if i > 0:
                    print(f"  {i}. {node.action} -> {node.state}")
                else:
                    print(f"  {i}. Start: {node.state}")
            
            if len(path) > 5:
                print(f"  ... ({len(path) - 5} more steps)")
        else:
            print(f"No solution found after {iterations} iterations.")


def main():
    """Main function."""
    print("=" * 50)
    print("AI Agent Demonstration")
    print("=" * 50)
    
    print("\nThis demo will showcase the AI agent's capabilities in two environments:")
    print("1. MIU System - A formal system with string transformation rules")
    print("2. Maze Environment - A grid-based pathfinding problem")
    
    # Demonstrate MIU system
    demo_miu_system()
    
    # Demonstrate maze environment
    demo_maze_environment()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("=" * 50)
    print("\nTo explore more, run 'python main.py' for the interactive CLI.")


if __name__ == "__main__":
    main()
