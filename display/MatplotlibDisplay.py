import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np


class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.current_day = 0
        self.fig, self.ax_3d, self.ax_pollution, self.ax_temperature = None, None, None, None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth

    def plot_3d(self):
        """Create the plot with pollution and temperature graphs."""
        self.fig = plt.figure(figsize=(15, 5))
        self.ax_3d = self.fig.add_subplot(131, projection='3d')  # 3D simulation
        self.ax_pollution = self.fig.add_subplot(132)  # Pollution graph
        self.ax_temperature = self.fig.add_subplot(133)  # Temperature graph

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render pollution and temperature graphs
        self.render_pollution_graph()
        self.render_temperature_graph()

        # Add keyboard navigation
        self.fig.canvas.mpl_connect("key_press_event", self.handle_key_press)

        # Render the initial day
        self.render_day(self.current_day)

        plt.show()

    def precompute_visualizations(self):
        """Precompute 3D scatter data for all days."""
        print("Precomputing 3D visualizations for all days...")
        for state in self.simulation.states:
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
        print("Precomputation complete.")

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

    def render_temperature_graph(self):
        """Render the temperature graph over time."""
        self.ax_temperature.cla()
        self.ax_temperature.set_title("Temperature Over Time")
        self.ax_temperature.set_xlabel("Day")
        self.ax_temperature.set_ylabel("Average Temperature")

        days = range(len(self.simulation.states))
        avg_temperatures = [
            np.mean([
                cell.temperature
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                for cell in [state.grid[x][y][z]]
            ])
            for state in self.simulation.states
        ]

        self.ax_temperature.plot(days, avg_temperatures, color="blue", label="Average Temperature")
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
                min(cell.pollution_level, 100)  # Cap pollution level to avoid overflow
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                for cell in [state.grid[x, y, z]]
            ])
            for state in self.simulation.states
        ]

        self.ax_pollution.plot(days, avg_pollution, color="red", label="Average Pollution")
        self.ax_pollution.legend()
        self.fig.canvas.draw_idle()

    def handle_key_press(self, event):
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
