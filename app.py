"""
Web interface for the AI Agent.

This module implements a web interface using Flask for the AI agent.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64
from datetime import datetime

from miu_system import next_states, is_valid_miu_string
from miu_problem import MIUProblem, miu_heuristic
from maze_environment import Maze, MazeProblem, manhattan_distance
from search import breadth_first_search, depth_first_search, a_star_search

app = Flask(__name__)

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/api/miu/next_states', methods=['POST'])
def api_miu_next_states():
    """API endpoint for getting next states in the MIU system."""
    data = request.get_json()
    state = data.get('state', 'MI')
    
    if not is_valid_miu_string(state):
        return jsonify({'error': 'Invalid MIU string'})
    
    result = next_states(state)
    return jsonify({'next_states': result})

@app.route('/api/miu/search', methods=['POST'])
def api_miu_search():
    """API endpoint for running a search in the MIU system."""
    data = request.get_json()
    initial_state = data.get('initial_state', 'MI')
    goal_state = data.get('goal_state', 'MU')
    algorithm = data.get('algorithm', 'bfs')
    max_iterations = int(data.get('max_iterations', 1000))
    
    if not is_valid_miu_string(initial_state) or not is_valid_miu_string(goal_state):
        return jsonify({'error': 'Invalid MIU string'})
    
    # Create the problem
    problem = MIUProblem(initial_state, goal_state)
    
    # Run the search algorithm
    if algorithm == 'bfs':
        solution, visited_nodes, iterations = breadth_first_search(problem, max_iterations)
    elif algorithm == 'dfs':
        solution, visited_nodes, iterations = depth_first_search(problem, max_iterations=max_iterations)
    elif algorithm == 'astar':
        solution, visited_nodes, iterations = a_star_search(problem, miu_heuristic, max_iterations)
    else:
        return jsonify({'error': 'Invalid algorithm'})
    
    # Prepare the result
    result = {
        'iterations': iterations,
        'visited_nodes_count': len(visited_nodes),
        'solution_found': solution is not None
    }
    
    if solution:
        path = solution.path()
        result['path_length'] = len(path) - 1
        result['path'] = []
        
        for i, node in enumerate(path):
            if i > 0:
                result['path'].append({
                    'step': i,
                    'action': node.action,
                    'state': node.state
                })
            else:
                result['path'].append({
                    'step': i,
                    'action': 'Start',
                    'state': node.state
                })
    
    # Generate a visualization of the search
    graph_image = generate_miu_graph(visited_nodes, solution)
    result['graph_image'] = graph_image
    
    return jsonify(result)

@app.route('/api/maze/generate', methods=['POST'])
def api_maze_generate():
    """API endpoint for generating a maze."""
    data = request.get_json()
    width = int(data.get('width', 10))
    height = int(data.get('height', 10))
    wall_prob = float(data.get('wall_prob', 0.3))
    seed = int(data.get('seed', 42))
    
    if width <= 0 or height <= 0 or wall_prob < 0 or wall_prob > 1:
        return jsonify({'error': 'Invalid maze parameters'})
    
    # Generate the maze
    maze = Maze(width, height, wall_prob, seed)
    
    # Convert the maze to a 2D array for JSON
    maze_grid = []
    for y in range(maze.height):
        row = []
        for x in range(maze.width):
            row.append(maze.grid[y][x])
        maze_grid.append(row)
    
    # Generate a visualization of the maze
    maze_image = generate_maze_image(maze)
    
    return jsonify({
        'width': maze.width,
        'height': maze.height,
        'grid': maze_grid,
        'start': maze.start,
        'goal': maze.goal,
        'maze_image': maze_image
    })

@app.route('/api/maze/search', methods=['POST'])
def api_maze_search():
    """API endpoint for running a search in a maze."""
    data = request.get_json()
    grid = data.get('grid', [])
    start = tuple(data.get('start', [0, 0]))
    goal = tuple(data.get('goal', [len(grid[0])-1, len(grid)-1]))
    algorithm = data.get('algorithm', 'astar')
    
    if not grid:
        return jsonify({'error': 'Invalid maze grid'})
    
    # Recreate the maze from the grid
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    maze = Maze(width, height, 0, 42)  # Seed doesn't matter here
    maze.grid = grid
    maze.start = start
    maze.goal = goal
    
    # Create the problem
    problem = MazeProblem(maze)
    
    # Run the search algorithm
    if algorithm == 'bfs':
        solution, visited_nodes, iterations = breadth_first_search(problem)
    elif algorithm == 'dfs':
        solution, visited_nodes, iterations = depth_first_search(problem)
    elif algorithm == 'astar':
        solution, visited_nodes, iterations = a_star_search(problem, manhattan_distance)
    else:
        return jsonify({'error': 'Invalid algorithm'})
    
    # Prepare the result
    result = {
        'iterations': iterations,
        'visited_nodes_count': len(visited_nodes),
        'solution_found': solution is not None
    }
    
    if solution:
        path = solution.path()
        result['path_length'] = len(path) - 1
        result['path'] = []
        
        for i, node in enumerate(path):
            if i > 0:
                result['path'].append({
                    'step': i,
                    'action': node.action,
                    'state': node.state
                })
            else:
                result['path'].append({
                    'step': i,
                    'action': 'Start',
                    'state': node.state
                })
    
    # Generate a visualization of the maze with the solution path
    maze_solution_image = generate_maze_solution(maze, solution, visited_nodes)
    result['maze_solution_image'] = maze_solution_image
    
    return jsonify(result)

def generate_miu_graph(visited_nodes, solution):
    """
    Generate a visualization of the MIU search graph.
    
    Args:
        visited_nodes (list): List of visited nodes
        solution (Node): The solution node, or None if no solution was found
        
    Returns:
        str: Base64-encoded PNG image
    """
    # Build the graph
    graph = nx.DiGraph()
    for node in visited_nodes:
        if node.parent:
            graph.add_edge(node.parent.state, node.state)
    
    # Use spring layout for small graphs, shell layout for larger ones
    if len(graph) < 20:
        pos = nx.spring_layout(graph)
    else:
        pos = nx.shell_layout(graph)
    
    plt.figure(figsize=(10, 8))
    
    # Draw the graph
    nx.draw(graph, pos, with_labels=True, 
           node_color="lightblue", node_size=500, font_size=8,
           edge_color="gray", arrows=True)
    
    # Highlight the path if a solution is found
    if solution:
        path_states = [n.state for n in solution.path()]
        path_edges = [(path_states[i], path_states[i+1]) for i in range(len(path_states)-1)]
        
        nx.draw_networkx_nodes(graph, pos, nodelist=path_states,
                             node_color="green", node_size=500)
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                             edge_color="green", width=2)
    
    plt.title("MIU System Search Graph")
    
    # Save the figure to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Convert to base64 for embedding in HTML
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Save to a file as well
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"static/images/miu_graph_{timestamp}.png"
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(img_str))
    
    return img_str

def generate_maze_image(maze):
    """
    Generate a visualization of a maze.
    
    Args:
        maze (Maze): The maze
        
    Returns:
        str: Base64-encoded PNG image
    """
    plt.figure(figsize=(10, 10))
    
    # Create a grid of colored cells
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]
            if cell == '#':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'black')
            elif cell == 'S':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'green')
                plt.text(x + 0.5, y + 0.5, 'S', ha='center', va='center')
            elif cell == 'G':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'red')
                plt.text(x + 0.5, y + 0.5, 'G', ha='center', va='center')
            else:
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'white')
    
    # Set the limits and aspect ratio
    plt.xlim(0, maze.width)
    plt.ylim(0, maze.height)
    plt.gca().invert_yaxis()  # Invert y-axis to match grid coordinates
    plt.gca().set_aspect('equal')
    
    # Remove ticks
    plt.xticks([])
    plt.yticks([])
    
    plt.title("Maze")
    
    # Save the figure to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Convert to base64 for embedding in HTML
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Save to a file as well
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"static/images/maze_{timestamp}.png"
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(img_str))
    
    return img_str

def generate_maze_solution(maze, solution, visited_nodes):
    """
    Generate a visualization of a maze with solution path.
    
    Args:
        maze (Maze): The maze
        solution (Node): The solution node, or None if no solution was found
        visited_nodes (list): List of visited nodes
        
    Returns:
        str: Base64-encoded PNG image
    """
    # Create a copy of the maze grid for visualization
    grid = [row[:] for row in maze.grid]
    
    # Mark visited nodes
    visited_positions = set()
    for node in visited_nodes:
        if node.state != maze.start and node.state != maze.goal:
            x, y = node.state
            visited_positions.add((x, y))
    
    # Mark the solution path
    solution_positions = set()
    if solution:
        path = solution.path()
        for node in path:
            if node.state != maze.start and node.state != maze.goal:
                x, y = node.state
                solution_positions.add((x, y))
    
    plt.figure(figsize=(10, 10))
    
    # Create a grid of colored cells
    for y in range(maze.height):
        for x in range(maze.width):
            cell = grid[y][x]
            if cell == '#':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'black')
            elif cell == 'S':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'green')
                plt.text(x + 0.5, y + 0.5, 'S', ha='center', va='center')
            elif cell == 'G':
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'red')
                plt.text(x + 0.5, y + 0.5, 'G', ha='center', va='center')
            elif (x, y) in solution_positions:
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'yellow')
            elif (x, y) in visited_positions:
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'lightblue')
            else:
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], 'white')
    
    # Set the limits and aspect ratio
    plt.xlim(0, maze.width)
    plt.ylim(0, maze.height)
    plt.gca().invert_yaxis()  # Invert y-axis to match grid coordinates
    plt.gca().set_aspect('equal')
    
    # Remove ticks
    plt.xticks([])
    plt.yticks([])
    
    plt.title("Maze with Solution Path")
    
    # Save the figure to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Convert to base64 for embedding in HTML
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Save to a file as well
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"static/images/maze_solution_{timestamp}.png"
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(img_str))
    
    return img_str

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
