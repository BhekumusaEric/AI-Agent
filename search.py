"""
Search Algorithms Module

This module implements various search algorithms for finding paths in a state space.
"""

from collections import deque
import heapq

class Node:
    """A node in the search tree/graph."""
    
    def __init__(self, state, parent=None, action=None, path_cost=0):
        """
        Create a search node.
        
        Args:
            state: The state represented by this node
            parent (Node): The node that generated this node
            action: The action that got us from parent to this node
            path_cost (int): The total cost of the path from the initial state to this node
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1
    
    def __lt__(self, other):
        """Comparison operator for priority queue."""
        return self.path_cost < other.path_cost
    
    def expand(self, problem):
        """Return a list of nodes reachable from this node."""
        return [self.child_node(problem, action, next_state)
                for action, next_state in problem.get_successors(self.state)]
    
    def child_node(self, problem, action, next_state):
        """Create a child node."""
        return Node(next_state, self, action, 
                   self.path_cost + problem.get_cost(self.state, action, next_state))
    
    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]
    
    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))
    
    def __eq__(self, other):
        """Nodes are equal if they represent the same state."""
        return isinstance(other, Node) and self.state == other.state
    
    def __hash__(self):
        """Hash value of a node is the hash value of its state."""
        return hash(self.state)


class Problem:
    """The abstract class for a formal problem."""
    
    def __init__(self, initial_state, goal=None):
        """Constructor."""
        self.initial_state = initial_state
        self.goal = goal
    
    def get_successors(self, state):
        """
        Return a list of (action, state) pairs reachable from the given state.
        
        Args:
            state: The current state
            
        Returns:
            list: A list of (action, state) pairs
        """
        raise NotImplementedError
    
    def is_goal(self, state):
        """
        Return True if the state is a goal state.
        
        Args:
            state: The state to check
            
        Returns:
            bool: True if the state is a goal state
        """
        return state == self.goal
    
    def get_cost(self, state, action, next_state):
        """
        Return the cost of taking action from state to reach next_state.
        
        Args:
            state: The current state
            action: The action to take
            next_state: The resulting state
            
        Returns:
            int: The cost of the action
        """
        return 1  # Default is uniform cost


def breadth_first_search(problem, max_iterations=1000):
    """
    Breadth-first search algorithm.
    
    Args:
        problem (Problem): The problem to solve
        max_iterations (int): Maximum number of iterations
        
    Returns:
        tuple: (solution_node, visited_nodes, iterations)
    """
    node = Node(problem.initial_state)
    if problem.is_goal(node.state):
        return node, [node], 0
    
    frontier = deque([node])
    explored = set()
    visited_nodes = [node]
    iterations = 0
    
    while frontier and iterations < max_iterations:
        iterations += 1
        node = frontier.popleft()
        explored.add(node.state)
        
        for child in node.expand(problem):
            visited_nodes.append(child)
            if problem.is_goal(child.state):
                return child, visited_nodes, iterations
            if child.state not in explored and child not in frontier:
                frontier.append(child)
    
    return None, visited_nodes, iterations


def depth_first_search(problem, max_depth=50, max_iterations=1000):
    """
    Depth-first search algorithm.
    
    Args:
        problem (Problem): The problem to solve
        max_depth (int): Maximum depth to search
        max_iterations (int): Maximum number of iterations
        
    Returns:
        tuple: (solution_node, visited_nodes, iterations)
    """
    node = Node(problem.initial_state)
    if problem.is_goal(node.state):
        return node, [node], 0
    
    frontier = [node]
    explored = set()
    visited_nodes = [node]
    iterations = 0
    
    while frontier and iterations < max_iterations:
        iterations += 1
        node = frontier.pop()
        explored.add(node.state)
        
        if node.depth < max_depth:
            for child in node.expand(problem):
                visited_nodes.append(child)
                if problem.is_goal(child.state):
                    return child, visited_nodes, iterations
                if child.state not in explored and child not in frontier:
                    frontier.append(child)
    
    return None, visited_nodes, iterations


def a_star_search(problem, heuristic, max_iterations=1000):
    """
    A* search algorithm.
    
    Args:
        problem (Problem): The problem to solve
        heuristic (function): A function that estimates the cost from a state to the goal
        max_iterations (int): Maximum number of iterations
        
    Returns:
        tuple: (solution_node, visited_nodes, iterations)
    """
    node = Node(problem.initial_state)
    if problem.is_goal(node.state):
        return node, [node], 0
    
    frontier = [(node.path_cost + heuristic(node.state, problem.goal), node)]
    explored = set()
    visited_nodes = [node]
    iterations = 0
    
    while frontier and iterations < max_iterations:
        iterations += 1
        _, node = heapq.heappop(frontier)
        
        if problem.is_goal(node.state):
            return node, visited_nodes, iterations
        
        explored.add(node.state)
        
        for child in node.expand(problem):
            visited_nodes.append(child)
            if child.state not in explored and child not in [n for _, n in frontier]:
                heapq.heappush(frontier, (child.path_cost + heuristic(child.state, problem.goal), child))
            elif child in [n for _, n in frontier]:
                # If child is in frontier with higher path_cost, replace it
                for i, (f, n) in enumerate(frontier):
                    if n.state == child.state:
                        if f > child.path_cost + heuristic(child.state, problem.goal):
                            frontier[i] = (child.path_cost + heuristic(child.state, problem.goal), child)
                            heapq.heapify(frontier)
                        break
    
    return None, visited_nodes, iterations
