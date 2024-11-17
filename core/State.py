import numpy as np
from .Cell import Cell

class State:
    def __init__(self, grid_size, day=0):
        self.grid_size = grid_size
        self.grid = np.empty((grid_size, grid_size, grid_size), dtype=object)
        self.day = day
        self.initialize_grid()

    def initialize_grid(self):
        """Initialize the grid with forests and cities placed at the same levels as land."""
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    if z <= np.random.randint(0, 2):  # Lowest levels mostly water
                        cell_type = 0  # Sea
                    elif z <= np.random.randint(2, 4):  # Slightly above water
                        cell_type = 1  # Land
                    elif z <= np.random.randint(4, 6):  # Moderate heights
                        base_cell_type = 1  # Ensure land is the base
                        # Randomly place forests and cities on top of land
                        cell_type = np.random.choice([1, 4, 5], p=[0.15, 0.35, 0.5])
                    elif z <= np.random.randint(6, 8):  # Higher levels
                        cell_type = 4  # Forests dominate at higher altitudes
                    else:
                        cell_type = 2  # Clouds at the highest altitudes

                    # Adjust water levels and pollution based on cell type
                    if cell_type == 0:  # Sea
                        water_level = np.random.uniform(1, 3)  # Varying water levels
                        pollution_level = np.random.uniform(0, 5)  # Slight pollution
                    elif cell_type == 3:  # Icebergs
                        water_level = np.random.uniform(2, 5)  # Pronounced icebergs
                        pollution_level = 0
                    elif cell_type == 5:  # Cities
                        water_level = 0.5
                        pollution_level = np.random.uniform(10, 50)  # Initial pollution
                    elif cell_type == 4:  # Forests
                        water_level = np.random.uniform(0, 2)  # Forests can have damp soil
                        pollution_level = 0
                    elif cell_type == 1:  # Land
                        water_level = 0
                        pollution_level = np.random.uniform(0, 10)  # Some pollution from nearby cities
                    elif cell_type == 2:  # Clouds
                        water_level = np.random.uniform(1, 3)  # Initial rain content
                        pollution_level = 0
                    else:
                        water_level = 0
                        pollution_level = 0

                    # Assign other environmental properties
                    temperature = np.random.uniform(-10, 35)  # Wider temperature range
                    wind_strength = np.random.uniform(0, 10)
                    wind_direction = (
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                    )

                    # Create the cell
                    self.grid[x][y][z] = Cell(
                        cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level
                    )

        # Enforce forests and cities at the same level as land
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    if self.grid[x][y][z].cell_type in [4, 5]:  # Forests or Cities
                        # Check levels below for land (1)
                        if any(
                            self.grid[x][y][z_].cell_type == 1 for z_ in range(z)
                        ):
                            self.grid[x][y][z].cell_type = 1.1  # Reset to land if no land below



    def update(self):
        new_grid = np.copy(self.grid)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    neighbors = self.get_neighbors(x, y, z)
                    new_grid[x, y, z].update(neighbors)
        self.grid = new_grid

    def get_neighbors(self, x, y, z):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if (dx, dy, dz) != (0, 0, 0):
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                            neighbors.append(self.grid[nx, ny, nz])
        return neighbors
