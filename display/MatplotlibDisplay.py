import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np


class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.precomputed_results = simulation.states  # Use precomputed results
        self.current_day = 0
        self.fig, self.ax_3d, self.ax_pollution, self.ax_temperature, self.ax_population, self.ax_forests = None, None, None, None, None, None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth

    def plot_3d(self):
        """Create the plot with all relevant graphs."""
        plt.ion()  # Enable interactive mode
        self.fig = plt.figure(figsize=(18, 12))  # Adjusted figure size for better layout
        # self.fig = plt.figure(figsize=(16, 10))  # Adjusted figure size for better layout

        # Adjust the positions of subplots
        self.ax_3d = self.fig.add_subplot(231, projection='3d')  # 3D simulation
        self.ax_pollution = self.fig.add_subplot(232)  # Pollution graph
        self.ax_temperature = self.fig.add_subplot(233)  # Temperature graph
        self.ax_population = self.fig.add_subplot(234)  # Population graph
        self.ax_forests = self.fig.add_subplot(235)  # Forest graph

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render the graphs
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()


        # Add keyboard navigation
        self.fig.canvas.mpl_connect("key_press_event", self.handle_key_press)

        # Render the initial day
        self.render_day(self.current_day)

        """Add a legend explaining the cell colors."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Sea', markersize=10, markerfacecolor='blue'),
            plt.Line2D([0], [0], marker='o', color='w', label='Land', markersize=10, markerfacecolor='yellow'),
            plt.Line2D([0], [0], marker='o', color='w', label='Cloud', markersize=10, markerfacecolor='gray'),
            plt.Line2D([0], [0], marker='o', color='w', label='Ice', markersize=10, markerfacecolor='cyan'),
            plt.Line2D([0], [0], marker='o', color='w', label='Forest', markersize=10, markerfacecolor='green'),
            plt.Line2D([0], [0], marker='o', color='w', label='City', markersize=10, markerfacecolor='purple'),
            plt.Line2D([0], [0], marker='o', color='w', label='Air (Sky)', markersize=10, markerfacecolor='lightblue'),
        ]
        self.ax_3d.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.1, 1.05))


        plt.tight_layout()  # Automatically adjust subplot spacing
        plt.ioff()  # Disable interactive mode to ensure `plt.show()` holds the program
        plt.show()

    def precompute_visualizations(self):
        """Precompute 3D scatter data for all precomputed states."""
        print("Precomputing 3D visualizations...")
        for state in self.precomputed_results:
            points = []
            colors = []
            sizes = []  # Add a list for point sizes
            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x][y][z]
                        # Collect points and corresponding data
                        points.append((x, y, z))
                        colors.append(to_rgba(cell.get_color()))  # Convert to valid RGBA
                        sizes.append(10)  # Default size for all points

            self.precomputed_data.append((points, colors, sizes))
        print("3D Precomputation complete.")

    def render_day(self, day):
        """Render the cached 3D visualization for a specific day."""
        # Save the current viewing angles
        self.current_elev = self.ax_3d.elev
        self.current_azim = self.ax_3d.azim

        # Clear the existing plot
        self.ax_3d.cla()
        self.ax_3d.set_title(f"Day {day}")
        self.ax_3d.set_axis_off()  # Simplify visualization

        points, colors, sizes = self.precomputed_data[day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore the saved viewing angles
        self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)

        self.fig.canvas.draw_idle()

    def render_population_graph(self):
        """Render the population (number of cities) graph over time."""
        self.ax_population.cla()
        self.ax_population.set_title("City Population Over Time")
        self.ax_population.set_xlabel("Day")
        self.ax_population.set_ylabel("Number of Cities")

        days = range(len(self.simulation.states))
        city_counts = [
            sum(
                1
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type == 5  # City cell type
            )
            for state in self.simulation.states
        ]

        max_count = max(city_counts) if city_counts else 1
        self.ax_population.plot(days, city_counts, color="purple", label="Cities")
        self.ax_population.set_ylim(0, max_count * 1.1)
        self.ax_population.legend()


    def render_forests_graph(self):
        """Render the forest count graph over time."""
        self.ax_forests.cla()
        self.ax_forests.set_title("Forest Count Over Time")
        self.ax_forests.set_xlabel("Day")
        self.ax_forests.set_ylabel("Number of Forests")

        days = range(len(self.simulation.states))
        forest_counts = [
            sum(
                1
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type == 4  # Forest cell type
            )
            for state in self.simulation.states
        ]

        max_count = max(forest_counts) if forest_counts else 1
        self.ax_forests.plot(days, forest_counts, color="green", label="Forests")
        self.ax_forests.set_ylim(0, max_count * 1.1)
        self.ax_forests.legend()


    def render_temperature_graph(self):
        """Render the temperature graph over time."""
        self.ax_temperature.cla()
        self.ax_temperature.set_title("Temperature Over Time")
        self.ax_temperature.set_xlabel("Day")
        self.ax_temperature.set_ylabel("Average Temperature")

        days = range(len(self.simulation.states))
        avg_temperatures = [
            np.mean([
                cell.temperature for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type !=6  # Exclude air cells
            ])
            if any(state.grid[x][y][z].cell_type !=6
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2]))
            else 0  # Default to 0 if only air cells are present
            for state in self.simulation.states
        ]

        max_temp = max(avg_temperatures) if avg_temperatures else 1
        min_temp = min(avg_temperatures) if avg_temperatures else 0
        self.ax_temperature.plot(days, avg_temperatures, color="blue", label="Temperature")
        self.ax_temperature.set_ylim(min_temp * 0.9, max_temp * 1.1)
        self.ax_temperature.legend()


    def render_pollution_graph(self):
        """Render the pollution graph over time."""
        self.ax_pollution.cla()
        self.ax_pollution.set_title("Pollution Over Time")
        self.ax_pollution.set_xlabel("Day")
        self.ax_pollution.set_ylabel("Average Pollution")

        days = range(len(self.simulation.states))
        avg_pollution = [
            np.mean([
                cell.pollution_level for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type not in ["air", 0]  # Exclude air and sea cells
            ])
            if any(state.grid[x][y][z].cell_type not in ["air", 0]
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2]))
            else 0  # Default to 0 if only air or sea cells are present
            for state in self.simulation.states
        ]

        max_pollution = max(avg_pollution) if avg_pollution else 1
        self.ax_pollution.plot(days, avg_pollution, color="red", label="Pollution")
        self.ax_pollution.set_ylim(0, max_pollution * 1.1)
        self.ax_pollution.legend()

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

    def add_legend(self):
        """Add a legend explaining the cell colors."""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Sea', markersize=10, markerfacecolor='blue'),
            plt.Line2D([0], [0], marker='o', color='w', label='Land', markersize=10, markerfacecolor='yellow'),
            plt.Line2D([0], [0], marker='o', color='w', label='Cloud', markersize=10, markerfacecolor='gray'),
            plt.Line2D([0], [0], marker='o', color='w', label='Ice', markersize=10, markerfacecolor='cyan'),
            plt.Line2D([0], [0], marker='o', color='w', label='Forest', markersize=10, markerfacecolor='green'),
            plt.Line2D([0], [0], marker='o', color='w', label='City', markersize=10, markerfacecolor='purple'),
            plt.Line2D([0], [0], marker='o', color='w', label='Air (Sky)', markersize=10, markerfacecolor='lightblue'),
        ]
        self.ax_3d.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.1, 1.05))
