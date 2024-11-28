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
                        position=(i, j, k),
                        grid_size = self.grid_size
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
        """
        Update the cells on the grid to compute their next states and resolve collisions.
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
        transfer_map = {}

        # First pass: Compute the next state for all cells and collect transfers
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    # Use original grid for neighbor lookup
                    cell = self.grid[i, j, k]
                    neighbors = self.get_neighbors(
                        i, j, k)  # Retrieve neighbors

                    # Unpack only the Particle objects
                    unpacked_neighbors = [
                        neighbor for neighbor, _ in neighbors]
                    new_grid[i, j, k].update_state(
                        unpacked_neighbors)  # Update state of the cell

                    # Compute water transfers and store in transfer map
                    for neighbor, neighbor_pos in neighbors:
                        if neighbor.cell_type in {2, 6}:  # Only clouds or air
                            transfer_amount = (
                                neighbor.water_mass - cell.water_mass) * 0.05
                            if transfer_amount != 0:
                                transfer_key = ((i, j, k), neighbor_pos)
                                transfer_map[transfer_key] = transfer_map.get(
                                    transfer_key, 0) + transfer_amount

        # Apply transfers to update water mass
        for (from_pos, to_pos), transfer in transfer_map.items():
            fx, fy, fz = from_pos
            tx, ty, tz = to_pos
            if 0 <= fx < x and 0 <= fy < y and 0 <= fz < z:
                new_grid[fx, fy, fz].water_mass -= transfer
            if 0 <= tx < x and 0 <= ty < y and 0 <= tz < z:
                new_grid[tx, ty, tz].water_mass += transfer

        # Second pass: Determine new positions and resolve collisions
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    # Use updated grid for next position calculation
                    cell = new_grid[i, j, k]
                    next_position = cell.get_next_position()
                    cell.position = next_position
                    if next_position not in position_map:
                        position_map[next_position] = cell
                    else:
                        # Handle collision by averaging attributes
                        other_cell = position_map[next_position]
                        self.resolve_collision(cell, other_cell)

        # Populate the new grid with updated cells
        for (ni, nj, nk), updated_cell in position_map.items():
            new_grid[ni, nj, nk] = updated_cell

        self.grid = new_grid  # Replace the current grid with the updated one
        self._recalculate_global_attributes()

    def resolve_collision(self, cell1, cell2):
        """
        Handle collisions between two cells. Adjust attributes accordingly.
        """
        # Example logic: Average water_mass and temperature
        cell1.water_mass = (cell1.water_mass + cell2.water_mass) / 2
        cell1.temperature = (cell1.temperature + cell2.temperature) / 2
        cell2.water_mass = cell1.water_mass
        cell2.temperature = cell1.temperature

        # Keep the higher pollution level
        cell1.pollution_level = max(
            cell1.pollution_level, cell2.pollution_level)
        cell2.pollution_level = cell1.pollution_level

        # Optionally adjust other attributes or preserve one cell's state

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
