import numpy as np
import logging
from core.conf import config
from .Particle import Particle


class World:
    """
    Represents the simulation world, including the grid of particles and associated behaviors.
    """

    config = config

    def __init__(self, grid_size=None, initial_ratios=None, day_number=0):
        """
        Initialize the World class.

        Args:
            grid_size (tuple): Dimensions of the grid (x, y, z). Defaults to config's default grid size.
            initial_ratios (dict): Initial ratios for cell types. Defaults to config's initial ratios.
            day_number (int): The current day in the simulation.
        """
        self.grid_size = grid_size or config["default_grid_size"]
        self.grid = np.empty(self.grid_size, dtype=object)

        initial_ratios = initial_ratios or config["initial_ratios"]
        self.initial_cities_ratio = initial_ratios["city"]
        self.initial_forests_ratio = initial_ratios["forest"]
        self.initial_deserts_ratio = initial_ratios["desert"]
        self.initial_vacuum_ratio = initial_ratios["vacuum"]

        self.day_number = day_number

    def clone(self):
        """
        Create a deep copy of the current World state.

        Returns:
            World: A cloned instance of the current World.
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
                    if self.grid[i, j, k] is None:
                        self.grid[i, j, k] = Particle(
                            cell_type=8,  # Default to Vacuum
                            temperature=0,
                            water_mass=0,
                            pollution_level=0,
                            direction=(0, 0, 0),
                            position=(i, j, k),
                            grid_size=self.grid_size
                        )
                    cloned_state.grid[i, j, k] = self.grid[i, j, k].clone()

        return cloned_state

    def initialize_grid(self):
        """
        Initialize the grid with a realistic distribution of various cell types, such as oceans, forests, cities,
        deserts, and other elements. Includes logic to:
        - Prevent overlapping forests and cities.
        - Adjust cloud/air probabilities dynamically based on elevation.
        - Ensure diversity in cell types while maintaining realistic environmental conditions.

        The initialization process uses a combination of ratios (e.g., for deserts, forests, cities, vacuum) and 
        elevation mapping (generated using Perlin noise) to assign cell types and properties.

        Steps:
        1. Generate an elevation map for terrain features.
        2. Normalize initial ratios to calculate probabilities for cell assignment.
        3. Loop through all cells in the grid, assigning types based on height and neighboring conditions.
        4. Configure additional properties like temperature, pollution, and direction for dynamic cells.

        Returns:
            None
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

        plane_surfaces_map = {}  # Tracks the type of surface for each plane

        # Use baseline values for temperature and pollution from config
        baseline_temperature = config["baseline_temperature"]
        baseline_pollution_level = config["baseline_pollution_level"]

        for i in range(x):
            for j in range(y):
                for k in range(z):

                    if self.grid[i, j, k] is None:
                        # Default to vacuum
                        self.grid[i, j, k] = Particle(
                            cell_type=8,  # Vacuum
                            temperature=0,
                            water_mass=0,
                            pollution_level=0,
                            direction=(0, 0, 0),
                            position=(i, j, k),
                            grid_size=self.grid_size
                        )

                    cell_type = 8  # Default to Vacuum
                    direction = (0, 0, 0)

                    if k == 0:
                        # Surface layer: Assign initial sea or land
                        cell_type = np.random.choice(
                            [0, 1], p=[0.5, 0.5]  # 50% Sea, 50% Land
                        )
                        plane_surfaces_map[(i, j, k)] = (
                            'unused_land' if cell_type == 1 else 'sea'
                        )
                    else:
                        # Check the surface type below this cell
                        surface_type = plane_surfaces_map.get(
                            (i, j, k - 1), 'sky'
                        )

                        if surface_type == 'sea':
                            # Sea layer behavior
                            if k < elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    # Mostly sea, some ice
                                    [0, 3], p=[0.99, 0.01]
                                )
                            elif k == elevation_map[i, j]:
                                cell_type = np.random.choice(
                                    [0, 3, 6], p=[0.75, 0.10, 0.15]  # Sea/Ice/Air
                                )
                            elif k > elevation_map[i, j]:  # Above sea
                                cell_type = self._get_dynamic_air_or_cloud_type(
                                    k, z)

                        elif surface_type == 'unused_land':
                            # Land layer behavior
                            if k <= elevation_map[i, j]:
                                cell_type = 1  # Unused Land (Desert)
                            elif k == elevation_map[i, j] + 1:
                                # Prevent forests/cities above existing forests/cities
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

                    # Update the plane_surfaces_map based on the assigned cell type
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

                    # Assign direction for dynamic cells
                    if cell_type in {0, 3}:  # Sea/Ice
                        direction = (0, 0, 0)  # Static cells
                    elif cell_type in {2, 6}:  # Cloud/Air
                        dx, dy = np.random.choice(
                            [-1, 0, 1]), np.random.choice([-1, 0, 1])
                        dz = -1 if cell_type == 6 else 1  # Air falls, clouds rise
                        direction = (dx, dy, dz)

                    if cell_type != 8:
                        # Create the particle for the cell
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

        self._recalculate_global_attributes()  # Update global stats
        logging.info(f"Grid initialized successfully with dimensions: {
                     self.grid_size}")

    def _get_dynamic_air_or_cloud_type(self, k, z):
        """
        Determine the type of Air, Cloud, or Vacuum based on elevation.

        Args:
            k (int): Current elevation.
            z (int): Maximum elevation.

        Returns:
            int: Cell type (6: Air, 2: Cloud, 8: Vacuum).
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

        # Normalize probabilities
        total_ratio = air_ratio + cloud_ratio + vacuum_ratio
        air_ratio /= total_ratio
        cloud_ratio /= total_ratio
        vacuum_ratio /= total_ratio

        return np.random.choice([6, 2, 8], p=[air_ratio, cloud_ratio, vacuum_ratio])

    def _generate_elevation_map(self):
        """
        Generate an elevation map using Perlin noise for smooth terrain.

        Returns:
            np.ndarray: A 2D elevation map.
        """
        from noise import pnoise2

        x, y, _ = self.grid_size
        elevation_map = np.zeros((x, y))

        scale = 10.0  # Scale for terrain features
        octaves = 10  # Detail level
        persistence = 0.5
        lacunarity = 2.0

        for i in range(x):
            for j in range(y):
                elevation_map[i, j] = int((pnoise2(i / scale, j / scale, octaves=octaves,
                                                   persistence=persistence, lacunarity=lacunarity) + 1) * (self.grid_size[2] // 5))

        return elevation_map

    def update_cells_on_grid(self):
        """
        Update all cells in the grid based on their next states and resolve collisions.
        """
        x, y, z = self.grid_size

        # Phase 1: Compute water transfers
        transfer_map = self.accumulate_water_transfers()

        # Phase 2: Apply transfers
        self.apply_water_transfers(transfer_map)

        updates = {}

        # Phase 3: Compute next states for all cells
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    cell = self.grid[i, j, k]
                    if cell is not None and cell.cell_type != 8:  # Skip vacuum
                        if cell.cell_type == 7:  # Rain
                            below = self.grid[i, j, k -
                                              1] if k - 1 >= 0 else None
                            # Ground types
                            if below and below.cell_type in {1, 4, 5}:
                                below.water_mass += cell.water_mass  # Absorb rain
                                cell.cell_type = 6  # Turn into air
                            elif below and below.cell_type == 6:  # Air
                                below.water_mass += cell.water_mass
                                cell.water_mass = 0
                            else:  # Rain continues falling
                                cell.position = (i, j, k - 1)
                        neighbors = [
                            self.grid[nx, ny, nz]
                            for nx, ny, nz in self.get_neighbor_positions(i, j, k)
                            if self.grid[nx, ny, nz] is not None
                        ]
                        updates[(i, j, k)] = cell.compute_next_state(neighbors)

        # Phase 4: Resolve collisions
        position_map = {}
        for (i, j, k), updated_cell in updates.items():
            next_position = updated_cell.get_next_position()
            if next_position not in position_map:
                position_map[next_position] = updated_cell
            else:
                position_map[next_position] = self.resolve_collision(
                    position_map[next_position], updated_cell
                )

        # Phase 5: Populate the new grid
        new_grid = np.empty_like(self.grid)
        for (i, j, k), cell in position_map.items():
            new_grid[i, j, k] = cell

        # Fill remaining cells with vacuum
        for i in range(x):
            for j in range(y):
                for k in range(z):
                    if new_grid[i, j, k] is None:
                        new_grid[i, j, k] = Particle(
                            cell_type=8,  # Vacuum
                            temperature=0,
                            water_mass=0,
                            pollution_level=0,
                            direction=(0, 0, 0),
                            position=(i, j, k),
                            grid_size=self.grid_size
                        )

        self.grid = new_grid
        self._recalculate_global_attributes()

    def resolve_collision(self, cell1, cell2):
        """
        Resolve collisions between two cells.

        Args:
            cell1 (Particle): The first cell involved in the collision.
            cell2 (Particle): The second cell involved in the collision.

        Returns:
            Particle: The resolved cell after the collision.
        """
        # Rain falls through air or vacuum
        if cell1.cell_type == 7 and cell2.cell_type in {6, 8}:
            return cell1
        elif cell2.cell_type == 7 and cell1.cell_type in {6, 8}:
            return cell2
        elif cell1.cell_type == 7 and cell2.cell_type == 7:  # Merge rain cells
            cell1.water_mass += cell2.water_mass
            return cell1
        # Default collision resolution
        return cell1 if self.config["cell_type_weights"][cell1.cell_type] >= self.config["cell_type_weights"][cell2.cell_type] else cell2

    def get_neighbor_positions(self, i, j, k):
        """
        Get the positions of neighboring cells for the given cell position (i, j, k).

        Args:
            i (int): The x-coordinate of the cell.
            j (int): The y-coordinate of the cell.
            k (int): The z-coordinate of the cell.

        Returns:
            list: A list of tuples representing the positions of neighboring cells.
        """
        neighbors = []
        directions = [
            (-1, 0, 0), (1, 0, 0),  # Left and right
            (0, -1, 0), (0, 1, 0),  # Up and down
            (0, 0, -1), (0, 0, 1)   # Below and above
        ]

        for dx, dy, dz in directions:
            nx, ny, nz = i + dx, j + dy, k + dz
            if 0 <= nx < self.grid_size[0] and 0 <= ny < self.grid_size[1] and 0 <= nz < self.grid_size[2]:
                neighbors.append((nx, ny, nz))

        return neighbors

    def _recalculate_global_attributes(self):
        """
        Recalculate global attributes like average temperature, pollution, water mass,
        and counts of cities, forests, and rain cells.
        """
        total_temperature = 0
        total_pollution = 0
        total_water_mass = 0
        total_cities = 0
        total_forests = 0
        total_cells = 0
        total_rain = 0

        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cell = self.grid[i, j, k]
                    if cell is None:
                        continue

                    total_temperature += cell.temperature
                    total_pollution += cell.pollution_level
                    total_water_mass += cell.water_mass
                    if cell.cell_type == 5:  # City
                        total_cities += 1
                    elif cell.cell_type == 4:  # Forest
                        total_forests += 1
                    elif cell.cell_type == 7:  # Rain
                        total_rain += 1

                    total_cells += 1

        self.avg_temperature = total_temperature / total_cells if total_cells > 0 else 0
        self.avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
        self.avg_water_mass = total_water_mass / total_cells if total_cells > 0 else 0
        self.total_cities = total_cities
        self.total_forests = total_forests
        self.total_rain = total_rain
        logging.info(
            f"Recalculated global attributes: Avg Temp={
                self.avg_temperature}, "
            f"Avg Pollution={self.avg_pollution}, Avg Water Mass={
                self.avg_water_mass}, "
            f"Total Cities={self.total_cities}, Total Forests={
                self.total_forests}, Total Rain={total_rain}"
        )

    def accumulate_water_transfers(self):
        """
        Compute all water transfers for the grid.

        Returns:
            dict: A transfer map with positions as keys and transfer amounts as values.
        """
        transfer_map = {}
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cell = self.grid[i, j, k]
                    if cell and cell.cell_type in {2, 6}:  # Cloud or Air
                        neighbors = [
                            self.grid[nx, ny, nz] for nx, ny, nz in self.get_neighbor_positions(i, j, k)
                        ]
                        cell_transfers = cell.calculate_water_transfer(
                            neighbors)
                        for neighbor_pos, transfer_amount in cell_transfers.items():
                            transfer_map[neighbor_pos] = transfer_map.get(
                                neighbor_pos, 0) + transfer_amount

        return transfer_map

    def apply_water_transfers(self, transfer_map):
        """
        Apply the water transfers to the grid based on the computed transfer map.
        """
        for (i, j, k), transfer_amount in transfer_map.items():
            cell = self.grid[i, j, k]
            if cell and cell.cell_type in {2, 6}:  # Cloud or Air
                cell.water_mass += transfer_amount

    def total_water_mass(self):
        """
        Calculate the total water mass in the grid for debugging purposes.

        Returns:
            float: Total water mass in the grid.
        """
        return sum(
            self.grid[i][j][k].water_mass
            for i in range(self.grid_size[0])
            for j in range(self.grid_size[1])
            for k in range(self.grid_size[2])
            if self.grid[i, j, k] and self.grid[i, j, k].cell_type in {2, 6, 7}
        )
