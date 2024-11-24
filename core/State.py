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

        # Initialize the grid if this is the first state
        if prev_state_index == -1:
            self.initialize_grid(initial_temperature, initial_pollution, initial_water_mass, initial_cities, initial_forests)

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
                    cloned_state.grid[i, j, k] = current_cell.clone() if current_cell else None

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
                    elevation = elevation_map[i, j] if k <= elevation_map[i, j] else None

                    if k <= sea_level:
                        cell_type = np.random.choice([0, 3], p=[0.9, 0.1])  # Sea or Ice
                    elif k == elevation_map[i, j] + 1:
                        cell_type = np.random.choice([0, 4, 5], p=[1 - (initial_cities + initial_forests) / (z ** 2), initial_forests / (z ** 2), initial_cities / (z ** 2)])  # City, Forest, Land
                    elif k > (z - 2):
                        cell_type = np.random.choice([6, 2], p=[0.8, 0.2])  # Air or Cloud

                    self.grid[i, j, k] = Cell(
                        cell_type=cell_type,
                        direction=(np.random.choice([1, -1]), np.random.choice([1, -1])) if cell_type in {6, 2} else (0, 0),
                        temperature=-10 if cell_type == 3 else (initial_temperature + np.random.uniform(-2, 2)),
                        water_mass=initial_water_mass if cell_type in {0, 3} else 0,
                        pollution_level=initial_pollution if cell_type == 6 else 0,
                        elevation=elevation,
                    )

        self._recalculate_global_attributes()
        logging.debug(f"Grid initialized successfully with dimensions: {self.grid_size}")

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
        Update cells in the grid based on their interactions with neighbors.
        """
        x, y, z = self.grid_size
        new_grid = np.empty_like(self.grid)

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = self.grid[i, j, k]
                    if current_cell is None:
                        continue
                    neighbors = self.get_neighbors(i, j, k)
                    new_grid[i, j, k] = current_cell.get_next_state(neighbors, (i, j, k), self.grid_size)

        self.grid = new_grid
        self._recalculate_global_attributes()


    def move_cells_on_grid(self):
        """
        Move cells in the grid based on their direction property.
        This modifies the grid in place.
        """
        x, y, z = self.grid_size
        new_grid = np.empty((x, y, z), dtype=object)

        # Initialize the new grid with Air cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = Cell(cell_type=6)  # Default to Air

        elevation_limit = z * 0.8  # Define the sky layer threshold for cloud formation

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    current_cell = self.grid[i, j, k]
                    if current_cell is None:
                        continue

                    # Let the cell handle elevation logic
                    current_cell.elevate_and_update(elevation_limit)

                    # Determine the new position for movement
                    new_position = current_cell.move((i, j, k), self.grid_size)
                    ni, nj, nk = new_position

                    # Resolve potential collisions in the new grid
                    new_grid[ni, nj, nk] = self.resolve_collision(new_grid[ni, nj, nk], current_cell)

        self.grid = new_grid

    def resolve_collision(self, existing_cell, incoming_cell):
        """
        Resolve collision when two cells occupy the same position.
        Currently, prioritizes the incoming cell if the existing cell is Air.
        """
        if existing_cell.cell_type == 6:  # If the existing cell is Air
            return incoming_cell  # Replace Air with the incoming cell
        if existing_cell.cell_type == 0 and incoming_cell.cell_type == 2:
            # Clouds replace Sea in elevated positions
            return incoming_cell
        return existing_cell  # Default: keep the original cell


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

        logging.debug(f"Recalculated global attributes: Avg Temp={self.avg_temperature}, Avg Pollution={self.avg_pollution}, Avg Water Mass={self.avg_water_mass}")
