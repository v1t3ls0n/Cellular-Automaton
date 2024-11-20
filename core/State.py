import numpy as np
from .Cell import Cell


class State:
    def __init__(self, grid_size, initial_temperature, initial_pollution, initial_water_mass, initial_cities=None, initial_forests=None):
        """
        Initialize the State class with a 3D grid of Cell objects.
        :param grid_size: Tuple of (x, y, z) dimensions for the grid.
        :param initial_temperature: Initial temperature for all cells.
        :param initial_pollution: Initial pollution level for all cells.
        :param initial_water_mass: Initial water mass for all cells.
        :param initial_cities: (Optional) Target number of initial city cells.
        :param initial_forests: (Optional) Target number of initial forest cells.
        """
        self.grid_size = grid_size
        self.grid = self.initialize_grid(
            grid_size,
            initial_temperature,
            initial_pollution,
            initial_water_mass,
            initial_cities,
            initial_forests,
        )
        self.state_index = 0  # Represents the number of days passed

    def initialize_grid(self, grid_size, temperature, pollution, water_mass, initial_cities, initial_forests):
        """
        Initialize the grid with logical placement of all cell types.
        :param grid_size: Tuple of (x, y, z) dimensions for the grid.
        :param temperature: Initial temperature for all cells.
        :param pollution: Initial pollution level for all cells.
        :param water_mass: Initial water mass for all cells.
        :param initial_cities: Target number of city cells.
        :param initial_forests: Target number of forest cells.
        :return: A 3D numpy array of Cell objects.
        """
        city_count = forest_count = land_count = sea_count = iceberg_count = cloud_count = 0
        x, y, z = grid_size
        total_cells = x * y * z
        min_icebergs = max(1, int(total_cells * 0.01))
        sea_probability = 0.3
        iceberg_probability = sea_probability * 0.05
        cloud_probability = 0.01

        # Set default values for optional parameters
        initial_cities = initial_cities if initial_cities is not None else total_cells // 50
        initial_forests = initial_forests if initial_forests is not None else total_cells // 50

        elevation_map = self._generate_elevation_map(x, y)

        grid = np.empty((x, y, z), dtype=object)

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    rand = np.random.random()

                    cell_type = 6  # Default to air

                    # Determine cell type based on elevation and probabilities
                    if k <= elevation_map[i, j]:
                        if k <= 2:
                            if rand < sea_probability:
                                cell_type = 0  # Sea
                                sea_count += 1
                            elif rand < iceberg_probability:
                                cell_type = 3  # Iceberg
                                iceberg_count += 1
                        else:
                            cell_type = 0
                            sea_count += 1
                    elif k == elevation_map[i, j] + 1:
                        if city_count < initial_cities and forest_count < initial_forests:
                            cell_type = 5 if rand < 0.5 else 4
                            if cell_type == 5:
                                city_count += 1
                            else:
                                forest_count += 1
                        elif city_count < initial_cities:
                            cell_type = 5
                            city_count += 1
                        elif forest_count < initial_forests:
                            cell_type = 4
                            forest_count += 1
                        else:
                            cell_type = 1
                            land_count += 1
                    elif k > elevation_map[i, j] + 1:
                        if cloud_count < total_cells * cloud_probability and rand < cloud_probability:
                            cell_type = 2
                            cloud_count += 1

                    # Set pollution, temperature, and water level
                    pollution_level = pollution if cell_type in [4, 5] else 0
                    cell_temperature = temperature + np.random.uniform(-2, 2)
                    cell_water_level = water_mass if cell_type in [0, 3] else 0

                    grid[i, j, k] = Cell(cell_type, cell_temperature, cell_water_level, pollution_level)

        print(f"Grid initialized: {city_count} cities, {forest_count} forests, {land_count} land cells, "
              f"{sea_count} seas, {iceberg_count} icebergs, {cloud_count} clouds.")
        return grid


    def _generate_elevation_map(self, grid_size):
        """
        Generate an elevation map using Perlin noise to simulate terrain elevation.
        :param grid_size: Tuple of (x, y) dimensions for the grid.
        :return: A 2D numpy array representing terrain elevation.
        """
        from noise import pnoise2
        x, y, _ = grid_size
        elevation_map = np.zeros((x, y))

        for i in range(x):
            for j in range(y):
                # Normalize Perlin noise output to fit within the grid's z-dimensions
                elevation_map[i, j] = int((pnoise2(i / 10, j / 10, octaves=4) + 1) * (grid_size[2] * 0.25))

        return elevation_map

    def move_cells(self):
        """
        Move cells based on their direction property.
        """
        x, y, z = self.grid_size
        new_grid = np.empty((x, y, z), dtype=object)

        # Initialize the new grid with empty cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = Cell(6)  # Empty cells (air)

        # Move cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = self.grid[i, j, k]
                    dx, dy = current_cell.direction

                    # Calculate new position
                    new_i = (i + dx) % x
                    new_j = (j + dy) % y
                    new_k = k  # Z-direction is static in this example

                    # Move cell to new position if it's not empty
                    if current_cell.cell_type != 6:
                        new_grid[new_i, new_j, new_k] = current_cell

        self.grid = new_grid

    def update_cells(self):
        """
        Update each cell in the grid based on its interactions with neighbors.
        """
        x, y, z = self.grid_size

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = self.grid[i, j, k]

                    # Get neighbors of the current cell
                    neighbors = self.get_neighbors(i, j, k)
                    current_cell.update(neighbors)

    def get_neighbors(self, i, j, k):
        """
        Get the neighbors of a cell at position (i, j, k).
        :param i: X-coordinate.
        :param j: Y-coordinate.
        :param k: Z-coordinate.
        :return: A list of neighboring Cell objects.
        """
        neighbors = []
        x, y, z = self.grid_size
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    ni, nj, nk = (i + dx) % x, (j + dy) % y, (k + dz) % z
                    neighbors.append(self.grid[ni, nj, nk])
        return neighbors

    def next_state(self):
        """
        Calculate the next state of the grid (simulate one day).
        """
        self.move_cells()  # Move cells based on their direction
        self.update_cells()  # Update cells based on their interactions
        self.state_index += 1  # Increment the state index (day counter)

    def visualize(self):
        """
        Visualize the 3D grid using matplotlib.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x, y, z = self.grid_size
        colors = {
            0: 'blue',  # Sea
            1: 'yellow',  # Land
            2: 'gray',  # Cloud
            3: 'cyan',  # Ice
            4: 'green',  # Forest
            5: 'purple',  # City
            6: 'white'  # Air
        }

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell = self.grid[i, j, k]
                    color = colors.get(cell.cell_type, 'black')
                    ax.scatter(i, j, k, color=color)

        plt.title(f"State at Day {self.state_index}")
        plt.show()
