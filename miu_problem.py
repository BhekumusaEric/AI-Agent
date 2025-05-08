"""
MIU Problem Module

This module defines the MIU problem as a search problem.
"""

from search import Problem
from miu_system import next_states

class MIUProblem(Problem):
    """
    The MIU problem as a search problem.
    
    The MIU problem involves transforming strings according to the MIU system rules.
    """
    
    def __init__(self, initial_state, goal):
        """
        Initialize the MIU problem.
        
        Args:
            initial_state (str): The initial MIU string
            goal (str): The goal MIU string
        """
        super().__init__(initial_state, goal)
    
    def get_successors(self, state):
        """
        Return a list of (action, state) pairs reachable from the given state.
        
        Args:
            state (str): The current MIU string
            
        Returns:
            list: A list of (action, state) pairs
        """
        successors = []
        next_states_list = next_states(state)
        
        # Rule 1: If string ends with 'I', append 'U'
        if state.endswith("I"):
            new_state = state + "U"
            if new_state in next_states_list:
                successors.append(("Rule 1: Append U", new_state))
        
        # Rule 2: If string starts with 'M', duplicate everything after 'M'
        if state.startswith("M"):
            suffix = state[1:]
            new_state = "M" + suffix + suffix
            if new_state in next_states_list:
                successors.append(("Rule 2: Duplicate after M", new_state))
        
        # Rule 3: Replace "III" with "U"
        idx = 0
        while "III" in state[idx:]:
            i = state.index("III", idx)
            new_state = state[:i] + "U" + state[i+3:]
            if new_state in next_states_list:
                successors.append((f"Rule 3: Replace III with U at position {i}", new_state))
            idx = i + 1
        
        # Rule 4: Remove "UU"
        idx = 0
        while "UU" in state[idx:]:
            i = state.index("UU", idx)
            new_state = state[:i] + state[i+2:]
            if new_state in next_states_list:
                successors.append((f"Rule 4: Remove UU at position {i}", new_state))
            idx = i + 1
        
        return successors
    
    def is_goal(self, state):
        """
        Return True if the state is the goal state.
        
        Args:
            state (str): The state to check
            
        Returns:
            bool: True if the state is the goal state
        """
        return state == self.goal
    
    def get_cost(self, state, action, next_state):
        """
        Return the cost of taking action from state to reach next_state.
        
        Args:
            state (str): The current state
            action (str): The action to take
            next_state (str): The resulting state
            
        Returns:
            int: The cost of the action
        """
        # All actions have the same cost in the MIU problem
        return 1


def miu_heuristic(state, goal):
    """
    A heuristic function for the MIU problem.
    
    This is a simple heuristic based on the difference in length and character counts.
    
    Args:
        state (str): The current state
        goal (str): The goal state
        
    Returns:
        int: An estimate of the cost to reach the goal
    """
    if not goal:
        return 0
    
    # Length difference
    length_diff = abs(len(state) - len(goal))
    
    # Character count differences
    state_counts = {'M': state.count('M'), 'I': state.count('I'), 'U': state.count('U')}
    goal_counts = {'M': goal.count('M'), 'I': goal.count('I'), 'U': goal.count('U')}
    
    char_diff = sum(abs(state_counts[c] - goal_counts[c]) for c in 'MIU')
    
    return length_diff + char_diff
