import numpy as np
import logging
from core.conf import config
from .Particle import Particle

class World:
    def __init__(self, grid_size=None, initial_ratios=None, day_number=0):
        """
        Initialize the World class.
        """
        # Set grid size and default ratios from config if not provided
        self.grid_size = grid_size or config["default_grid_size"]
        self.grid = np.empty(self.grid_size, dtype=object)
        
        initial_ratios = initial_ratios or config["initial_ratios"]
        self.initial_cities_ratio = initial_ratios["city"]
        self.initial_forests_ratio = initial_ratios["forest"]
        self.initial_deserts_ratio = initial_ratios["desert"]
        
        self.day_number = day_number

    def clone(self):
        """
        Create a deep clone of the current state.
        """
        cloned_state = World(
            grid_size=self.grid_size,
            initial_ratios={
                "city": self.initial_cities_ratio,
                "forest": self.initial_forests_ratio,
                "desert": self.initial_deserts_ratio,
            },
            day_number=self.day_number
        )

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cloned_state.grid[i, j, k] = self.grid[i, j, k].clone()

        return cloned_state

    def initialize_grid(self):
        """
        Initialize the grid with a realistic distribution of oceans, forests, cities, deserts, and other elements.
        Includes logic to prevent overlapping forests/cities and adjusts cloud/air probabilities dynamically by height.
        """
        x, y, z = self.grid_size
        elevation_map = self._generate_elevation_map()

        # Normalize the initial land ratios
        total_land_ratio = self.initial_cities_ratio + self.initial_forests_ratio + self.initial_deserts_ratio
        cities_ratio = self.initial_cities_ratio / total_land_ratio
        forests_ratio = self.initial_forests_ratio / total_land_ratio
        deserts_ratio = self.initial_deserts_ratio / total_land_ratio

        plane_surfaces_map = {}  # Use a dictionary to track the surface type

        # Use cell properties from config
        baseline_temperature = config["baseline_temperature"]
        baseline_pollution_level = config["baseline_pollution_level"]

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell_type = 6  # Default to Air
                    direction = (0, 0, 0)

                    if k == 0:
                        # Surface layer: Assign initial sea or land
                        cell_type = np.random.choice(
                            [0, 1], p=[0.5, 0.5])  # 50% Sea, 50% Land
                        plane_surfaces_map[(i, j, k)] = 'unused_land' if cell_type == 1 else 'sea'
                    else:
                        # Check the surface type below this cell
                        surface_type = plane_surfaces_map.get((i, j, k - 1), 'sky')

                        if surface_type == 'sea':
                            if k < elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3], p=[0.99, 0.01])  # Mostly sea, some ice
                            elif k == elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3, 6], p=[0.65, 0.05, 0.3])  # Sea/Ice/Air
                            elif k > elevation_map[i, j]:  # Above sea
                                cell_type = self._get_dynamic_air_or_cloud_type(k, z)

                        elif surface_type == 'unused_land':
                            if k <= elevation_map[i, j]:
                                cell_type = 1  # Unused Land (Desert)
                            elif k == elevation_map[i, j] + 1:
                                # Prevent placing forests/cities above existing forests/cities
                                if plane_surfaces_map.get((i, j, k - 1)) != 'used_land':
                                    cell_type = np.random.choice(
                                        [1, 4, 5],
                                        p=[deserts_ratio, forests_ratio, cities_ratio]
                                    )
                                    plane_surfaces_map[(i, j, k)] = 'used_land'
                            elif k > elevation_map[i, j] + 1:  # Above land
                                cell_type = self._get_dynamic_air_or_cloud_type(k, z)

                        elif surface_type == 'used_land':
                            # Above forests/cities, only air or cloud
                            cell_type = self._get_dynamic_air_or_cloud_type(k, z)

                        elif surface_type == 'sky':
                            # Above sky, only air or cloud
                            cell_type = self._get_dynamic_air_or_cloud_type(k, z)

                    # Update plane_surfaces_map
                    if cell_type in {0, 3}:  # Sea or Ice
                        plane_surfaces_map[(i, j, k)] = 'sea'
                    elif cell_type == 1:  # Unused Land (Desert)
                        plane_surfaces_map[(i, j, k)] = 'unused_land'
                    elif cell_type in {4, 5}:  # Forest or City
                        plane_surfaces_map[(i, j, k)] = 'used_land'
                    elif cell_type in {2, 6}:  # Cloud or Air
                        plane_surfaces_map[(i, j, k)] = 'sky'

                    # Set direction for dynamic cells
                    if cell_type in {0, 3}:  # Sea/Ice
                        direction = (0, 0, 0)
                        np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1])
                    elif cell_type in {2, 6}:  # Cloud/Air
                        dx, dy = np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1])
                        dz = -1 if cell_type == 6 else 1  # Air falls, clouds rise
                        direction = (dx, dy, dz)

                    # Create the cell
                    temperature = baseline_temperature[cell_type] + np.random.uniform(-2, 2)
                    pollution = baseline_pollution_level[cell_type]
                    self.grid[i, j, k] = Particle(
                        cell_type=cell_type,
                        temperature=temperature,
                        water_mass=1 if cell_type in {0, 2, 3} else 0,
                        pollution_level=pollution,
                        direction=direction,
                        position=(i, j, k),
                        grid_size=self.grid_size
                    )

        self._recalculate_global_attributes()
        logging.debug(f"Grid initialized successfully with dimensions: {self.grid_size}")

    def _get_dynamic_air_or_cloud_type(self, k, z):
        """
        Determine the type of air or cloud based on elevation.
        """
        if k >= 0.9 * z:
            return np.random.choice([6, 2], p=[0.6, 0.4])  # Air or Cloud
        elif k >= 0.8 * z:
            return np.random.choice([6, 2], p=[0.7, 0.3])  # Air or Cloud
        elif k >= 0.7 * z:
            return np.random.choice([6, 2], p=[0.9, 0.1])  # Air or Cloud
        else:
            return 6  # Default to Air

    def _get_dynamic_air_or_cloud_type(self, k, z):
        """
        Determine the type of air or cloud based on elevation.
        """
        if k >= 0.9 * z:
            return np.random.choice([6, 2], p=[0.6, 0.4])  # Air or Cloud
        elif k >= 0.8 * z:
            return np.random.choice([6, 2], p=[0.7, 0.3])  # Air or Cloud
        elif k >= 0.7 * z:
            return np.random.choice([6, 2], p=[0.9, 0.1])  # Air or Cloud
        else:
            return 6  # Default to Air

    def _generate_elevation_map(self):
        """
        Generate an elevation map using Perlin noise for smooth terrain.
        """
        from noise import pnoise2

        x, y, _ = self.grid_size
        elevation_map = np.zeros((x, y))

        scale = 10.0  # Adjust for larger/smaller features
        octaves = 10  # Higher value for more detail
        persistence = 0.5
        lacunarity = 2.0

        for i in range(x):
            for j in range(y):
                elevation_map[i, j] = int((pnoise2(i / scale, j / scale, octaves=octaves,
                                                   persistence=persistence, lacunarity=lacunarity) + 1) * (self.grid_size[2] // 5))

        return elevation_map
    
    def update_cells_on_grid(self):
        """
        Update the cells on the grid to compute their next states and resolve collisions.
        Handles non-air cells first to avoid illogical overwriting and processes air cells afterward.
        """
        x, y, z = self.grid_size
        # Properly initialize a new grid to hold the updated state
        new_grid = np.empty((x, y, z), dtype=object)

        # Clone the current grid to initialize new cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = self.grid[i, j, k].clone()

        position_map = {}

        # First pass: Handle non-air cells (priority update for stability)
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell = self.grid[i, j, k]

                    # Skip air cells for now
                    if cell.cell_type == 6:
                        continue

                    next_position = cell.get_next_position()

                    if next_position not in position_map:
                        position_map[next_position] = cell
                    else:
                        # Resolve collision logically
                        other_cell = position_map[next_position]
                        resolved_position = self.resolve_collision(cell, other_cell, position_map)
                        position_map[resolved_position] = cell

        # Second pass: Handle air cells (less priority, fill gaps)
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell = self.grid[i, j, k]

                    # Process only air cells
                    if cell.cell_type != 6:
                        continue

                    next_position = cell.get_next_position()

                    if next_position not in position_map:
                        position_map[next_position] = cell
                    else:
                        # Find a nearby empty spot for the air cell
                        empty_position = self.find_nearest_empty_position(next_position, position_map)
                        if empty_position:
                            position_map[empty_position] = cell
                        else:
                            # Keep air cell static if no space is found
                            position_map[(i, j, k)] = cell

        # Populate the new grid with updated cells
        for (ni, nj, nk), updated_cell in position_map.items():
            new_grid[ni, nj, nk] = updated_cell

        self.grid = new_grid  # Replace the current grid with the updated one
        self._recalculate_global_attributes()

    def resolve_collision(self, cell1, cell2, position_map):
        """
        Handle collisions between two cells. Adjust attributes and resolve positioning.
        """
        # Higher priority to non-air cells; air cells relocate
        if cell1.cell_type == 6 or cell2.cell_type == 6:
            air_cell = cell1 if cell1.cell_type == 6 else cell2
            non_air_cell = cell2 if cell1.cell_type == 6 else cell1

            # Try to find a nearby empty position for the air cell
            empty_position = self.find_nearest_empty_position(air_cell.position, position_map)
            if empty_position:
                return empty_position
            else:
                # If no space is found, keep the non-air cell in place
                return non_air_cell.position
        else:
            # For two non-air cells, merge their attributes logically
            self.merge_cells(cell1, cell2)
            return cell2.position  # Keep one cell's position for the merged cell

    def merge_cells(self, cell1, cell2):
        """
        Merge two cells by averaging their attributes.
        """
        # Example logic: Average water_mass and temperature
        cell1.water_mass = (cell1.water_mass + cell2.water_mass) / 2
        cell1.temperature = (cell1.temperature + cell2.temperature) / 2
        cell2.water_mass = cell1.water_mass
        cell2.temperature = cell1.temperature

        # Keep the higher pollution level
        cell1.pollution_level = max(cell1.pollution_level, cell2.pollution_level)
        cell2.pollution_level = cell1.pollution_level

        # Optionally adjust other attributes


    def find_nearest_empty_position(self, position, position_map):
        """
        Find the nearest empty position to the given position within the grid bounds.
        """
        x, y, z = position
        for dx, dy, dz in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.grid_size[0] and 0 <= ny < self.grid_size[1] and 0 <= nz < self.grid_size[2]:
                if (nx, ny, nz) not in position_map:
                    return (nx, ny, nz)
        return None  # Return None if no valid empty position is found









    def get_neighbors(self, x, y, z):
        """
        Get the neighbors of the cell at position (x, y, z) and their positions.
        """
        neighbors = []
        positions = []
        for dx, dy, dz in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.grid_size[0] and 0 <= ny < self.grid_size[1] and 0 <= nz < self.grid_size[2]:
                neighbors.append(self.grid[nx, ny, nz])
                positions.append((nx, ny, nz))
        # Return both neighbors and positions
        return list(zip(neighbors, positions))

    def _recalculate_global_attributes(self):
        """
        Recalculate global attributes based on the current grid.
        """
        total_temperature = 0
        total_pollution = 0
        total_water_mass = 0
        total_cities = 0
        total_forests = 0
        total_cells = 0

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cell = self.grid[i, j, k]
                    if cell and cell.cell_type != 6:  # Exclude air cells
                        total_temperature += cell.temperature
                        total_pollution += cell.pollution_level
                        total_water_mass += cell.water_mass
                        if cell.cell_type == 5:  # City
                            total_cities += 1
                        elif cell.cell_type == 4:  # Forest
                            total_forests += 1
                        total_cells += 1

        self.avg_temperature = total_temperature / total_cells if total_cells > 0 else 0
        self.avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
        self.avg_water_mass = total_water_mass / total_cells if total_cells > 0 else 0
        self.total_cities = total_cities
        self.total_forests = total_forests

        logging.debug(f"Recalculated global attributes: Avg Temp={self.avg_temperature}, Avg Pollution={
                      self.avg_pollution}, Avg Water Mass={self.avg_water_mass}")
