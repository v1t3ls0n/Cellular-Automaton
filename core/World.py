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
        self.initial_deserts_ratio = initial_ratios["desert"]
        self.initial_vacuum_ratio = initial_ratios["vacuum"]
        # Initialize global attributes
        self.avg_temperature = 0
        self.avg_pollution = 0
        self.avg_water_mass = 0
        self.total_cities = 0
        self.total_forests = 0
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
                "vacuum": self.initial_vacuum_ratio
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

        # Normalize the initial ratios without modifying instance variables
        total_ratio = (
            self.initial_cities_ratio
            + self.initial_forests_ratio
            + self.initial_deserts_ratio
            + self.initial_vacuum_ratio
        )

        cities_ratio = self.initial_cities_ratio / total_ratio
        forests_ratio = self.initial_forests_ratio / total_ratio
        deserts_ratio = self.initial_deserts_ratio / total_ratio
        vacuum_ratio = self.initial_vacuum_ratio / total_ratio

        plane_surfaces_map = {}  # Use a dictionary to track the surface type

        # Use cell properties from config
        baseline_temperature = config["baseline_temperature"]
        baseline_pollution_level = config["baseline_pollution_level"]

        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell_type = 8  # Default to Vacuum
                    direction = (0, 0, 0)

                    if k == 0:
                        # Surface layer: Assign initial sea or land
                        cell_type = np.random.choice(
                            [0, 1], p=[0.5, 0.5])  # 50% Sea, 50% Land
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
                                    [0, 3], p=[0.99, 0.01])
                            elif k == elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3, 6], p=[0.65, 0.05, 0.3])  # Sea/Ice/Air
                            elif k > elevation_map[i, j]:  # Above sea
                                cell_type = self._get_dynamic_air_or_cloud_type(
                                    k, z)

                        elif surface_type == 'unused_land':
                            if k <= elevation_map[i, j]:
                                cell_type = 1  # Unused Land (Desert)
                            elif k == elevation_map[i, j] + 1:
                                # Prevent placing forests/cities above existing forests/cities
                                if plane_surfaces_map.get((i, j, k - 1)) != 'used_land':
                                    cell_type = np.random.choice(
                                        [1, 4, 5, 8],
                                        p=[deserts_ratio, forests_ratio,
                                            cities_ratio, vacuum_ratio]
                                    )
                                    plane_surfaces_map[(i, j, k)] = 'used_land'
                            elif k > elevation_map[i, j] + 1:  # Above land
                                cell_type = self._get_dynamic_air_or_cloud_type(
                                    k, z)

                        elif surface_type == 'used_land':
                            # Above forests/cities, only air or cloud
                            cell_type = self._get_dynamic_air_or_cloud_type(
                                k, z)

                        elif surface_type == 'sky':
                            # Above sky, only air or cloud
                            cell_type = self._get_dynamic_air_or_cloud_type(
                                k, z)

                    # Update plane_surfaces_map
                    if cell_type in {0, 3}:  # Sea or Ice
                        plane_surfaces_map[(i, j, k)] = 'sea'
                    elif cell_type == 1:  # Unused Land (Desert)
                        plane_surfaces_map[(i, j, k)] = 'unused_land'
                    elif cell_type in {4, 5}:  # Forest or City
                        plane_surfaces_map[(i, j, k)] = 'used_land'
                    elif cell_type in {2, 6}:  # Cloud or Air
                        plane_surfaces_map[(i, j, k)] = 'sky'
                    elif cell_type == 8:  # Vacuum
                        plane_surfaces_map[(i, j, k)] = 'vacuum'

                    # Set direction for dynamic cells
                    if cell_type in {0, 3}:  # Sea/Ice
                        # direction = (0, 0, 0)
                        np.random.choice(
                            [-1, 0, 1]), np.random.choice([-1, 0, 1])
                    elif cell_type in {2, 6}:  # Cloud/Air
                        dx, dy = np.random.choice(
                            [-1, 0, 1]), np.random.choice([-1, 0, 1])
                        dz = -1 if cell_type == 6 else 1  # Air falls, clouds rise
                        direction = (dx, dy, dz)

                    # Create the cell
                    temperature = baseline_temperature[cell_type] + \
                        np.random.uniform(-2, 2)
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
        logging.debug(f"Grid initialized successfully with dimensions: {
                      self.grid_size}")

    def _get_dynamic_air_or_cloud_type(self, k, z):
        """
        Determine the type of air, cloud, or vacuum based on elevation.
        """
        vacuum_ratio = self.initial_vacuum_ratio

        if k >= 0.9 * z:
            air_ratio = 0.5 - vacuum_ratio
            cloud_ratio = 0.4
        elif k >= 0.8 * z:
            air_ratio = 0.6 - vacuum_ratio
            cloud_ratio = 0.3
        elif k >= 0.7 * z:
            air_ratio = 0.8 - vacuum_ratio
            cloud_ratio = 0.1
        else:
            return 6  # Default to Air

        # Normalize probabilities to ensure they sum to 1
        total_ratio = air_ratio + cloud_ratio + vacuum_ratio
        air_ratio /= total_ratio
        cloud_ratio /= total_ratio
        vacuum_ratio /= total_ratio

        return np.random.choice([6, 2, 8], p=[air_ratio, cloud_ratio, vacuum_ratio])

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

    def apply_day_night_cycle(self, day):
        """
        Apply a day-night temperature cycle to the entire grid.

        Args:
            day (int): The current day or time step in the simulation.
        """
        cycle_amplitude = config.get("cycle_amplitude", 5)  # Temperature swing
        base_temperature = config.get(
            "ambient_temperature", 20)  # Base temperature

        # Calculate a sinusoidal adjustment for the day-night cycle
        temp_adjustment = cycle_amplitude * np.sin(2 * np.pi * (day % 24) / 24)

        # Apply the adjustment to all cells
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                for z in range(self.grid_size[2]):
                    cell = self.grid[x, y, z]
                    if cell.cell_type != 8:  # Skip Vacuum cells
                        cell.temperature += temp_adjustment

    def update_cells_on_grid(self):
        """
        Update the cells on the grid to compute their next states and resolve collisions.
        """
        # self.apply_day_night_cycle(self.day_number)
        x, y, z = self.grid_size
        new_grid = np.empty((x, y, z), dtype=object)

        # Clone the current grid to initialize new cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    new_grid[i, j, k] = self.grid[i, j, k]
        position_map = {}
        transfer_map = {}

        # First pass: Update states and collect transfers
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    # Use original grid for neighbor lookup
                    cell = self.grid[i, j, k]
                    if cell.cell_type == 8:  # Skip Vacuum cells
                        continue

                    # Retrieve neighbors and unpack only the `Particle` objects
                    neighbors = [neighbor for neighbor,
                                 _ in self.get_neighbors(i, j, k)]

                    # Update state and collect water transfers
                    cell_transfer_map = cell.update_state(neighbors)
                    for (to_pos, transfer_amount) in cell_transfer_map.items():
                        transfer_key = ((i, j, k), to_pos)
                        transfer_map[transfer_key] = transfer_map.get(
                            transfer_key, 0) + transfer_amount

        # Apply transfers directly to the grid
        for (from_pos, to_pos), transfer_amount in transfer_map.items():
            fx, fy, fz = from_pos
            tx, ty, tz = to_pos

            # Ensure valid positions
            if 0 <= fx < x and 0 <= fy < y and 0 <= fz < z:
                new_grid[fx, fy, fz].water_mass = max(
                    0, new_grid[fx, fy, fz].water_mass - transfer_amount
                )
            if 0 <= tx < x and 0 <= ty < y and 0 <= tz < z:
                new_grid[tx, ty, tz].water_mass += transfer_amount

            # Second pass: Determine new positions and resolve collisions
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    # Use updated grid for next position calculation
                    cell = new_grid[i, j, k]
                    next_position = cell.get_next_position()

                    # Debugging output for position calculations
                    logging.debug(
                        f"Cell ({i}, {j}, {k}) -> Next Position: {next_position}")
                    logging.debug(f"Before update: {position_map.keys()}")
                    logging.debug(f"Cell ({i}, {j}, {k}) moving to {
                                  next_position}")

                    if next_position not in position_map:
                        position_map[next_position] = cell
                    else:
                        # Handle collision by resolving interactions
                        other_cell = position_map[next_position]
                        logging.debug(f"Collision detected between {cell} and {
                                      other_cell} at {next_position}")

                        self.resolve_collision(cell, other_cell)

                        # Save both resolved cells back to the position map
                        # Assume `resolve_collision` modifies `cell` and `other_cell` in place
                        resolved_positions = [
                            cell.position, other_cell.position]
                        resolved_cells = [cell, other_cell]

                        for pos, resolved_cell in zip(resolved_positions, resolved_cells):
                            if pos:
                                position_map[pos] = resolved_cell
                        logging.debug(f"Day {self.day_number}: Cell ({
                                      i}, {j}, {k}) state: {cell}")
                        logging.debug(f"Collision resolved: {
                                      cell} with {other_cell}")
                        logging.debug(f"Transfer applied: {transfer_map}")

            # Populate the final grid
            for (ni, nj, nk), cell in position_map.items():
                new_grid[ni, nj, nk] = cell

            self.grid = new_grid
            self._recalculate_global_attributes()

    def apply_transfers(self, new_grid, transfer_map):
        """
        Applies all water mass transfers from the transfer map to the updated grid.
        Args:
            new_grid (np.ndarray): The updated grid to apply transfers to.
            transfer_map (dict): A dictionary mapping (to_pos) -> transfer_amount.
        """
        for (from_pos, to_pos), transfer_amount in transfer_map.items():
            fx, fy, fz = from_pos
            tx, ty, tz = to_pos

            # Ensure valid positions
            if 0 <= fx < self.grid_size[0] and 0 <= fy < self.grid_size[1] and 0 <= fz < self.grid_size[2]:
                new_grid[fx, fy, fz].water_mass -= transfer_amount
            if 0 <= tx < self.grid_size[0] and 0 <= ty < self.grid_size[1] and 0 <= tz < self.grid_size[2]:
                new_grid[tx, ty, tz].water_mass += transfer_amount

    def resolve_collision(self, cell1, cell2):
        """
        Resolves a collision between two cells, updating their states based on predefined rules.

        Args:
            cell1: The first colliding cell.
            cell2: The second colliding cell.
        """
        # If both cells are of the same type
        if cell1.cell_type == cell2.cell_type:
            if cell1.cell_type == 2:  # Both are Clouds
                # Merge water mass and average temperature
                cell1.water_mass += cell2.water_mass
                cell1.temperature = (cell1.temperature + cell2.temperature) / 2
                # Convert cell2 to Vacuum after merging
                cell2.cell_type = 8
            elif cell1.cell_type == 7:  # Both are Rain
                # Combine water mass into cell1 and remove cell2
                cell1.water_mass += cell2.water_mass
                cell2.cell_type = 8
            else:
                # No interaction; keep both cells as they are
                pass

        # Handle specific interactions between different cell types
        # Air and Rain
        elif (cell1.cell_type, cell2.cell_type) in [(6, 7), (7, 6)]:
            # Rain falls; Air moves up
            if cell1.cell_type == 7:  # cell1 is Rain
                cell1.go_down()
                cell2.go_up()
            else:  # cell2 is Rain
                cell2.go_down()
                cell1.go_up()

        # Air and Cloud
        elif (cell1.cell_type, cell2.cell_type) in [(6, 2), (2, 6)]:
            # Air goes down; Cloud moves up
            if cell1.cell_type == 2:  # cell1 is Cloud
                cell1.go_up()
                cell2.go_down()
            else:  # cell2 is Cloud
                cell2.go_up()
                cell1.go_down()

        # Cloud and Rain
        elif (cell1.cell_type, cell2.cell_type) in [(2, 7), (7, 2)]:
            # Rain falls; Cloud moves up
            if cell1.cell_type == 7:  # cell1 is Rain
                cell1.go_down()
                cell2.go_up()
            else:  # cell2 is Rain
                cell2.go_down()
                cell1.go_up()

        # Air/Cloud/Rain and Vacuum
        elif (cell1.cell_type, cell2.cell_type) in [(6, 8), (7, 8), (2, 8)]:
            # Swap the cell with the vacuum
            if cell1.cell_type == 8:  # cell1 is Vacuum
                cell1.cell_type = cell2.cell_type
                cell1.copy_state_from(cell2)
                cell2.cell_type = 8
            else:  # cell2 is Vacuum
                cell2.cell_type = cell1.cell_type
                cell2.copy_state_from(cell1)
                cell1.cell_type = 8

        else:
            # Default behavior: No collision resolution for other cases
            pass

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
        cell1.pollution_level = max(
            cell1.pollution_level, cell2.pollution_level)
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
        # return neighbors

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
