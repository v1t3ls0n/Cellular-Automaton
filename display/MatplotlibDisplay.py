import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np
import logging
from core.conf import config, key_labels,  format_config_value 
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg










class MatplotlibDisplay:
    config = config

    def __init__(self, simulation):
        self.simulation = simulation
        self.precomputed_results = simulation.states  # Use precomputed results
        self.current_day = 0
        self.fig = None
        self.ax_3d = None
        self.ax_pollution = None
        self.ax_temperature = None
        self.ax_population = None
        self.ax_forests = None
        self.ax_ice_coverage = None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth



    def plot_3d(self):
        """Create the plot with all relevant graphs, legends, and tables."""
        plt.ion()  # Enable interactive mode



        # Create the main figure
        self.fig = plt.figure(figsize=(18, 12))  # Larger size for better spacing

        # Use GridSpec for flexible layout
        spec = gridspec.GridSpec(nrows=3, ncols=3, figure=self.fig)

        # Create a Tkinter root window
        root = tk.Tk()
        root.title("Configuration Table")

        # Add the scrollable table
        self.add_config_table_with_scrollbar(root)

        # 3D Simulation plot
        self.ax_3d = self.fig.add_subplot(spec[0, 0], projection="3d")
        self.ax_3d.set_title("3D Simulation")

        # Pollution graph
        self.ax_pollution = self.fig.add_subplot(spec[1, 0])
        self.ax_pollution.set_title("Pollution Over Time")

        # Temperature graph
        self.ax_temperature = self.fig.add_subplot(spec[1, 1])
        self.ax_temperature.set_title("Temperature Over Time")

        # City Population graph
        self.ax_population = self.fig.add_subplot(spec[1, 2])
        self.ax_population.set_title("City Population Over Time")

        # Forest Count graph
        self.ax_forests = self.fig.add_subplot(spec[2, 0])
        self.ax_forests.set_title("Forest Count Over Time")

        # Color map legend
        self.ax_color_map = self.fig.add_subplot(spec[0, 1])
        self.ax_color_map.axis("off")  # Hide axes for the legend
        self.add_cell_type_legend()

        # Configuration table
        self.ax_table = self.fig.add_subplot(spec[2, 1:])  # Spans two columns
        self.ax_table.axis("off")  # Hide axes for the table

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render graphs
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()

        # Render the initial day
        self.render_day(self.current_day)

        # Adjust layout
        plt.subplots_adjust(
            left=0.05,    # Left margin
            right=0.95,   # Right margin
            top=0.95,     # Top margin
            bottom=0.05,  # Bottom margin
            wspace=0.4,   # Width space between subplots
            hspace=0.6    # Height space between subplots
        )

        plt.ioff()  # Disable interactive mode to ensure `plt.show()` holds the program
        plt.show()
        # Start the Tkinter loop
        root.mainloop()








    def add_config_table_with_scrollbar(self, root=None):
        # Create a new window if root is not provided
        if root is None:
            root = tk.Tk()
            root.title("Configuration Table")

        # Get screen dimensions for dynamic window sizing
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Adjust the window size based on screen dimensions
        window_width = int(screen_width * 0.5)  # Use 80% of screen width
        window_height = int(screen_height * 0.5)  # Use 80% of screen height
        root.geometry(f"{window_width}x{window_height}")

        # Add a frame for scrolling
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar using tk.Scrollbar
        vsb = tk.Scrollbar(frame, orient="vertical", width = 20)
        vsb.grid(row=0, column=1, sticky="ns")

        # Create a horizontal scrollbar using tk.Scrollbar
        hsb = tk.Scrollbar(frame, orient="horizontal", width = 20)
        hsb.grid(row=1, column=0, sticky="ew")

        # Create the treeview (table)
        tree = ttk.Treeview(
            frame,
            columns=("Parameter", "Value"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        tree.grid(row=0, column=0, sticky="nsew")

        # Configure scrollbars to work with the treeview
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Define column headings
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")

        # Define column widths
        tree.column("Parameter", width=window_width//4, anchor="w")
        tree.column("Value", width=window_width//4, anchor="w")


        # Add data to the table
        for key, value in self.config.items():
            
            if key == "base_colors":
                continue

            # Use key_labels for meaningful names
            parameter_name = key_labels.get(key, key)
            
            # Format the value using format_config_value
            formatted_value = format_config_value(key, value)
            
            # Add the row to the treeview
            tree.insert("", "end", values=(parameter_name, formatted_value))

        # Adjust layout of root
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=2)
        frame.grid_columnconfigure(0, weight=2)

        # Run the Tkinter main loop if no parent root was provided
        if root is None:
            root.mainloop()











    def add_cell_type_legend(self):
        """Add a legend explaining the cell colors and cell type numbers."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='0: Ocean', markersize=10, markerfacecolor=self.config["base_colors"][0]),
            plt.Line2D([0], [0], marker='o', color='w', label='1: Desert', markersize=10, markerfacecolor=self.config["base_colors"][1]),
            plt.Line2D([0], [0], marker='o', color='w', label='2: Cloud', markersize=10, markerfacecolor=self.config["base_colors"][2]),
            plt.Line2D([0], [0], marker='o', color='w', label='3: Ice', markersize=10, markerfacecolor=self.config["base_colors"][3]),
            plt.Line2D([0], [0], marker='o', color='w', label='4: Forest', markersize=10, markerfacecolor=self.config["base_colors"][4]),
            plt.Line2D([0], [0], marker='o', color='w', label='5: City', markersize=10, markerfacecolor=self.config["base_colors"][5]),
            plt.Line2D([0], [0], marker='o', color='w', label='6: Air (Sky)', markersize=10, markerfacecolor=self.config["base_colors"][6]),
            plt.Line2D([0], [0], marker='o', color='w', label='7: Rain', markersize=10, markerfacecolor=self.config["base_colors"][7]),
            plt.Line2D([0], [0], marker='o', color='w', label='8: Vacuum', markersize=10, markerfacecolor=self.config["base_colors"][8]),
        ]
        self.ax_color_map.legend(
            handles=legend_elements,
            loc="center",
            title="Cell Types",
            frameon=False
        )






















    def precompute_visualizations(self):
        """Precompute 3D scatter data for all precomputed states."""
        logging.info("Precomputing 3D visualizations...")
        for state in self.simulation.states:
            points = []
            colors = []
            sizes = []  # Add a list for point sizes
            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x][y][z]
                        if cell.get_color() is not None:
                            # Interpolate multiple points for "densification"
                            for dx in np.linspace(-0.1, 0.1, 2):  # Fine-tune interpolation
                                for dy in np.linspace(-0.1, 0.1, 2):
                                    for dz in np.linspace(-0.1, 0.1, 2):
                                        points.append((x + dx, y + dy, z + dz))
                                        colors.append(to_rgba(cell.get_color()))
                                        sizes.append(80)  # Larger size for denser appearance
                            
                            # points.append((x , y , z ))
                            # colors.append(to_rgba(cell.get_color()))
                            # sizes.append(80)  # Larger size for denser appearance

            self.precomputed_data.append((points, colors, sizes))
        logging.info("3D Precomputation complete.")

    def render_day(self, day):
        """Render the cached 3D visualization for a specific day."""
        # Save the current viewing angles
        self.current_elev = self.ax_3d.elev
        self.current_azim = self.ax_3d.azim

        # Clear the existing plot
        self.ax_3d.cla()
        self.ax_3d.set_title(f"Day {day}")
        self.ax_3d.set_axis_on()  # Simplify visualization

        # Add grid for spatial reference
        self.ax_3d.grid(True)

        points, colors, sizes = self.precomputed_data[day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore the saved viewing angles
        self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)

        self.fig.canvas.draw_idle()

    def render_population_graph(self):
        """Render the city population graph over time."""
        self.ax_population.cla()
        self.ax_population.set_title("City Population Over Time")
        self.ax_population.set_xlabel("Day")
        self.ax_population.set_ylabel("Number of Cities")

        # Retrieve data
        days = range(len(self.simulation.city_population_over_time))
        city_population = self.simulation.city_population_over_time

        # Ensure data matches the length of days
        if len(days) == len(city_population):
            self.ax_population.plot(days, city_population, color="purple", label="Cities")
            self.ax_population.legend()
        else:
            logging.error("Data length mismatch in population graph.")

    def render_forests_graph(self):
        """Render the forest count graph over time."""
        self.ax_forests.cla()
        self.ax_forests.set_title("Forest Count Over Time")
        self.ax_forests.set_xlabel("Day")
        self.ax_forests.set_ylabel("Number of Forests")

        # Retrieve data
        days = range(len(self.simulation.forest_count_over_time))
        forest_count = self.simulation.forest_count_over_time

        if len(days) == len(forest_count):
            self.ax_forests.plot(days, forest_count, color="green", label="Forests")
            self.ax_forests.legend()
        else:
            logging.error("Data length mismatch in forest graph.")

    def render_temperature_graph(self):
        """Render the temperature graph over time."""
        self.ax_temperature.cla()
        self.ax_temperature.set_title("Temperature Over Time")
        self.ax_temperature.set_xlabel("Day")
        self.ax_temperature.set_ylabel("Average Temperature")

        days = range(len(self.simulation.temperature_over_time))
        avg_temperatures = self.simulation.temperature_over_time

        if len(days) == len(avg_temperatures):
            self.ax_temperature.plot(days, avg_temperatures, color="blue", label="Temperature")
            self.ax_temperature.legend()
        else:
            logging.error("Data length mismatch in temperature graph.")

    def render_pollution_graph(self):
        """Render the pollution graph over time."""
        self.ax_pollution.cla()
        self.ax_pollution.set_title("Pollution Over Time")
        self.ax_pollution.set_xlabel("Day")
        self.ax_pollution.set_ylabel("Average Pollution")

        days = range(len(self.simulation.pollution_over_time))
        avg_pollution = self.simulation.pollution_over_time

        if len(days) == len(avg_pollution):
            self.ax_pollution.plot(days, avg_pollution, color="red", label="Pollution")
            self.ax_pollution.legend()
        else:
            logging.error("Data length mismatch in pollution graph.")

    def handle_key_press(self, event):
        """Handle key presses for navigating and zooming/panning the graphs."""
        if event.key == "right":
            self.next_day()
        elif event.key == "left":
            self.previous_day()

    def next_day(self):
        if self.current_day < len(self.simulation.states) - 1:
            self.current_day += 1
            self.render_day(self.current_day)

    def previous_day(self):
        if self.current_day > 0:
            self.current_day -= 1
            self.render_day(self.current_day)

