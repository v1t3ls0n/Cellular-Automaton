import numpy as np
import Cell

class State:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = np.empty((grid_size, grid_size, grid_size), dtype=object)
        self.initialize_grid()

    def initialize_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    # חלוקה לסוגי תאים
                    cell_type = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.3, 0.1, 0.1, 0.1, 0.1])
                    temperature = np.random.randint(-10, 40)
                    wind_strength = np.random.uniform(0, 10)
                    wind_direction = (np.random.choice([-1, 0, 1]), 
                                    np.random.choice([-1, 0, 1]), 
                                    np.random.choice([-1, 0, 1]))
                    pollution_level = 0 if cell_type not in [4, 5] else np.random.randint(10, 50)
                    water_level = 0 if cell_type not in [0, 3, 2] else np.random.randint(5, 20)
                    self.grid[x, y, z] = Cell(cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level)

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
