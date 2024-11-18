import numpy as np
from .Cell import Cell


class State:
    def __init__(self, grid_size, day=0):
        self.grid_size = grid_size
        self.grid = np.empty((grid_size, grid_size, grid_size), dtype=object)
        self.day = day
        self.initialize_grid()

    def initialize_grid(self):
        """Initialize the grid with dynamic water levels and ensure realistic terrain and water interactions."""
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    # Assign cell types based on z-level
                    if z <= 1:  # Lowest level: mostly sea
                        cell_type = np.random.choice([0, 3], p=[0.9, 0.1])
                    elif z <= 5:  # Forests, land, or cities
                        cell_type = np.random.choice(
                            [1, 4, 5], p=[0.1, 0.3, 0.6])
                    else:  # Clouds
                        cell_type = np.random.choice([None, 2], p=[0.5, 0.5])
                        

                    # Calculate water level with increased variability
                    base_water_level = np.random.uniform(1.0, 5.0)
                    curve_variation = np.sin(x * 0.4) * np.cos(y * 0.4) * 2.5
                    random_variation = np.random.uniform(-1.5, 1.5)
                    water_level = base_water_level + curve_variation + random_variation

                    # Ensure water levels do not exceed terrain height
                    if cell_type in [1, 4, 5]:  # Land, forests, or cities
                        water_level = max(0, min(water_level, z))

                    # Set pollution levels
                    pollution_level = {
                        0: np.random.uniform(0, 2),   # Sea
                        3: np.random.uniform(0, 1),   # Icebergs
                        5: np.random.uniform(10, 30),  # Cities
                        4: np.random.uniform(0, 3),   # Forests
                        2: np.random.uniform(5, 10),  # Clouds
                    }.get(cell_type, np.random.uniform(0, 5))

                    # Assign other attributes
                    temperature = np.random.uniform(-5, 30)
                    wind_strength = np.random.uniform(0, 3)
                    wind_direction = (
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                        np.random.choice([-1, 0, 1]),
                    )

                    self.grid[x][y][z] = Cell(
                        cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level
                    )

                    # Log initialization
                    print(f"Initialized Cell ({x}, {y}, {z}) - Type: {cell_type}, Water Level: {water_level:.2f}, "
                          f"Pollution: {pollution_level:.2f}, Temperature: {temperature:.2f}")

    def update(self):
        """Update the state based on current grid and interactions."""
        new_grid = np.empty_like(self.grid, dtype=object)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    neighbors = self.get_neighbors(x, y, z)
                    current_cell = self.grid[x, y, z]

                    # Create a copy of the current cell to avoid overwriting during updates
                    new_cell = Cell(
                        current_cell.cell_type,
                        current_cell.temperature,
                        current_cell.wind_strength,
                        current_cell.wind_direction,
                        current_cell.pollution_level,
                        current_cell.water_level,
                    )

                    # Update the cell's state based on its neighbors
                    new_cell.update(neighbors)

                    # Adjust water levels dynamically
                    if new_cell.cell_type in [1, 4, 5]:  # Land, forests, cities
                        new_cell.water_level = max(
                            0, min(new_cell.water_level, z + 1))
                    elif new_cell.cell_type == 0:  # Sea
                        new_cell.water_level = max(0, new_cell.water_level)

                    # Limit pollution and temperature
                    new_cell.pollution_level = min(
                        new_cell.pollution_level, 100)
                    new_cell.temperature = min(new_cell.temperature, 50)

                    new_grid[x, y, z] = new_cell

                    # Log updates
                    # print(f"Cell ({x}, {y}, {z}) - Type: {current_cell.cell_type}, Initial Water Level: {current_cell.water_level:.2f}, "
                    #       f"Updated Water Level: {new_cell.water_level:.2f}, Pollution: {
                    #           new_cell.pollution_level:.2f}, "
                    #       f"Temperature: {new_cell.temperature:.2f}")

        self.grid = new_grid

    def get_neighbors(self, x, y, z):
        """Retrieve neighbors for a given cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if (dx, dy, dz) != (0, 0, 0):  # Exclude the current cell
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                            neighbors.append(self.grid[nx, ny, nz])
        return neighbors
