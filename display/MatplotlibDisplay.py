import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.grid_size = simulation.grid_size

    def plot_3d(self):
        # Create 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Lists to store cell positions and colors
        x, y, z, colors = [], [], [], []

        # Iterate over the 3D grid
        for xi in range(self.grid_size):
            for yi in range(self.grid_size):
                for zi in range(self.grid_size):
                    cell = self.simulation.states[0].grid[xi, yi, zi]
                    x.append(xi)
                    y.append(yi)
                    z.append(zi)

                    # Define colors based on cell type
                    if cell.cell_type == 0:  # Sea
                        colors.append((0.0, 0.0, 1.0, 1.0))  # Blue (opaque)
                    elif cell.cell_type == 1:  # Land
                        colors.append((0.0, 1.0, 0.0, 1.0))  # Green (opaque)
                    elif cell.cell_type == 2:  # Clouds
                        colors.append((0.5, 0.5, 0.5, 0.8))  # Gray (semi-transparent)
                    elif cell.cell_type == 3:  # Icebergs
                        colors.append((0.5, 0.8, 1.0, 1.0))  # Sky blue (opaque)
                    elif cell.cell_type == 4:  # Forests
                        colors.append((0.0, 0.5, 0.0, 1.0))  # Dark green (opaque)
                    elif cell.cell_type == 5:  # Cities
                        colors.append((1.0, 0.0, 0.0, 1.0))  # Red (opaque)
                    else:  # Air, light blue with transparency
                        colors.append((0.7, 0.9, 1.0, 0.3))  # Light blue (transparent)

        # Plot points in 3D
        scatter = ax.scatter(x, y, z, c=colors, s=50)

        # Set axis labels
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.set_title('3D Simulation Visualization')

        # Show the plot
        plt.show()
