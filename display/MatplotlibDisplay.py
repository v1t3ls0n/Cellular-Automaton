import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import numpy as np
import logging
from core.conf import config


class MatplotlibDisplay:
    config = config

    def __init__(self, simulation):
        self.simulation = simulation
        self.precomputed_results = simulation.states
        self.current_day = 0
        self.fig = None
        self.ax_3d = None
        self.ax_pollution = None
        self.ax_temperature = None
        self.ax_population = None
        self.ax_forests = None
        self.ax_table = None
        self.precomputed_data = []
        self.current_elev = 20
        self.current_azim = 45

    def plot_3d(self):
        """Create a scrollable UI with all relevant graphs."""
        # Create a Tkinter root window
        root = tk.Tk()
        root.title("Simulation Visualization")

        # Create a main frame for the canvas and scrollbar
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Add a canvas widget for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Configure scrolling behavior
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Matplotlib figure
        self.fig = plt.figure(figsize=(12, 20))
        self.ax_3d = self.fig.add_subplot(231, projection='3d')
        self.ax_pollution = self.fig.add_subplot(234)
        self.ax_temperature = self.fig.add_subplot(235)
        self.ax_population = self.fig.add_subplot(236)
        self.ax_forests = self.fig.add_subplot(233)
        self.ax_table = self.fig.add_subplot(232)

        # Precompute data and render initial graphs
        self.precompute_visualizations()
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()
        self.add_config_table()
        self.render_day(self.current_day)

        # Embed the Matplotlib figure in the Tkinter UI
        canvas_widget = FigureCanvasTkAgg(self.fig, scrollable_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Run the Tkinter event loop
        root.mainloop()

    def precompute_visualizations(self):
        """Precompute 3D scatter data for all precomputed states."""
        logging.info("Precomputing 3D visualizations...")
        for state in self.simulation.states:
            points, colors, sizes = [], [], []
            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x][y][z]
                        if cell.get_color() is not None:
                            points.append((x, y, z))
                            colors.append(to_rgba(cell.get_color()))
                            sizes.append(80)
            self.precomputed_data.append((points, colors, sizes))
        logging.info("3D Precomputation complete.")

    def render_day(self, day):
        """Render the 3D scatter plot for a specific day."""
        self.ax_3d.cla()
        self.ax_3d.set_title(f"Day {day}")
        self.ax_3d.grid(True)
        points, colors, sizes = self.precomputed_data[day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore view angles
        self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)
        self.fig.canvas.draw_idle()

    def add_config_table(self):
        """Add a table with configuration parameters."""
        config_params = [
            ("Temperature Extinction", self.config["temperature_extinction_point"]),
            ("Freezing Point", self.config["freezing_point"]),
            ("Melting Point", self.config["melting_point"]),
            ("Evaporation Point", self.config["evaporation_point"]),
            ("Water Transfer Threshold", self.config["water_transfer_threshold"]),
            # Add other parameters as needed
        ]

        table_data = [[param, value] for param, value in config_params]
        self.ax_table.axis("tight")
        self.ax_table.axis("off")
        self.ax_table.table(
            cellText=table_data,
            colLabels=["Parameter", "Value"],
            loc="center",
            cellLoc="center"
        )

    def render_pollution_graph(self):
        """Render pollution data."""
        self.ax_pollution.cla()
        self.ax_pollution.set_title("Pollution Over Time")
        days = range(len(self.simulation.pollution_over_time))
        self.ax_pollution.plot(days, self.simulation.pollution_over_time, color="red", label="Pollution")
        self.ax_pollution.legend()

    def render_temperature_graph(self):
        """Render temperature data."""
        self.ax_temperature.cla()
        self.ax_temperature.set_title("Temperature Over Time")
        days = range(len(self.simulation.temperature_over_time))
        self.ax_temperature.plot(days, self.simulation.temperature_over_time, color="blue", label="Temperature")
        self.ax_temperature.legend()

    def render_population_graph(self):
        """Render city population data."""
        self.ax_population.cla()
        self.ax_population.set_title("City Population Over Time")
        days = range(len(self.simulation.city_population_over_time))
        self.ax_population.plot(days, self.simulation.city_population_over_time, color="purple", label="Cities")
        self.ax_population.legend()

    def render_forests_graph(self):
        """Render forest data."""
        self.ax_forests.cla()
        self.ax_forests.set_title("Forest Count Over Time")
        days = range(len(self.simulation.forest_count_over_time))
        self.ax_forests.plot(days, self.simulation.forest_count_over_time, color="green", label="Forests")
        self.ax_forests.legend()
