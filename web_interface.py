"""
Simple web interface for the AI Agent using Python's built-in HTTP server.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import base64
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import threading
import time
from datetime import datetime

from miu_system import next_states, is_valid_miu_string
from miu_problem import MIUProblem, miu_heuristic
from maze_environment import Maze, MazeProblem, manhattan_distance
from search import breadth_first_search, depth_first_search, a_star_search

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# Global variables to store state
current_maze = None
search_results = {}

class AIAgentHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the AI Agent web interface."""
    
    def do_GET(self):
        """Handle GET requests."""
        # Serve static files
        if self.path.startswith('/static/'):
            self.path = self.path[1:]  # Remove leading slash
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Serve the main page
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open('static/index.html', 'rb') as file:
                self.wfile.write(file.read())
            return
        
        # API endpoints
        if self.path.startswith('/api/'):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API endpoints require POST requests'}).encode())
            return
        
        # Default: serve 404
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'404 Not Found')
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Parse JSON data
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return
        
        # API endpoints
        if self.path == '/api/miu/next_states':
            self.handle_miu_next_states(data)
        elif self.path == '/api/miu/search':
            self.handle_miu_search(data)
        elif self.path == '/api/maze/generate':
            self.handle_maze_generate(data)
        elif self.path == '/api/maze/search':
            self.handle_maze_search(data)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
    
    def handle_miu_next_states(self, data):
        """Handle MIU next states API endpoint."""
        state = data.get('state', 'MI')
        
        if not is_valid_miu_string(state):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid MIU string'}).encode())
            return
        
        result = next_states(state)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'next_states': result}).encode())
    
    def handle_miu_search(self, data):
        """Handle MIU search API endpoint."""
        initial_state = data.get('initial_state', 'MI')
        goal_state = data.get('goal_state', 'MU')
        algorithm = data.get('algorithm', 'bfs')
        max_iterations = int(data.get('max_iterations', 1000))
        
        if not is_valid_miu_string(initial_state) or not is_valid_miu_string(goal_state):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid MIU string'}).encode())
            return
        
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
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid algorithm'}).encode())
            return
        
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
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"static/images/miu_graph_{timestamp}.png"
        self.generate_miu_graph(visited_nodes, solution, filename)
        result['graph_image'] = f"/static/images/miu_graph_{timestamp}.png"
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_maze_generate(self, data):
        """Handle maze generation API endpoint."""
        global current_maze
        
        width = int(data.get('width', 10))
        height = int(data.get('height', 10))
        wall_prob = float(data.get('wall_prob', 0.3))
        seed = int(data.get('seed', 42))
        
        if width <= 0 or height <= 0 or wall_prob < 0 or wall_prob > 1:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid maze parameters'}).encode())
            return
        
        # Generate the maze
        current_maze = Maze(width, height, wall_prob, seed)
        
        # Convert the maze to a 2D array for JSON
        maze_grid = []
        for y in range(current_maze.height):
            row = []
            for x in range(current_maze.width):
                row.append(current_maze.grid[y][x])
            maze_grid.append(row)
        
        # Generate a visualization of the maze
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"static/images/maze_{timestamp}.png"
        self.generate_maze_image(current_maze, filename)
        
        result = {
            'width': current_maze.width,
            'height': current_maze.height,
            'grid': maze_grid,
            'start': current_maze.start,
            'goal': current_maze.goal,
            'maze_image': f"/static/images/maze_{timestamp}.png"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_maze_search(self, data):
        """Handle maze search API endpoint."""
        global current_maze
        
        if not current_maze:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'No maze generated'}).encode())
            return
        
        algorithm = data.get('algorithm', 'astar')
        
        # Create the problem
        problem = MazeProblem(current_maze)
        
        # Run the search algorithm
        if algorithm == 'bfs':
            solution, visited_nodes, iterations = breadth_first_search(problem)
        elif algorithm == 'dfs':
            solution, visited_nodes, iterations = depth_first_search(problem)
        elif algorithm == 'astar':
            solution, visited_nodes, iterations = a_star_search(problem, manhattan_distance)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid algorithm'}).encode())
            return
        
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
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"static/images/maze_solution_{timestamp}.png"
        self.generate_maze_solution(current_maze, solution, visited_nodes, filename)
        result['maze_solution_image'] = f"/static/images/maze_solution_{timestamp}.png"
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def generate_miu_graph(self, visited_nodes, solution, filename):
        """Generate a visualization of the MIU search graph."""
        import networkx as nx
        
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
        plt.savefig(filename)
        plt.close()
    
    def generate_maze_image(self, maze, filename):
        """Generate a visualization of a maze."""
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
        plt.savefig(filename)
        plt.close()
    
    def generate_maze_solution(self, maze, solution, visited_nodes, filename):
        """Generate a visualization of a maze with solution path."""
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
        plt.savefig(filename)
        plt.close()


def run_server(port=8000):
    """Run the HTTP server."""
    handler = AIAgentHandler
    
    # Set the directory for serving static files
    handler.directory = os.getcwd()
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
