import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba


class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.current_day = 0
        self.fig, self.ax_3d, self.ax_graph = None, None, None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth

    def plot_3d(self):
        # Create the figure and subplots
        self.fig = plt.figure(figsize=(10, 5))
        self.ax_3d = self.fig.add_subplot(121, projection='3d')
        self.ax_graph = self.fig.add_subplot(122)

        # Precompute 3D visualizations
        self.precompute_visualizations()

        # Render pollution graph (static)
        self.render_pollution_graph()

        # Add keyboard navigation
        self.fig.canvas.mpl_connect("key_press_event", self.handle_key_press)

        # Render the initial day
        self.render_day(self.current_day)

        # Show the plot
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


    def render_pollution_graph(self):
        """Render the pollution graph over time."""
        self.ax_graph.cla()
        self.ax_graph.set_title("Pollution Over Time")
        self.ax_graph.set_xlabel("Day")
        self.ax_graph.set_ylabel("Average Pollution")

        avg_pollution = []
        for state in self.simulation.states:
            total_pollution = sum(
                cell.pollution_level for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                for cell in [state.grid[x, y, z]]
            )
            total_cells = state.grid.shape[0] * state.grid.shape[1] * state.grid.shape[2]
            avg_pollution.append(total_pollution / total_cells)

        self.ax_graph.plot(range(len(avg_pollution)), avg_pollution, color="red", label="Average Pollution")
        self.ax_graph.legend()
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
