"""
Maze Environment Module

This module implements a maze environment for the AI agent.
"""

import random
from search import Problem

class Maze:
    """A maze environment."""
    
    def __init__(self, width, height, wall_probability=0.3, seed=None):
        """
        Create a maze.
        
        Args:
            width (int): The width of the maze
            height (int): The height of the maze
            wall_probability (float): The probability of a cell being a wall
            seed (int): Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Generate random walls
        for y in range(height):
            for x in range(width):
                if random.random() < wall_probability:
                    self.grid[y][x] = '#'
        
        # Ensure start and goal are not walls
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)
        self.grid[self.start[1]][self.start[0]] = 'S'
        self.grid[self.goal[1]][self.goal[0]] = 'G'
    
    def is_valid_position(self, x, y):
        """
        Check if a position is valid (within bounds and not a wall).
        
        Args:
            x (int): The x-coordinate
            y (int): The y-coordinate
            
        Returns:
            bool: True if the position is valid
        """
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] != '#')
    
    def get_neighbors(self, x, y):
        """
        Get the valid neighboring positions.
        
        Args:
            x (int): The x-coordinate
            y (int): The y-coordinate
            
        Returns:
            list: A list of valid neighboring positions (x, y)
        """
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def __str__(self):
        """Return a string representation of the maze."""
        return '\n'.join(''.join(row) for row in self.grid)


class MazeProblem(Problem):
    """The maze problem as a search problem."""
    
    def __init__(self, maze):
        """
        Initialize the maze problem.
        
        Args:
            maze (Maze): The maze
        """
        super().__init__(maze.start, maze.goal)
        self.maze = maze
    
    def get_successors(self, state):
        """
        Return a list of (action, state) pairs reachable from the given state.
        
        Args:
            state (tuple): The current position (x, y)
            
        Returns:
            list: A list of (action, state) pairs
        """
        x, y = state
        successors = []
        
        for nx, ny in self.maze.get_neighbors(x, y):
            if (nx, ny) == (x + 1, y):
                action = "Right"
            elif (nx, ny) == (x - 1, y):
                action = "Left"
            elif (nx, ny) == (x, y + 1):
                action = "Down"
            else:  # (nx, ny) == (x, y - 1)
                action = "Up"
            
            successors.append((action, (nx, ny)))
        
        return successors
    
    def is_goal(self, state):
        """
        Return True if the state is the goal state.
        
        Args:
            state (tuple): The state to check
            
        Returns:
            bool: True if the state is the goal state
        """
        return state == self.goal
    
    def get_cost(self, state, action, next_state):
        """
        Return the cost of taking action from state to reach next_state.
        
        Args:
            state (tuple): The current state
            action (str): The action to take
            next_state (tuple): The resulting state
            
        Returns:
            int: The cost of the action
        """
        # All actions have the same cost in this maze
        return 1


def manhattan_distance(state, goal):
    """
    Calculate the Manhattan distance between two points.
    
    Args:
        state (tuple): The current position (x, y)
        goal (tuple): The goal position (x, y)
        
    Returns:
        int: The Manhattan distance
    """
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
