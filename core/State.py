import numpy as np
from .Cell import Cell
from noise import pnoise3  # Perlin noise for realistic terrain patterns


class State:
    def __init__(self, grid_size, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        self.grid_size = grid_size
        self.grid = np.full((grid_size, grid_size, grid_size), Cell(6, 0.0, 0.0, (0, 0, 0), 0, 0), dtype=object)
        self.day = 0
        self.wind_direction = (1, 1)
        self.wind_strength = 1
        self.initialize_grid(initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level)

    def initialize_grid(self, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        """Initialize the grid with logical placement of all cell types."""
        city_count = forest_count = land_count = sea_count = iceberg_count = cloud_count = 0
        total_cells = self.grid_size ** 3
        min_icebergs = max(1, int(total_cells * 0.01))
        sea_probability = 0.3
        iceberg_probability = sea_probability * 0.05
        cloud_probability = 0.1

        elevation_map = self._generate_elevation_map()

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell_type = 6  # Default to air
                    rand = np.random.random()

                    # Determine cell type based on elevation and probabilities
                    if z <= elevation_map[x, y]:
                        if z <= 2:
                            if rand < sea_probability:
                                cell_type = 0  # Sea
                                sea_count += 1
                            elif rand < iceberg_probability:
                                cell_type = 3  # Iceberg
                                iceberg_count += 1
                        else:
                            cell_type = 0
                            sea_count += 1
                    elif z == elevation_map[x, y] + 1:
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
                    elif z > elevation_map[x, y] + 1:
                        if cloud_count < total_cells * cloud_probability:
                            cell_type = 2
                            cloud_count += 1

                    # Set pollution, temperature, and water level
                    pollution_level = initial_pollution if cell_type in [4, 5] else 0
                    temperature = initial_temperature + np.random.uniform(-2, 2)
                    water_level = initial_water_level if cell_type in [0, 3] else 0

                    self.grid[x, y, z] = Cell(cell_type, temperature, 0.0, (0, 0, 0), pollution_level, water_level)

        print(f"Grid initialized: {city_count} cities, {forest_count} forests, {land_count} land cells, "
              f"{sea_count} seas, {iceberg_count} icebergs, {cloud_count} clouds.")

    def update(self):
        """Update the grid based on interactions between cells."""
        new_grid = np.full(
            (self.grid_size, self.grid_size, self.grid_size),
            Cell(6, 0.0, 0.0, (0, 0, 0), 0, 0),
            dtype=object,
        )

        forest_count = city_count = total_temperature = total_pollution = total_cells = 0

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell = self.grid[x, y, z]

                    if cell.cell_type == 4:
                        forest_count += 1
                    elif cell.cell_type == 5:
                        city_count += 1
                    if cell.cell_type != 6:
                        total_temperature += cell.temperature
                        total_pollution += cell.pollution_level
                        total_cells += 1

        self.average_temperature = total_temperature / total_cells if total_cells else 0
        self.average_pollution = total_pollution / total_cells if total_cells else 0
        forest_to_city_ratio = forest_count / city_count if city_count else 0

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    current_cell = self.grid[x, y, z]
                    
                    # Handle air cells (type 6)
                    if current_cell.cell_type == 6:
                        neighbors = self.get_neighbors_with_distances(x, y, z, include_distances=False)
                        for neighbor in neighbors:
                            # Absorb temperature and pollution
                            current_cell.temperature += 0.05 * neighbor.temperature
                            current_cell.pollution_level += min(0.01 * neighbor.pollution_level, 1.0)

                            # Check for cloud formation
                            if neighbor.cell_type == 2 and current_cell.pollution_level > 10 and current_cell.temperature > 25:
                                if np.random.random() < 0.1:  # 10% chance
                                    current_cell.cell_type = 2
                                    current_cell.water_level = neighbor.water_level * 0.5
                        continue  # Skip further updates for air cells

                    neighbors = self.get_neighbors_with_distances(x, y, z, include_distances=True)
                    simple_neighbors = [neighbor for neighbor, _ in neighbors]
                    current_cell.update(simple_neighbors, forest_count, city_count)

                    if current_cell.cell_type == 5:  # City
                        extinction_chance = 0.05 + (0.5 - forest_to_city_ratio)
                        if np.random.random() < extinction_chance:
                            current_cell.cell_type = 1  # City turns into land
                            city_count -= 1

                    elif current_cell.cell_type == 4 and self.average_pollution > 40 and self.average_temperature > 30:
                        current_cell.cell_type = 1  # Turn forest into land
                        forest_count -= 1

                        for neighbor, distance in neighbors:
                            if neighbor.cell_type == 5:
                                extinction_chance = 0.1 + abs((city_count - forest_count) / city_count) / (distance + 1)
                                if np.random.random() < extinction_chance:
                                    neighbor.cell_type = 1
                                    city_count -= 1

                    if current_cell.cell_type == 2:
                        dx, dy = self.wind_direction
                        new_x = (x + dx * self.wind_strength) % self.grid_size
                        new_y = (y + dy * self.wind_strength) % self.grid_size
                        target_cell = new_grid[new_x, new_y, z]

                        if target_cell.cell_type == 6:
                            new_grid[new_x, new_y, z] = current_cell
                        elif target_cell.cell_type == 2:
                            merged_temperature = (current_cell.temperature + target_cell.temperature) / 2
                            merged_pollution = current_cell.pollution_level + target_cell.pollution_level
                            merged_water_level = current_cell.water_level + target_cell.water_level
                            new_grid[new_x, new_y, z] = Cell(2, merged_temperature, 0.0, self.wind_direction, merged_pollution, merged_water_level)

                    if current_cell.cell_type != 6:
                        new_grid[x, y, z] = current_cell

        self.grid = new_grid

    def _generate_elevation_map(self):
        elevation_map = np.zeros((self.grid_size, self.grid_size))
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                elevation_map[x, y] = int((pnoise3(x / 10, y / 10, 0) + 1) * (self.grid_size * 0.25))
        return elevation_map

    def get_neighbors_with_distances(self, x, y, z, include_distances=False):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if (dx, dy, dz) != (0, 0, 0):
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                            neighbor = self.grid[nx, ny, nz]
                            if include_distances:
                                distance = np.sqrt(dx**2 + dy**2 + dz**2)
                                neighbors.append((neighbor, distance))
                            else:
                                neighbors.append(neighbor)
        return neighbors
