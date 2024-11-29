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
        """Create the plot with all relevant graphs, including the configuration window."""

        # Create the main Tkinter root window for the simulation
        root = tk.Tk()
        root.title("Simulation")

        # Maximize the window without entering full-screen mode
        # 'zoomed' state maximizes the window on most platforms
        root.state("zoomed")

        # Define a clean exit function
        def on_close():
            root.destroy()  # Close the main simulation window
            exit(0)  # Ensure the Python script exits

        # Set the window close protocol
        root.protocol("WM_DELETE_WINDOW", on_close)

        # Create a frame for the simulation plot and buttons
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the control frame for buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Add control buttons to the main simulation window
        bring_to_front_button = tk.Button(
            control_frame,
            text="Bring Config to Front",
            command=lambda: self.bring_config_to_front(),
        )
        bring_to_front_button.pack(side=tk.LEFT, padx=5)

        minimize_button = tk.Button(
            control_frame,
            text="Minimize Config Window",
            command=lambda: self.minimize_config_window(),
        )
        minimize_button.pack(side=tk.LEFT, padx=5)

        # Create a frame for the simulation plot
        plot_frame = tk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Create the main figure
        # Larger size for better spacing
        self.fig = plt.Figure(figsize=(18, 12))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Use GridSpec for flexible layout
        spec = gridspec.GridSpec(nrows=3, ncols=3, figure=self.fig)

        # Adjust the positions of subplots
        self.ax_3d = self.fig.add_subplot(
            231, projection="3d")  # 3D simulation
        self.ax_pollution = self.fig.add_subplot(234)  # Pollution graph
        self.ax_temperature = self.fig.add_subplot(235)  # Temperature graph
        self.ax_population = self.fig.add_subplot(236)  # City Population graph
        self.ax_forests = self.fig.add_subplot(233)  # Forest graph
        self.ax_color_map = self.fig.add_subplot(
            spec[0, 1])  # Color map legend
        self.ax_color_map.axis("off")  # Hide axes for the legend
        self.add_cell_type_legend()

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render the graphs
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()
        self.add_cell_type_legend()

        # Add keyboard navigation
        self.fig.canvas.mpl_connect("key_press_event", self.handle_key_press)

        # Render the initial day
        self.render_day(self.current_day)

        # Display the configuration table
        self.add_config_table_with_scrollbar(root)

        # Start the Tkinter event loop
        root.mainloop()

    def bring_config_to_front(self):
        """Bring the configuration window to the front."""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.deiconify()
            self.config_window.lift()
            self.config_window.focus_force()

    def minimize_config_window(self):
        """Minimize the configuration window."""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.iconify()

    def add_config_table_with_scrollbar(self, root=None):
        """Create a configuration table window with scrollbars and add control buttons."""
        # Create a new window for the configuration table
        self.config_window = tk.Toplevel(root)
        self.config_window.title("Configuration Table")

        # Ensure the configuration window stays on top of the main window initially
        # Keeps the window in front
        self.config_window.attributes("-topmost", True)
        self.config_window.lift()  # Brings it to the top
        # self.config_window.focus_force()  # Sets focus to this window

        # Create a frame to hold the table and scrollbars
        frame = tk.Frame(self.config_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add vertical scrollbar
        vsb = tk.Scrollbar(frame, orient="vertical", width=20)
        vsb.pack(side="right", fill="y")

        # Add horizontal scrollbar
        hsb = tk.Scrollbar(frame, orient="horizontal", width=20)
        hsb.pack(side="bottom", fill="x")

        # Create a treeview for the table
        tree = ttk.Treeview(
            frame,
            columns=("Parameter", "Value"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")

        # Attach the scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Add data to the table
        parameter_width = 0
        value_width = 0

        # Populate the treeview with formatted data
        for key, value in self.config.items():
            if key in key_labels:
                formatted_value = format_config_value(key, value)
                tree.insert("", "end", values=(
                    key_labels[key], formatted_value))
                # Calculate maximum width for the Parameter column
                parameter_width = max(
                    parameter_width, len(key_labels[key]) * 10)

                # Calculate maximum width for the Value column
                value_width = max(value_width, len(formatted_value) * 7)

        # Set the column widths to fit the data
        tree.column("Parameter", width=parameter_width, anchor="w")
        tree.column("Value", width=value_width, anchor="w")
        tree.pack(fill=tk.BOTH, side="top", expand=True)

        # Dynamically adjust the window size based on table content
        table_width = parameter_width + value_width + 50  # Extra padding
        # Adjust height to avoid oversized windows
        table_height = min(500, len(self.config) * 25 + 100)

        # Apply the calculated dimensions to the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = min(table_width, screen_width * 0.9)
        window_height = min(table_height, screen_height * 0.9)

        self.config_window.geometry(
            f"{int(window_width)}x{int(window_height)}")

        # Remove the topmost attribute after focusing on the window
        self.config_window.after(
            1000, lambda: self.config_window.attributes("-topmost", False))

    def add_cell_type_legend(self):
        """Add a legend explaining the cell colors and cell type numbers."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='0: Ocean',
                       markersize=10, markerfacecolor=self.config["base_colors"][0]),
            plt.Line2D([0], [0], marker='o', color='w', label='1: Desert',
                       markersize=10, markerfacecolor=self.config["base_colors"][1]),
            plt.Line2D([0], [0], marker='o', color='w', label='2: Cloud',
                       markersize=10, markerfacecolor=self.config["base_colors"][2]),
            plt.Line2D([0], [0], marker='o', color='w', label='3: Ice',
                       markersize=10, markerfacecolor=self.config["base_colors"][3]),
            plt.Line2D([0], [0], marker='o', color='w', label='4: Forest',
                       markersize=10, markerfacecolor=self.config["base_colors"][4]),
            plt.Line2D([0], [0], marker='o', color='w', label='5: City',
                       markersize=10, markerfacecolor=self.config["base_colors"][5]),
            plt.Line2D([0], [0], marker='o', color='w', label='6: Air (White With Low Opacity)',
                       markersize=10, markerfacecolor=self.config["base_colors"][6]),
            plt.Line2D([0], [0], marker='o', color='w', label='7: Rain',
                       markersize=10, markerfacecolor=self.config["base_colors"][7]),
            plt.Line2D([0], [0], marker='o', color='w', label='8: Vacuum (Transparent)',
                       markersize=10, markerfacecolor=self.config["base_colors"][8])]
        
        if self.config['tint']:
            tinted_red = plt.Line2D([0], [0], marker='o', color='w', label='9: Pollution Levels (Tinted Color)',
                        markersize=10, markerfacecolor='red')
            legend_elements.append(tinted_red)
        
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
                            # Fine-tune interpolation
                            for dx in np.linspace(-0.1, 0.1, 2):
                                for dy in np.linspace(-0.1, 0.1, 2):
                                    for dz in np.linspace(-0.1, 0.1, 2):
                                        points.append((x + dx, y + dy, z + dz))
                                        colors.append(
                                            to_rgba(cell.get_color()))
                                        # Larger size for denser appearance
                                        sizes.append(80)

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
            self.ax_population.plot(
                days, city_population, color="purple", label="Cities")
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
            self.ax_forests.plot(days, forest_count,
                                 color="green", label="Forests")
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
            self.ax_temperature.plot(
                days, avg_temperatures, color="blue", label="Temperature")
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
            self.ax_pollution.plot(days, avg_pollution,
                                   color="red", label="Pollution")
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
