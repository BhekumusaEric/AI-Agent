# AI-Agent
# Enhanced AI Agent with GUI
Welcome to the first installment in our series on [Artificial Intelligence], where you'll build your very own AI agent! In this series, you'll learn how AI agents work and gradually develop your agent using the concepts and techniques presented here.

AI agents are practical implementations of AI principles, designed to interact with environments and take actions autonomously.

Creeper in Minecraft can be considered a simple AI agent because it perceives its environment, makes decisions, and takes actions based on its programmed behavior. Such an agent is reactive, meaning it responds immediately to inputs without planning ahead.

In contrast, our focus will be on deliberative AI agents—agents that plan ahead by exploring a search space and systematically finding solutions.

Types of **AI Agents**:

Reactive Agents: Act only on current perceptions (e.g., Reflex AI like thermostats).
Deliberative Agents: Plan ahead, search for solutions (e.g., pathfinding robots).
Learning Agents: Improve over time (e.g., reinforcement learning bots).
Key Components of a Deliberative AI Agent:

Search Space: The environment where the agent looks for solutions.
State: The current situation of the agent (e.g., location in a maze).
Actions: Possible moves that lead to new states.
Goal State: The desired outcome (e.g., reaching the exit).
Search Algorithm: The strategy to find the best solution (e.g., A* search).
In Pac-Man, the Blinky ghost is a deliberative agent because it actively searches for Pac-Man rather than just reacting.

How It Works:

Search Space: The Pac-Man map.
States: Ghost’s current position.
Actions: Moving in four directions.
Goal: Find the shortest path to Pac-Man.
Search Algorithm: Uses A search* to efficiently chase Pac-Man.
Now that you have an idea of what deliberative AI agents are, I will introduce you to the first step of building your own AI agent.

The MIU System

The MIU Puzzle is a formal system introduced in Douglas Hofstadter’s Gödel, Escher, Bach: An Eternal Golden Braid (1979). In the MIU Puzzle, you start with the string "MI" and try to transform it into "MU" using a set of rules. (Fun fact: deriving "MU" from "MI" is actually impossible, but you can generate many other valid strings!)

We are using the MIU system as a foundation for our AI agent. Your future AI agent will search this space of strings—each representing a state—to eventually find a transformation path leading to a specified goal state.

The MIU system is governed by the following rules, which must be applied in the order listed:

Transformation Rules

If a string ends in "I," you may append a "U" at the end: x I → x IU
If a string starts with "M," you can duplicate everything after "M": M x → M x x
If the string contains "III," you can replace it with a "U": x III y → x U y
If the string contains "UU," you can remove it entirely: x UU y → x y
Now, let's proceed to your first step.

The Kata Task: Expanding the Search Space
Usually, AI agents don't keep the entire search space in the memory. As you can imagine, the search space can be extremely large and it will be hard to hold it entirely in the active memory. Therefore, you are going to expand your search space step by step until you find the goal.

Your First Task: Implement the next_states(s) Function

Your task is to implement the function next_states(s) which takes a string s as input and returns a list of all possible strings that can be generated from s in a single step by applying the MIU system rules.

Ordering of Results:

The results must be returned in the order of rule application:

First, include the result of Rule 1 (if applicable).
Next, include the result of Rule 2.
Then, include the results from applying Rule 3 (in order of appearance within the string).
Finally, include the results from applying Rule 4 (again, in order of appearance).
For example, for the input "MI", the function should return:

next_states("MI") → ["MIU", "MII"]

Note on Duplicates:

You need to remove all duplicates across all rules. You must ensure that if the same transformation produces the same result multiple times, it is added only once in order of appearence.Also, if the string has been already added by , say rule 3, and you generate same in rule 4, you must drop it, as well.

Examples:

next_states("MI") → ["MIU", "MII"]
next_states("MIU") → ["MIUIU"]
next_states("MUI") → ["MUIU", "MUIUI"]
next_states("MIIII") → ["MIIIIU", "MIIIIIIII", "MUI", "MIU"]
next_states("MUUII") → ["MUUIIU", "MUUIIUUII", "MII"]
next_states("MUUUI") → ["MUUUIU", "MUUUIUUUI", "MUI"]
This function is the foundation upon which you'll build more advanced search strategies in future katas. It lets your AI agent explore the MIU search space incrementally, without needing to load all possible states into memory at once.

## Enhanced AI Agent Features

This enhanced version of the AI Agent includes:

1. **Command-Line Interface (CLI)**: A user-friendly interface that allows you to:
   - Configure search parameters
   - Interact with different environments
   - View search results in text format

2. **Multiple Search Algorithms**:
   - Breadth-First Search (BFS)
   - Depth-First Search (DFS)
   - A* Search with heuristics

3. **Multiple Environments**:
   - MIU System: Explore string transformations
   - Maze Environment: Navigate through randomly generated mazes

4. **Visualization Tools**:
   - Graph visualization for the MIU system
   - Grid visualization for mazes
   - Path highlighting for solutions

## Getting Started

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the demo to see the AI agent in action:
   ```
   python3 demo.py
   ```

3. Run the interactive CLI:
   ```
   python3 main.py
   ```

4. Use the CLI to:
   - Select an environment (MIU System or Maze)
   - Configure parameters
   - Choose a search algorithm
   - Start the search and view the results

## Project Structure

- `main.py`: Entry point for the application
- `cli.py`: Command-line interface implementation
- `demo.py`: Demonstration script with predefined examples
- `miu_system.py`: Implementation of the MIU formal system
- `search.py`: Search algorithms (BFS, DFS, A*)
- `miu_problem.py`: MIU problem definition
- `maze_environment.py`: Maze environment implementation
