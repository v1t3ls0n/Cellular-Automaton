import numpy as np
from .Cell import Cell


class State:
    def __init__(self, grid_size, day=0):
        self.grid_size = grid_size
        self.grid = np.empty((grid_size, grid_size, grid_size), dtype=object)
        self.day = day
        self.initialize_grid()

    def initialize_grid(self):
        """Initialize the grid with more dynamic distributions and ensure proper layering."""
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    if z == 0:  # Lowest level is sea
                        cell_type = 0
                    elif z <= 2:  # Land, cities, and icebergs
                        cell_type = np.random.choice([1, 3, 5], p=[0.5, 0.2, 0.3])
                    elif z <= 4:  # Forests, cities, or land
                        cell_type = np.random.choice([1, 4, 5], p=[0.3, 0.4, 0.3])
                    else:  # High levels are mostly clouds
                        cell_type = 2

                    # Assign water levels and pollution based on cell type
                    if cell_type == 0:  # Sea
                        water_level = np.random.uniform(1, 3)
                        pollution_level = 0
                    elif cell_type == 3:  # Icebergs
                        water_level = np.random.uniform(2, 3)
                        pollution_level = 0
                    elif cell_type == 5:  # Cities
                        water_level = 0
                        pollution_level = np.random.uniform(10, 50)
                    elif cell_type == 4:  # Forests
                        water_level = np.random.uniform(0, 1)
                        pollution_level = 0
                    elif cell_type == 2:  # Clouds
                        water_level = np.random.uniform(1, 2)
                        pollution_level = np.random.uniform(1, 5)
                    else:  # Land or undefined
                        water_level = 0
                        pollution_level = np.random.uniform(0, 5)

                    temperature = np.random.uniform(-5, 35)
                    wind_strength = np.random.uniform(0, 5)
                    wind_direction = (
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                    )

                    self.grid[x][y][z] = Cell(
                        cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level
                    )

        # Ensure forests and cities are placed on land
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    if self.grid[x][y][z].cell_type in [4, 5]:  # Forests or Cities
                        if not any(self.grid[x][y][z_].cell_type == 1 for z_ in range(z)):
                            self.grid[x][y][z].cell_type = 1  # Reset to land if no land below

    def update(self):
        """Update the state based on current grid and interactions."""
        new_grid = np.empty_like(self.grid, dtype=object)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    neighbors = self.get_neighbors(x, y, z)
                    new_cell = Cell(
                        self.grid[x, y, z].cell_type,
                        self.grid[x, y, z].temperature,
                        self.grid[x, y, z].wind_strength,
                        self.grid[x, y, z].wind_direction,
                        self.grid[x, y, z].pollution_level,
                        self.grid[x, y, z].water_level,
                    )
                    new_cell.update(neighbors)
                    new_grid[x, y, z] = new_cell
        self.grid = new_grid

    def get_neighbors(self, x, y, z):
        """Retrieve neighbors for a given cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if (dx, dy, dz) != (0, 0, 0):
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                            neighbors.append(self.grid[nx, ny, nz])
        return neighbors
