import numpy as np
from .Particle import Particle
import logging
import random
from collections import defaultdict


class World:
    def __init__(self, grid_size=(10, 10, 10), initial_cities_ratio=0.3, initial_forests_ratio=0.3, initial_deserts_ratio=0.4, day_number=0):
        """
        Initialize the World class.
        """
        self.grid_size = grid_size
        self.grid = np.empty(grid_size, dtype=object)
        self.initial_cities_ratio = initial_cities_ratio
        self.initial_forests_ratio = initial_forests_ratio
        self.day_number = day_number
        self.initial_deserts_ratio = initial_deserts_ratio

    def clone(self):
        """
        Create a deep clone of the current state.
        """
        cloned_state = World(
            grid_size=self.grid_size,
            initial_cities_ratio=self.initial_cities_ratio,
            initial_forests_ratio=self.initial_forests_ratio,
            initial_deserts_ratio=self.initial_deserts_ratio,
            day_number=self.day_number
        )

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cloned_state.grid[i, j, k] = self.grid[i, j, k].clone()

        return cloned_state

    def initialize_grid(self, initial_cities_ratio, initial_forests_ratio, initial_deserts_ratio):
        """
        Initialize the grid with a realistic distribution of oceans, forests, cities, deserts, and other elements.
        Includes logic to prevent overlapping forests/cities and adjusts cloud/air probabilities dynamically by height.
        """
        x, y, z = self.grid_size
        elevation_map = self._generate_elevation_map()

        # Adjust the ratios for realistic distributions
        total_land_ratio = initial_cities_ratio + \
            initial_forests_ratio + initial_deserts_ratio
        initial_cities_ratio /= total_land_ratio
        initial_forests_ratio /= total_land_ratio
        initial_deserts_ratio /= total_land_ratio

        plane_surfaces_map = {}  # Use a dictionary to track the surface type
        cell_properties = {
            0: {"temperature": 15, "pollution": 0},  # Sea
            1: {"temperature": 25, "pollution": 5},  # Desert
            2: {"temperature": 5, "pollution": 0},   # Cloud
            3: {"temperature": -10, "pollution": 0},  # Ice
            4: {"temperature": 20, "pollution": 0},  # Forest
            5: {"temperature": 30, "pollution": 20},  # City
            6: {"temperature": 10, "pollution": 5},  # Air
        }

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell_type = 6  # Default to Air
                    direction = (0, 0, 0)

                    if k == 0:
                        # Surface layer: Assign initial sea or land
                        cell_type = np.random.choice([0, 1], p=[0.5, 0.5])
                        plane_surfaces_map[(
                            i, j, k)] = 'unused_land' if cell_type == 1 else 'sea'
                    else:
                        # Check the surface type below this cell
                        surface_type = plane_surfaces_map.get(
                            (i, j, k - 1), 'sky')

                        if surface_type == 'sea':
                            if k < elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    # Mostly sea, some ice
                                    [0, 3], p=[0.9, 0.1])
                            elif k == elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3, 6], p=[0.6, 0.1, 0.3])  # Sea/Ice/Air
                            elif k > elevation_map[i, j]:  # Above sea
                                if k >= 0.9 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.6, 0.4])  # Air or Cloud
                                elif k >= 0.8 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.7, 0.3])  # Air or Cloud
                                elif k >= 0.7 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.9, 0.1])  # Air or Cloud
                                else:
                                    cell_type = 6

                        elif surface_type == 'unused_land':
                            if k <= elevation_map[i, j]:
                                cell_type = 1  # Unused Land (Desert)
                            elif k == elevation_map[i, j] + 1:
                                # Prevent placing forests/cities above existing forests/cities
                                if plane_surfaces_map.get((i, j, k - 1)) != 'used_land':
                                    cell_type = np.random.choice(
                                        [1, 4, 5], p=[initial_deserts_ratio, initial_forests_ratio, initial_cities_ratio])
                                    plane_surfaces_map[(i, j, k)] = 'used_land'
                            elif k > elevation_map[i, j] + 1:  # Above land
                                if k >= 0.9 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.6, 0.4])  # Air or Cloud
                                elif k >= 0.8 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.7, 0.3])  # Air or Cloud
                                elif k >= 0.7 * z:
                                    cell_type = np.random.choice(
                                        [6, 2], p=[0.9, 0.1])  # Air or Cloud
                                else:
                                    cell_type = 6

                        elif surface_type == 'used_land':
                            # Above forests/cities, only air or cloud
                            if k >= 0.9 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.6, 0.4])  # Air or Cloud
                            elif k >= 0.8 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.7, 0.3])  # Air or Cloud
                            elif k >= 0.7 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.9, 0.1])  # Air or Cloud
                            else:
                                cell_type = 6

                        elif surface_type == 'sky':
                            # Above sky, only air or cloud
                            if k >= 0.9 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.6, 0.4])  # Air or Cloud
                            elif k >= 0.8 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.7, 0.3])  # Air or Cloud
                            elif k >= 0.7 * z:
                                cell_type = np.random.choice(
                                    [6, 2], p=[0.9, 0.1])  # Air or Cloud
                            else:
                                cell_type = 6

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
                        direction = (np.random.choice(
                            [-1, 0, 1]), np.random.choice([-1, 0, 1]), 0)
                    elif cell_type in {2, 6}:  # Cloud/Air
                        dx, dy = np.random.choice(
                            [-1, 0, 1]), np.random.choice([-1, 0, 1])
                        dz = -1 if cell_type == 6 else 1  # Air falls, clouds rise
                        direction = (dx, dy, dz)

                    # Logging for debugging
                    logging.info(f"plane_surfaces_map[{(i, j, k)}]: {
                                 plane_surfaces_map[(i, j, k)]}")

                    # Create the cell
                    temperature = cell_properties[cell_type]["temperature"] + \
                        np.random.uniform(-2, 2)
                    pollution = cell_properties[cell_type]["pollution"]
                    self.grid[i, j, k] = Particle(
                        cell_type=cell_type,
                        temperature=temperature,
                        water_mass=1 if cell_type in {0, 2, 3} else 0,
                        pollution_level=pollution,
                        direction=direction,
                        elevation=elevation_map[i, j],
                    )

        self._recalculate_global_attributes()
        logging.debug(f"Grid initialized successfully with dimensions: {
                      self.grid_size}")

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
        x, y, z = self.grid_size
        # Properly initialize new_grid
        new_grid = np.empty((x, y, z), dtype=object)

        # Initialize the new grid with Air cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = self.grid[i,j, k].clone()  
        
        position_map = {}

        # Compute next states and positions
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell = new_grid[i, j, k] 
                    neighbors = self.get_neighbors(i, j, k)
                    cell.update_state(neighbors)
                    next_position = cell.get_next_position((i, j, k), self.grid_size)
                    position_map[next_position] = cell

        # Fill new grid and resolve collisions
        for (ni, nj, nk), updated_cell in position_map.items():
            new_grid[ni, nj, nk] = updated_cell

        self.grid = new_grid
        self._recalculate_global_attributes()

    def get_neighbors(self, i, j, k):
        """
        Get the neighbors of a cell at position (i, j, k).
        Returns a list of neighbor cells.
        """
        neighbors = []
        x, y, z = self.grid_size
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip the current cell itself
                    ni, nj, nk = (i + dx) % x, (j + dy) % y, (k + dz) % z
                    neighbors.append(self.grid[ni, nj, nk])
        return neighbors

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
