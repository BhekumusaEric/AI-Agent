"""
GUI for AI Agent

This module implements a graphical user interface for the AI agent using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading

from miu_system import next_states, is_valid_miu_string
from miu_problem import MIUProblem, miu_heuristic
from maze_environment import Maze, MazeProblem, manhattan_distance
from search import breadth_first_search, depth_first_search, a_star_search

class AIAgentGUI:
    """GUI for the AI Agent."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("AI Agent")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.miu_tab = ttk.Frame(self.notebook)
        self.maze_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.miu_tab, text="MIU System")
        self.notebook.add(self.maze_tab, text="Maze Environment")
        
        # Set up the MIU System tab
        self.setup_miu_tab()
        
        # Set up the Maze Environment tab
        self.setup_maze_tab()
        
        # Variables for search visualization
        self.graph = nx.DiGraph()
        self.pos = None
        self.search_running = False
        
    def setup_miu_tab(self):
        """Set up the MIU System tab."""
        # Create frames
        input_frame = ttk.LabelFrame(self.miu_tab, text="Input")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        control_frame = ttk.LabelFrame(self.miu_tab, text="Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_frame = ttk.LabelFrame(self.miu_tab, text="Output")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame widgets
        ttk.Label(input_frame, text="Initial State:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.initial_state_var = tk.StringVar(value="MI")
        ttk.Entry(input_frame, textvariable=self.initial_state_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Goal State:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.goal_state_var = tk.StringVar(value="MU")
        ttk.Entry(input_frame, textvariable=self.goal_state_var, width=20).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Control frame widgets
        ttk.Label(control_frame, text="Search Algorithm:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_algorithm_var = tk.StringVar(value="BFS")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.search_algorithm_var, 
                                      values=["BFS", "DFS", "A*"], state="readonly", width=10)
        algorithm_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(control_frame, text="Max Iterations:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.max_iterations_var = tk.IntVar(value=1000)
        ttk.Entry(control_frame, textvariable=self.max_iterations_var, width=10).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(control_frame, text="Visualization Speed:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        search_button = ttk.Button(control_frame, text="Start Search", command=self.start_miu_search)
        search_button.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        
        stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_search)
        stop_button.grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        
        # Output frame widgets
        output_paned = ttk.PanedWindow(output_frame, orient=tk.HORIZONTAL)
        output_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: Graph visualization
        graph_frame = ttk.Frame(output_paned)
        output_paned.add(graph_frame, weight=2)
        
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right side: Text output
        text_frame = ttk.Frame(output_paned)
        output_paned.add(text_frame, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_maze_tab(self):
        """Set up the Maze Environment tab."""
        # Create frames
        input_frame = ttk.LabelFrame(self.maze_tab, text="Maze Configuration")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        control_frame = ttk.LabelFrame(self.maze_tab, text="Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_frame = ttk.LabelFrame(self.maze_tab, text="Maze Visualization")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame widgets
        ttk.Label(input_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.maze_width_var = tk.IntVar(value=10)
        ttk.Entry(input_frame, textvariable=self.maze_width_var, width=5).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Height:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.maze_height_var = tk.IntVar(value=10)
        ttk.Entry(input_frame, textvariable=self.maze_height_var, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Wall Probability:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.wall_prob_var = tk.DoubleVar(value=0.3)
        ttk.Entry(input_frame, textvariable=self.wall_prob_var, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Random Seed:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.seed_var = tk.IntVar(value=42)
        ttk.Entry(input_frame, textvariable=self.seed_var, width=5).grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        
        generate_button = ttk.Button(input_frame, text="Generate Maze", command=self.generate_maze)
        generate_button.grid(row=0, column=8, padx=5, pady=5, sticky=tk.W)
        
        # Control frame widgets
        ttk.Label(control_frame, text="Search Algorithm:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.maze_algorithm_var = tk.StringVar(value="A*")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.maze_algorithm_var, 
                                      values=["BFS", "DFS", "A*"], state="readonly", width=10)
        algorithm_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(control_frame, text="Visualization Speed:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.maze_speed_var = tk.DoubleVar(value=0.5)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.maze_speed_var, orient=tk.HORIZONTAL)
        speed_scale.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        search_button = ttk.Button(control_frame, text="Start Search", command=self.start_maze_search)
        search_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_search)
        stop_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Output frame for maze visualization
        self.maze_canvas = tk.Canvas(output_frame, bg="white")
        self.maze_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize maze
        self.maze = None
        self.cell_size = 30
        
    def generate_maze(self):
        """Generate a new maze."""
        try:
            width = self.maze_width_var.get()
            height = self.maze_height_var.get()
            wall_prob = self.wall_prob_var.get()
            seed = self.seed_var.get()
            
            if width <= 0 or height <= 0 or wall_prob < 0 or wall_prob > 1:
                messagebox.showerror("Invalid Input", "Please enter valid maze parameters.")
                return
            
            self.maze = Maze(width, height, wall_prob, seed)
            self.draw_maze()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate maze: {str(e)}")
    
    def draw_maze(self):
        """Draw the maze on the canvas."""
        if not self.maze:
            return
        
        # Calculate cell size based on canvas size
        canvas_width = self.maze_canvas.winfo_width()
        canvas_height = self.maze_canvas.winfo_height()
        
        self.cell_size = min(
            (canvas_width - 20) // self.maze.width,
            (canvas_height - 20) // self.maze.height
        )
        
        # Clear canvas
        self.maze_canvas.delete("all")
        
        # Draw cells
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                x1 = 10 + x * self.cell_size
                y1 = 10 + y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                cell = self.maze.grid[y][x]
                if cell == '#':
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
                elif cell == 'S':
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="gray")
                    self.maze_canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, text="S")
                elif cell == 'G':
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="gray")
                    self.maze_canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2, text="G")
                else:
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")
    
    def start_miu_search(self):
        """Start the MIU search."""
        if self.search_running:
            messagebox.showinfo("Search in Progress", "A search is already running. Please stop it first.")
            return
        
        initial_state = self.initial_state_var.get()
        goal_state = self.goal_state_var.get()
        
        if not is_valid_miu_string(initial_state) or not is_valid_miu_string(goal_state):
            messagebox.showerror("Invalid Input", "Initial and goal states must be valid MIU strings.")
            return
        
        algorithm = self.search_algorithm_var.get()
        max_iterations = self.max_iterations_var.get()
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.graph = nx.DiGraph()
        self.ax.clear()
        self.canvas.draw()
        
        # Create the problem
        problem = MIUProblem(initial_state, goal_state)
        
        # Start search in a separate thread
        self.search_running = True
        threading.Thread(target=self.run_miu_search, args=(problem, algorithm, max_iterations)).start()
    
    def run_miu_search(self, problem, algorithm, max_iterations):
        """
        Run the MIU search algorithm.
        
        Args:
            problem (MIUProblem): The MIU problem
            algorithm (str): The search algorithm to use
            max_iterations (int): Maximum number of iterations
        """
        try:
            self.output_text.insert(tk.END, f"Starting {algorithm} search...\n")
            self.output_text.insert(tk.END, f"Initial state: {problem.initial_state}\n")
            self.output_text.insert(tk.END, f"Goal state: {problem.goal}\n\n")
            
            # Run the search algorithm
            if algorithm == "BFS":
                solution, visited_nodes, iterations = breadth_first_search(problem, max_iterations)
            elif algorithm == "DFS":
                solution, visited_nodes, iterations = depth_first_search(problem, max_iterations=max_iterations)
            elif algorithm == "A*":
                solution, visited_nodes, iterations = a_star_search(problem, miu_heuristic, max_iterations)
            
            # Visualize the search process
            self.visualize_miu_search(visited_nodes, solution)
            
            # Display results
            if solution:
                self.output_text.insert(tk.END, f"Solution found in {iterations} iterations!\n")
                self.output_text.insert(tk.END, "Path:\n")
                
                path = solution.path()
                for i, node in enumerate(path):
                    if i > 0:
                        self.output_text.insert(tk.END, f"  {i}. {node.action} -> {node.state}\n")
                    else:
                        self.output_text.insert(tk.END, f"  {i}. Start: {node.state}\n")
            else:
                self.output_text.insert(tk.END, f"No solution found after {iterations} iterations.\n")
            
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            self.search_running = False
    
    def visualize_miu_search(self, visited_nodes, solution):
        """
        Visualize the MIU search process.
        
        Args:
            visited_nodes (list): List of visited nodes
            solution (Node): The solution node, or None if no solution was found
        """
        # Build the graph
        for node in visited_nodes:
            if node.parent:
                self.graph.add_edge(node.parent.state, node.state)
                
                # Update the graph visualization
                if not self.search_running:
                    break
                    
                self.ax.clear()
                
                # Use spring layout for small graphs, shell layout for larger ones
                if len(self.graph) < 20:
                    self.pos = nx.spring_layout(self.graph)
                else:
                    self.pos = nx.shell_layout(self.graph)
                
                nx.draw(self.graph, self.pos, ax=self.ax, with_labels=True, 
                       node_color="lightblue", node_size=500, font_size=8,
                       edge_color="gray", arrows=True)
                
                # Highlight the current node
                nx.draw_networkx_nodes(self.graph, self.pos, nodelist=[node.state],
                                     node_color="yellow", node_size=500, ax=self.ax)
                
                # Highlight the path if a solution is found
                if solution:
                    path_states = [n.state for n in solution.path()]
                    path_edges = [(path_states[i], path_states[i+1]) for i in range(len(path_states)-1)]
                    
                    nx.draw_networkx_nodes(self.graph, self.pos, nodelist=path_states,
                                         node_color="green", node_size=500, ax=self.ax)
                    nx.draw_networkx_edges(self.graph, self.pos, edgelist=path_edges,
                                         edge_color="green", width=2, ax=self.ax)
                
                self.canvas.draw()
                time.sleep(1.0 / self.speed_var.get())  # Adjust visualization speed
    
    def start_maze_search(self):
        """Start the maze search."""
        if not self.maze:
            messagebox.showerror("No Maze", "Please generate a maze first.")
            return
            
        if self.search_running:
            messagebox.showinfo("Search in Progress", "A search is already running. Please stop it first.")
            return
        
        algorithm = self.maze_algorithm_var.get()
        
        # Create the problem
        problem = MazeProblem(self.maze)
        
        # Start search in a separate thread
        self.search_running = True
        threading.Thread(target=self.run_maze_search, args=(problem, algorithm)).start()
    
    def run_maze_search(self, problem, algorithm):
        """
        Run the maze search algorithm.
        
        Args:
            problem (MazeProblem): The maze problem
            algorithm (str): The search algorithm to use
        """
        try:
            # Run the search algorithm
            if algorithm == "BFS":
                solution, visited_nodes, iterations = breadth_first_search(problem)
            elif algorithm == "DFS":
                solution, visited_nodes, iterations = depth_first_search(problem)
            elif algorithm == "A*":
                solution, visited_nodes, iterations = a_star_search(problem, manhattan_distance)
            
            # Visualize the search process
            self.visualize_maze_search(visited_nodes, solution)
            
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
        finally:
            self.search_running = False
    
    def visualize_maze_search(self, visited_nodes, solution):
        """
        Visualize the maze search process.
        
        Args:
            visited_nodes (list): List of visited nodes
            solution (Node): The solution node, or None if no solution was found
        """
        # Redraw the maze
        self.draw_maze()
        
        # Visualize the search process
        for node in visited_nodes:
            if not self.search_running:
                break
                
            if node.parent:
                x, y = node.state
                x1 = 10 + x * self.cell_size
                y1 = 10 + y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Draw visited cell
                if self.maze.grid[y][x] not in ['S', 'G']:
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="gray")
                
                self.root.update()
                time.sleep(0.5 / self.maze_speed_var.get())  # Adjust visualization speed
        
        # Draw the solution path if found
        if solution:
            path = solution.path()
            for node in path:
                if not self.search_running:
                    break
                    
                x, y = node.state
                if self.maze.grid[y][x] not in ['S', 'G']:
                    x1 = 10 + x * self.cell_size
                    y1 = 10 + y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    
                    self.maze_canvas.create_rectangle(x1, y1, x2, y2, fill="yellow", outline="gray")
                
                self.root.update()
                time.sleep(0.5 / self.maze_speed_var.get())
    
    def stop_search(self):
        """Stop the current search."""
        self.search_running = False


def main():
    """Main function."""
    root = tk.Tk()
    app = AIAgentGUI(root)
    
    # Handle window resize for maze visualization
    def on_resize(event):
        if app.maze:
            app.draw_maze()
    
    app.maze_canvas.bind("<Configure>", on_resize)
    
    root.mainloop()


if __name__ == "__main__":
    main()
