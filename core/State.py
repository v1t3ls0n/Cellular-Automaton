import numpy as np
from .Cell import Cell
from noise import pnoise3  # Perlin noise for realistic terrain patterns

class State:
    def __init__(self, grid_size, initial_cities, initial_forests, initial_pollution,
                 initial_temperature, initial_water_level):
        self.grid_size = grid_size
        self.grid = np.empty((grid_size, grid_size, grid_size), dtype=object)
        self.day = 0
        self.initialize_grid(
            initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level
        )
    
    
    
    def initialize_grid(self, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        """Initialize the grid with realistic 3D terrain using Perlin noise and logical cloud distribution."""
        city_count = 0
        forest_count = 0
        sea_count = 0
        land_count = 0
        cloud_count = 0
        iceberg_count = 0
        total_cells = self.grid_size ** 3  # Total number of cells in the grid

        # Noise parameters
        scale = 0.1  # Adjust terrain smoothness
        sea_level = self.grid_size * 0.3  # Define sea level as 30% of the grid height
        cloud_level = self.grid_size * 0.8  # Define cloud level as 80% of the grid height

        # Create 3D Perlin noise for terrain
        elevation_map = np.zeros((self.grid_size, self.grid_size, self.grid_size))
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    elevation_map[x, y, z] = pnoise3(x * scale, y * scale, z * scale)

        # Normalize elevation map to fit the grid height
        elevation_map = (elevation_map - elevation_map.min()) / (elevation_map.max() - elevation_map.min()) * self.grid_size

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell_type = None
                    elevation = elevation_map[x, y, z]

                    # Determine cell type based on elevation and layer (z)
                    if z <= sea_level:  # Below sea level
                        rand = np.random.random()
                        if sea_count < total_cells * 0.3 and rand < 0.7:  # Increase sea probability
                            cell_type = 0  # Sea
                            sea_count += 1
                        elif iceberg_count < total_cells * 0.1 and rand < 0.9:  # Increase iceberg probability
                            cell_type = 3  # Iceberg
                            iceberg_count += 1
                    elif z <= elevation:  # Land layer
                        rand = np.random.random()
                        if city_count < initial_cities and rand < 0.2:
                            cell_type = 5  # City
                            city_count += 1
                        elif forest_count < initial_forests and rand < 0.4:
                            cell_type = 4  # Forest
                            forest_count += 1
                        else:
                            cell_type = 1  # Land
                            land_count += 1
                    elif z > cloud_level:  # Clouds in upper layers
                        rand = np.random.random()
                        if rand < 0.8:  # Set higher probability for clouds
                            cell_type = 2  # Cloud
                            cloud_count += 1

                    # Fallback logic
                    if cell_type is None:
                        if z <= sea_level:
                            cell_type = 0  # Sea
                            sea_count += 1
                        elif z <= self.grid_size * 0.6:
                            cell_type = 1  # Land
                            land_count += 1
                        elif z > cloud_level:
                            if rand < 0.8:  # Even fallback prioritizes clouds
                                cell_type = 2  # Cloud
                                cloud_count += 1

                    # Set pollution, temperature, and water level
                    pollution_level = initial_pollution if cell_type in [5, 4] else 0
                    temperature = initial_temperature
                    water_level = initial_water_level if cell_type in [0, 3] else 0

                    # Assign cell
                    self.grid[x][y][z] = Cell(
                        cell_type, temperature, 0.0, (0, 0, 0), pollution_level, water_level
                    )

        # Log initialization summary
        print(f"Grid initialized: {city_count} cities, {forest_count} forests, {land_count} land cells, {sea_count} seas, {iceberg_count} icebergs, {cloud_count} clouds.")
                 
    def update(self):
        """Update the state based on current grid and interactions."""
        new_grid = np.empty_like(self.grid, dtype=object)

        # Count forests and cities in the current grid
        global_forest_count = np.sum(
            cell.cell_type == 4 for x in range(self.grid_size)
            for y in range(self.grid_size)
            for z in range(self.grid_size)
            for cell in [self.grid[x, y, z]]
        )
        global_city_count = np.sum(
            cell.cell_type == 5 for x in range(self.grid_size)
            for y in range(self.grid_size)
            for z in range(self.grid_size)
            for cell in [self.grid[x, y, z]]
        )

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
                    new_cell.update(neighbors, global_forest_count, global_city_count)

                    # Limit water levels to prevent unrealistic values
                    if new_cell.cell_type in [1, 4, 5]:  # Land, forests, cities
                        new_cell.water_level = max(0, min(new_cell.water_level, z))
                    elif new_cell.cell_type == 0:  # Sea
                        new_cell.water_level = max(0, new_cell.water_level)

                    # Limit pollution levels to avoid overflow
                    new_cell.pollution_level = min(new_cell.pollution_level, 100)

                    # Limit temperature to avoid runaway effects
                    new_cell.temperature = min(new_cell.temperature, 50)

                    new_grid[x][y][z] = new_cell

        # Update the grid with the new state
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
