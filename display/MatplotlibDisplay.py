import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np
import logging

class MatplotlibDisplay:
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
        self.ax_water_mass = None
        self.ax_ice_coverage = None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth

    def plot_3d(self):
        """Create the plot with all relevant graphs."""
        plt.ion()  # Enable interactive mode
        self.fig = plt.figure(figsize=(16, 10))  # Adjusted figure size for better layout

        # Adjust the positions of subplots
        self.ax_3d = self.fig.add_subplot(231, projection='3d')  # 3D simulation
        self.ax_pollution = self.fig.add_subplot(232)  # Pollution graph
        self.ax_temperature = self.fig.add_subplot(233)  # Temperature graph
        self.ax_population = self.fig.add_subplot(234)  # Population graph
        self.ax_forests = self.fig.add_subplot(235)  # Forest graph
        self.ax_water_mass = self.fig.add_subplot(236)  # Water Mass graph

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render the graphs
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()
        self.render_water_mass_graph()

        # Add keyboard navigation
        self.fig.canvas.mpl_connect("key_press_event", self.handle_key_press)

        # Render the initial day
        self.render_day(self.current_day)

        plt.tight_layout()  # Automatically adjust subplot spacing
        plt.ioff()  # Disable interactive mode to ensure `plt.show()` holds the program
        plt.show()

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
                            for dx in np.linspace(-0.5, 0.5, 2):  # Fine-tune interpolation
                                for dy in np.linspace(-0.5, 0.5, 2):
                                    for dz in np.linspace(-0.5, 0.5, 2):
                                        points.append((x + dx, y + dy, z + dz))
                                        colors.append(to_rgba(cell.get_color()))
                                        sizes.append(80)  # Larger size for denser appearance

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

        # Set axis limits based on the grid size
        # x_limit, y_limit, z_limit = self.simulation.grid_size
        # self.ax_3d.set_xlim(0, x_limit )
        # self.ax_3d.set_ylim(0, y_limit )
        # self.ax_3d.set_zlim(0, z_limit )

        # Add axis labels
        # self.ax_3d.set_xlabel("X-axis (Width)")
        # self.ax_3d.set_ylabel("Y-axis (Depth)")
        # self.ax_3d.set_zlabel("Z-axis (Height)")

        # Add grid for spatial reference
        self.ax_3d.grid(True)

        points, colors, sizes = self.precomputed_data[day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore the saved viewing angles
        self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)

        # Add legend for the simulation
        self.add_legend()

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

    def render_water_mass_graph(self):
        """Render the water mass graph over time."""
        self.ax_water_mass.cla()
        self.ax_water_mass.set_title("Water Mass Over Time")
        self.ax_water_mass.set_xlabel("Day")
        self.ax_water_mass.set_ylabel("Average Water Mass")

        days = range(len(self.simulation.water_mass_over_time))
        avg_water_mass = self.simulation.water_mass_over_time

        if len(days) == len(avg_water_mass):
            self.ax_water_mass.plot(days, avg_water_mass, color="cyan", label="Water Mass")
            self.ax_water_mass.legend()
        else:
            logging.error("Data length mismatch in water mass graph.")

    def add_legend(self):
        """Add a legend explaining the cell colors."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Sea', markersize=10, markerfacecolor='blue'),
            plt.Line2D([0], [0], marker='o', color='w', label='Land', markersize=10, markerfacecolor='yellow'),
            plt.Line2D([0], [0], marker='o', color='w', label='Cloud', markersize=10, markerfacecolor='gray'),
            plt.Line2D([0], [0], marker='o', color='w', label='Ice', markersize=10, markerfacecolor='lightcyan'),
            plt.Line2D([0], [0], marker='o', color='w', label='Forest', markersize=10, markerfacecolor='green'),
            plt.Line2D([0], [0], marker='o', color='w', label='City', markersize=10, markerfacecolor='purple'),
            plt.Line2D([0], [0], marker='o', color='w', label='Air (Sky)', markersize=10, markerfacecolor='ghostwhite'),
            plt.Line2D([0], [0], marker='o', color='w', label='Black-Tinted Color', markersize=10, markerfacecolor='black')
        ]
        self.ax_3d.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.1, 1.05))

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
