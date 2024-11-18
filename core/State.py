import numpy as np
from .Cell import Cell
from noise import pnoise3  # Perlin noise for realistic terrain patterns


class State:
    def __init__(self, grid_size, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        self.grid_size = grid_size
        # Initialize all grid positions with "air" cells by default
        self.grid = np.full((grid_size, grid_size, grid_size), Cell(
            "air", 0.0, 0.0, (0, 0, 0), 0, 0), dtype=object)
        self.day = 0
        self.wind_direction = (1, 1)  # Example: (x, y) direction
        self.wind_strength = 1  # Number of cells clouds move per update
        self.initialize_grid(
            initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level
        )

    def initialize_grid(self, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        """Initialize the grid dynamically based on user input, ensuring logical placement of all cell types."""
        city_count = 0
        forest_count = 0
        land_count = 0
        sea_count = 0
        iceberg_count = 0
        cloud_count = 0
        total_cells = self.grid_size ** 3
        # At least 1% of cells as icebergs
        min_icebergs = max(1, int(total_cells * 0.01))
        min_water_level = 1  # Minimum water level

        # Dynamic placement probabilities
        city_probability = initial_cities / total_cells
        forest_probability = initial_forests / total_cells
        sea_probability = 0.3  # Default 30% for sea
        iceberg_probability = sea_probability * 0.05  # Icebergs as a fraction of sea
        cloud_probability = 0.1  # Cloud probability
        land_probability = 1 - city_probability-forest_probability-sea_probability - \
            iceberg_probability-cloud_probability  # Start with 20% default land probability

        # Create an elevation map using Perlin noise to determine terrain elevation
        elevation_map = np.zeros((self.grid_size, self.grid_size))
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                # Normalize and cap elevation
                elevation_map[x, y] = int(
                    (pnoise3(x / 10, y / 10, 0) + 1) * (self.grid_size * 0.25))

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell_type = "air"  # Default to "air"
                    rand = np.random.random()

                    # Below or at elevation: water or icebergs
                    if z <= elevation_map[x, y]:
                        if z <= 2:  # Prioritize sea and icebergs in the lowest layers
                            if sea_count < total_cells * sea_probability and rand < sea_probability:
                                cell_type = 0  # Sea
                                sea_count += 1
                            elif iceberg_count < min_icebergs or (rand < iceberg_probability and iceberg_count < total_cells * iceberg_probability):
                                cell_type = 3  # Iceberg
                                iceberg_count += 1
                            else:
                                cell_type = 0  # Fallback to sea
                                sea_count += 1
                    # First layer above terrain: land/city/forest
                    elif z == elevation_map[x, y] + 1:  # First layer above terrain
                        cell_type = 1  # Land
                        land_count += 1
                    elif z == elevation_map[x, y] + 2:  # Second layer above terrain
                        if city_count < initial_cities and (forest_count >= initial_forests or city_count <= forest_count):
                            cell_type = 5  # City
                            city_count += 1
                        elif forest_count < initial_forests and (city_count >= initial_cities or forest_count <= city_count):
                            cell_type = 4  # Forest
                            forest_count += 1

                    # Higher layers with a gap for clouds
                    elif z > elevation_map[x, y] + 2:
                        if cloud_count < total_cells * cloud_probability:
                            cell_type = 2  # Cloud
                            cloud_count += 1
                        else:
                            cell_type = "air"
                            

                    # Set pollution, temperature, and water level
                    pollution_level = initial_pollution if cell_type in [
                        5, 4] else 0
                    temperature = temperature = initial_temperature + np.random.uniform(-2, 2)
                    water_level = max(min_water_level, initial_water_level) if cell_type in [
                        0, 3] else 0

                    self.grid[x, y, z] = Cell(
                        cell_type, temperature, 0.0, (0, 0,
                                                      0), pollution_level, water_level
                    )

        # Log initialization summary
        print(f"Grid initialized: {city_count} cities, {forest_count} forests, {land_count} land cells, "
              f"{sea_count} seas, {iceberg_count} icebergs, {cloud_count} clouds.")

    def update(self):
        """Update the state based on current grid and interactions."""
        # Initialize new_grid with "air" cells
        new_grid = np.full(
            (self.grid_size, self.grid_size, self.grid_size),
            Cell("air", 0.0, 0.0, (0, 0, 0), 0, 0),
            dtype=object,
        )

        # Calculate the current counts of forests and cities
        forest_count = 0
        city_count = 0

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    current_cell = self.grid[x, y, z]

                    # Count forests and cities
                    if current_cell.cell_type == 4:  # Forest
                        forest_count += 1
                    elif current_cell.cell_type == 5:  # City
                        city_count += 1

        # Update each cell based on its type and neighbors
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    current_cell = self.grid[x, y, z]
                    neighbors = self.get_neighbors(x, y, z)

                    # Update the cell with the current counts
                    current_cell.update(neighbors, forest_count, city_count)

                    if current_cell.cell_type == 2:  # Clouds
                        # Movement logic
                        dx, dy = self.wind_direction
                        new_x = (x + dx * self.wind_strength) % self.grid_size
                        new_y = (y + dy * self.wind_strength) % self.grid_size

                        target_cell = new_grid[new_x, new_y, z]

                        if target_cell.cell_type == "air":
                            # Move the cloud to the empty air cell
                            new_grid[new_x, new_y, z] = current_cell
                            # Clear the current position
                            self.grid[x, y, z] = Cell(
                                "air", 0.0, 0.0, (0, 0, 0), 0, 0)
                        elif target_cell.cell_type == 2:  # Another cloud
                            # Merge properties of the two clouds
                            merged_temperature = (
                                current_cell.temperature + target_cell.temperature) / 2
                            merged_pollution = current_cell.pollution_level + target_cell.pollution_level
                            merged_water_level = current_cell.water_level + target_cell.water_level

                            new_grid[new_x, new_y, z] = Cell(
                                2,  # Still a cloud
                                merged_temperature,
                                0.0,
                                self.wind_direction,
                                merged_pollution,
                                merged_water_level,
                            )
                            # Clear the current position
                            self.grid[x, y, z] = Cell(
                                "air", 0.0, 0.0, (0, 0, 0), 0, 0)
                        else:
                            # If the target cell is not air or cloud, keep the cloud in its current position
                            new_grid[x, y, z] = current_cell
                            # Ensure the original cell is not duplicated
                            self.grid[x, y, z] = Cell(
                                "air", 0.0, 0.0, (0, 0, 0), 0, 0)
                    elif current_cell.cell_type != "air":
                        # Copy all other cells directly
                        new_grid[x, y, z] = current_cell

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
