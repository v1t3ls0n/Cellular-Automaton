import numpy as np
from .Cell import Cell
import logging
import random
from collections import defaultdict

class State:
    def __init__(self, grid_size=(10, 10, 10), initial_cities_ratio=0.3, initial_forests_ratio=0.3, initial_deserts_ratio=0.4, state_index=0):
        """
        Initialize the State class.
        """
        self.grid_size = grid_size
        self.grid = np.empty(grid_size, dtype=object)
        self.initial_cities_ratio = initial_cities_ratio
        self.initial_forests_ratio = initial_forests_ratio
        self.state_index = state_index
        self.initial_deserts_ratio = initial_deserts_ratio

    def clone(self):
        """
        Create a deep clone of the current state.
        """
        cloned_state = State(
            grid_size=self.grid_size,
            initial_cities_ratio=self.initial_cities_ratio,
            initial_forests_ratio=self.initial_forests_ratio,
            initial_deserts_ratio=self.initial_deserts_ratio,
            state_index=self.state_index
        )

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cloned_state.grid[i, j, k] = self.grid[i, j, k].clone()

        return cloned_state

    def initialize_grid(self, initial_cities_ratio, initial_forests_ratio, initial_deserts_ratio):
        """
        Initialize the grid with a realistic distribution of oceans, forests, cities, deserts, and other elements.
        Adjust cloud probability dynamically based on height above the surface.
        """
        x, y, z = self.grid_size
        elevation_map = self._generate_elevation_map()

        # Adjust the ratios for realistic distributions
        total_land_ratio = initial_cities_ratio + \
            initial_forests_ratio + initial_deserts_ratio
        initial_cities_ratio /= total_land_ratio
        initial_forests_ratio /= total_land_ratio
        initial_deserts_ratio /= total_land_ratio
        # sea_prob = 1.0 - total_land_ratio  # Remaining probability for sea at z=0

        plane_surfaces_map = defaultdict(str)
        # Define temperature and pollution levels for each cell type
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
                    cell_type = 6
                    direction = (0,0,0)
                    if k >= 1:
                        if plane_surfaces_map[(i,j,k-1)] == 'sea':
                            if k < elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3], p=[0.9, 0.1])
                            elif k == elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3, 6], p=[0.6, 0.1, 0.3])
                            elif k > elevation_map[i, j]:  # Above land or sea
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

                        elif plane_surfaces_map[(i,j,k-1)] == 'land':
                            if k <= elevation_map[i, j]:
                                cell_type = 1
                            elif k == elevation_map[i, j] + 1:
                                cell_type = np.random.choice(
                                    [1, 4, 5], p=[initial_deserts_ratio, initial_forests_ratio, initial_cities_ratio])

                            elif k > elevation_map[i, j] + 1:  # Above land or sea
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

                        elif plane_surfaces_map[(i,j,k-1)] == 'sky':

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
                        else:
                            cell_type = 6
                    else:
                        cell_type = np.random.choice([0,1], p=[0.5, 0.5])
                        plane_surfaces_map[(i,j,k)] = 'land' if cell_type else 'sea'

                    match cell_type:
                        case 0 | 3:
                            plane_surfaces_map[(i,j,k)] == 'sea'
                            dx, dy = np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1])
                            direction = (dx, dy, 0)
                        case 1:
                            plane_surfaces_map[(i,j,k)] == 'land'
                            direction = (0, 0, 0)
                        case 4 | 5:
                            plane_surfaces_map[(i,j,k)] == 'forest or city'
                            direction = (0, 0, 0)
                        case 2 | 6 | 7:
                            plane_surfaces_map[(i,j,k)] == 'sky'
                            dx, dy = np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1]) 
                            dz = -1 if cell_type == 6 else 1  # Clouds rise, air falls
                            direction = (dx, dy, dz)

                    
                    logging.info(f"plane_surfaces_map[{(i,j,k)}]: {plane_surfaces_map[(i,j,k)]}")
                    temperature = cell_properties[cell_type]["temperature"] + np.random.uniform(-2, 2)
                    pollution = cell_properties[cell_type]["pollution"]

                    # Adjust movement direction and other dynamic properties
            
                    self.grid[i, j, k] = Cell(
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

    def _generate_land_map(self, x, y):
        """
        Generate a 2D map of land using Perlin noise for realistic islands.
        """
        from noise import pnoise2
        scale = 20.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        threshold = 0.2  # Adjust for land-water balance

        land_map = np.zeros((x, y), dtype=bool)
        for i in range(x):
            for j in range(y):
                noise_value = pnoise2(
                    i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                # Land if above threshold
                land_map[i, j] = noise_value > threshold
        return land_map

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
                    new_grid[i, j, k] = self.grid[i,
                                                  j, k].clone()  # Default to Air
        position_map = {}

        # Compute next states and positions
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = new_grid[i, j, k]
                    neighbors = self.get_neighbors(i, j, k)
                    next_cell = current_cell.update_state(
                        neighbors, (i, j, k), self.grid_size)
                    next_position = next_cell.move((i, j, k), self.grid_size)
                    position_map[next_position] = next_cell

        # Fill new grid and resolve collisions
        for (ni, nj, nk), updated_cell in position_map.items():
            new_grid[ni, nj, nk] = updated_cell

        self.grid = new_grid
        self._recalculate_global_attributes()

    def move_cells_on_grid(self):
        """
        Move cells in the grid based on their direction property.
        This modifies the grid in place, ensuring all cells, including air, are moved.
        """
        x, y, z = self.grid_size
        # Properly initialize new_grid
        new_grid = np.empty((x, y, z), dtype=object)

        # Initialize the new grid with Air cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = self.grid[i,
                                                  j, k].clone()  # Default to Air

        # Step 1: Compute new positions for each cell
        position_map = {}
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = self.grid[i, j, k]

                    if current_cell:
                        # Compute new position
                        new_position = current_cell.move(
                            (i, j, k), self.grid_size)
                        ni, nj, nk = new_position

                        # Resolve collisions if needed
                        if (ni, nj, nk) in position_map:
                            position_map[(ni, nj, nk)] = self.resolve_collision(
                                position_map[(ni, nj, nk)], current_cell
                            )
                        else:
                            position_map[(ni, nj, nk)] = current_cell

        # Step 2: Update the new grid with computed positions
        for (ni, nj, nk), cell in position_map.items():
            new_grid[ni, nj, nk] = cell

        # Step 3: Replace the grid with the updated one
        self.grid = new_grid
        self._recalculate_global_attributes()

    def resolve_collision(self, existing_cell, incoming_cell):
        """
        Resolve collision when two cells occupy the same position.
        Prefer non-air cells, or prioritize based on specific rules.
        """
        if existing_cell.cell_type == 6:  # If the existing cell is Air
            return incoming_cell
        if incoming_cell.cell_type == 6:  # If the incoming cell is Air
            return existing_cell
        return existing_cell  # Default: Keep the original cell

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

        logging.debug(f"Recalculated global attributes: Avg Temp={self.avg_temperature}, Avg Pollution={ self.avg_pollution}, Avg Water Mass={self.avg_water_mass}")
