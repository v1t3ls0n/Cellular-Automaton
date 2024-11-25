import numpy as np
from .Cell import Cell
import logging
import random


class State:
    def __init__(self, grid_size, initial_temperature, initial_pollution, initial_water_mass, initial_cities, initial_forests, prev_state_index=-1):
        """
        Initialize the State class.
        """
        self.grid_size = grid_size
        self.grid = np.empty(grid_size, dtype=object)
        self.prev_state_index = prev_state_index
        self.avg_temperature = initial_temperature
        self.avg_pollution = initial_pollution
        self.avg_water_mass = initial_water_mass
        self.total_cities = initial_cities
        self.total_forests = initial_forests

    def clone(self):
        """
        Create a deep clone of the current state.
        """
        cloned_state = State(
            grid_size=self.grid_size,
            initial_temperature=self.avg_temperature,
            initial_pollution=self.avg_pollution,
            initial_water_mass=self.avg_water_mass,
            initial_cities=self.total_cities,
            initial_forests=self.total_forests,
            prev_state_index=self.prev_state_index,
        )

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    current_cell = self.grid[i, j, k]
                    cloned_state.grid[i, j, k] = current_cell.clone()

        return cloned_state

    def initialize_grid(self, initial_temperature, initial_pollution, initial_water_mass, initial_cities, initial_forests):
        """
        Initialize the grid with cells to create islands surrounded by the sea.
        """
        x, y, z = self.grid_size
        elevation_map = self._generate_elevation_map()
        sea_level = z // 8  # Define sea level

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell_type = 6  # Default to air
                    elevation = elevation_map[i,
                                              j] if k <= elevation_map[i, j] else None

                    if k < elevation_map[i, j]:
                        cell_type = 0
                        # cell_type = np.random.choice([0, 3], p=[0.8, 0.2])  # Sea or Ice
                    elif k == elevation_map[i, j]:
                        cell_type = np.random.choice(
                            [0, 3], p=[0.8, 0.2])  # Sea or Ice

                    elif k == elevation_map[i, j] + 1:
                        cell_type = np.random.choice([0, 4, 5], p=[1 - (initial_cities + initial_forests) / (
                            # City, Forest, Land
                            z ** 2), initial_forests / (z ** 2), initial_cities / (z ** 2)])
                    elif k > (z - 2):
                        cell_type = np.random.choice(
                            [6, 2], p=[0.8, 0.2])  # Air or Cloud
                    else:
                        cell_type = 6

                    if cell_type in {6, 2}:
                        dx = np.random.choice([0, 1, -1])
                        dy = np.random.choice([0, 1, -1])
                        dz = np.random.choice([0, 1])
                    elif cell_type in {0,3}:
                        dx = np.random.choice([-1, 1, 0])
                        dy = np.random.choice([-1, 1, 0])
                        dz = 0
                    else:
                        dx = dy = dz = 0
                    self.grid[i, j, k] = Cell(cell_type=cell_type, direction=(dx, dy, dz),
                                              temperature=-
                                              10 if cell_type == 3 else (
                                                  initial_temperature + np.random.uniform(-2, 2)),
                                              water_mass=initial_water_mass if cell_type in {
                                                  0, 3} else 0,
                                              pollution_level=initial_pollution,
                                              elevation=elevation,
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
                    new_grid[i, j, k] = self.grid[i,
                                                  j, k].clone()  # Default to Air
        position_map = {}

        # Compute next states and positions
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = new_grid[i, j, k]
                    neighbors = self.get_neighbors(i, j, k)
                    next_cell = current_cell.get_next_state(
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

        logging.debug(f"Recalculated global attributes: Avg Temp={self.avg_temperature}, Avg Pollution={
                      self.avg_pollution}, Avg Water Mass={self.avg_water_mass}")
