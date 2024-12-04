import numpy as np
from .Particle import Particle
from config.Config import config_instance 

class World:
    """
    Represents the simulation world, including the grid of particles and associated behaviors.
    """
    def __init__(self, grid_size=None, initial_ratios=None, day_number=0):
        """
        Initialize the World class.

        Args:
            grid_size (tuple): Dimensions of the grid (x, y, z). Defaults to config's Grid Dimensions.
            initial_ratios (dict): Initial ratios for cell types. Defaults to config's initial ratios.
            day_number (int): The current day in the simulation.
        """
        self.config = config_instance.get()  # Access the centralized configuration
        self.grid_size = grid_size or self.config["grid_size"]
        self.grid = np.empty(self.grid_size, dtype=object)

        initial_ratios = initial_ratios or self.config["initial_ratios"]
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

        def _get_dynamic_air_or_cloud_type(k, z):
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

        def _generate_elevation_map():
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

        x, y, z = self.grid_size
        elevation_map = _generate_elevation_map()

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
        baseline_temperature = self.config["baseline_temperature"]
        baseline_pollution_level = self.config["baseline_pollution_level"]

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
                                cell_type = _get_dynamic_air_or_cloud_type(
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
                                cell_type = _get_dynamic_air_or_cloud_type(
                                    k, z)

                        elif surface_type == 'used_land':
                            # Above forests/cities, only air or cloud
                            cell_type = _get_dynamic_air_or_cloud_type(
                                k, z)

                        elif surface_type == 'sky':
                            # Above sky, only air or cloud
                            cell_type = _get_dynamic_air_or_cloud_type(
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
                        dx, dy = np.random.choice([-1, 0, 1]), np.random.choice([-1, 0, 1])
                        dz = 0
                        direction = (dx, dy, dz)

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


    def update_cells_on_grid(self):
        """
        Update all cells in the grid based on their next states and resolve collisions.
        """
        def resolve_collision(cell1, cell2):
            """
            Resolve collisions between two cells with improved handling of interactions.

            Args:
                cell1 (Particle): The first cell involved in the collision.
                cell2 (Particle): The second cell involved in the collision.

            Returns:
                Particle: The resolved cell after the collision.
            """

            if (cell1.cell_type == 6 and cell2.cell_type == 6):
                # return cell1 if (cell1.water_mass + cell1.temperature) > (cell2.water_mass+cell2.temperature) else cell2
                return cell1 if cell1.water_mass >= cell2.water_mass else cell2

            # Prevent vacuum overwrite air or cloud
            if cell1.cell_type == 8 and cell2.cell_type in {2, 6}:
                return cell2
            if cell2.cell_type == 8 and cell1.cell_type in {2, 6}:
                return cell1

            # Handle rain interactions
            if cell1.cell_type == 7 and cell2.cell_type in {6, 8}:  # Cell1 is Rain
                return cell1

            if cell2.cell_type == 7 and cell1.cell_type in {6, 8}:  # Cell2 is Rain
                return cell2

            if cell1.cell_type == 7 and cell2.cell_type == 7:
                return cell1 if cell1.water_mass > cell2.water_mass else cell2
            # Handle rain clouds interactions (Clouds replace air)
            if cell1.cell_type == 6 and cell2.cell_type == 2:  # Cell1 is Rain
                return cell2

            if cell1.cell_type == 2 and cell2.cell_type == 6:  # Cell2 is Rain
                return cell1

            # Default behavior based on cell type weights
            return cell1 if self.config["cell_type_collision_weights"][cell1.cell_type] >= self.config["cell_type_collision_weights"][cell2.cell_type] else cell2

        def get_neighbor_positions(i, j, k):
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

        def accumulate_water_transfers():
            """
            Compute all water transfers for the grid.

            Returns:
                dict: A transfer map with positions as keys and scaled transfer amounts as values.
            """
            transfer_map = {}
            scale_factor = 1e3  # Scale down large transfer amounts if necessary

            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    for k in range(self.grid_size[2]):
                        cell = self.grid[i, j, k]
                        if cell and cell.cell_type != 8:  # Exclude Vacuum
                            neighbors = [
                                self.grid[nx, ny, nz]
                                for nx, ny, nz in get_neighbor_positions(i, j, k)
                            ]
                            cell_transfers = cell.calculate_water_transfer(neighbors)
                            for neighbor_pos, transfer_amount in cell_transfers.items():
                                # Scale transfer amounts if they exceed the scale factor
                                scaled_transfer = transfer_amount / scale_factor if abs(transfer_amount) > scale_factor else transfer_amount
                                transfer_map[neighbor_pos] = transfer_map.get(neighbor_pos, 0) + scaled_transfer

            return transfer_map

        def apply_water_transfers(transfer_map):
            """
            Apply the water transfers to the grid based on the computed transfer map.
            Ensures water_mass stays within reasonable limits to prevent instability.
            """
            max_water_mass = 1.0  # Maximum allowed water mass for a cell (example value)
            min_water_mass = 0.0  # Minimum allowed water mass for a cell

            for (i, j, k), transfer_amount in transfer_map.items():
                cell = self.grid[i, j, k]
                if cell:  # Ensure cell exists
                    cell.water_mass += transfer_amount

                    # Clamp water_mass to stay within defined bounds
                    cell.water_mass = max(min_water_mass, min(cell.water_mass, max_water_mass))

        x, y, z = self.grid_size

        # Phase 1: Compute water transfers
        transfer_map = accumulate_water_transfers()

        # Phase 2: Apply transfers
        apply_water_transfers(transfer_map)
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
                            for nx, ny, nz in get_neighbor_positions(i, j, k)
                            if self.grid[nx, ny, nz] is not None
                        ]
                        updates[(i, j, k)] = cell.compute_next_state(neighbors)

        # Phase 4: Resolve collisions
        position_map = {}
        for (i, j, k), updated_cell in updates.items():
            if updated_cell.cell_type in {0, 3, 1, 4, 5, 8}:
                position_map[i, j, k] = updated_cell
                continue

            next_position = updated_cell.get_next_position()
            if next_position not in position_map:
                position_map[next_position] = updated_cell
            else:
                position_map[next_position] = resolve_collision(
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
    
    def _recalculate_global_attributes(self):
        """
        Recalculate global attributes like average temperature, pollution, water mass,
        and counts of cities and forests. Also calculates averages and standard deviations
        for temperature, pollution, water mass, city count, and forest count.
        """
        total_temperature = 0
        total_pollution = 0
        total_water_mass = 0
        total_cells = 0

        temperature_values = []
        pollution_values = []
        water_mass_values = []
        city_counts = []
        forest_counts = []

        total_cities = 0
        total_forests = 0

        # Iterate over the grid
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                for k in range(self.grid_size[2]):
                    cell = self.grid[i, j, k]
                    if cell is None:
                        continue
                    total_cells += 1
                    total_temperature += cell.temperature
                    total_pollution += cell.pollution_level
                    total_water_mass += cell.water_mass

                    temperature_values.append(cell.temperature)
                    pollution_values.append(cell.pollution_level)
                    water_mass_values.append(cell.water_mass)

                    # Count cities and forests
                    if cell.cell_type == 5:  # City
                        total_cities += 1
                    elif cell.cell_type == 4:  # Forest
                        total_forests += 1

        # Add city and forest counts for standard deviation calculations
        city_counts.append(total_cities)
        forest_counts.append(total_forests)

        # Global averages
        self.avg_temperature = total_temperature / total_cells if total_cells > 0 else 0
        self.avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
        self.avg_water_mass = total_water_mass / total_cells if total_cells > 0 else 0

        # Total counts
        self.total_cities = total_cities
        self.total_forests = total_forests
        self.total_cells = total_cells

        # Standard deviations
        self.std_dev_temperature = np.std(temperature_values) if temperature_values else 0
        self.std_dev_pollution = np.std(pollution_values) if pollution_values else 0
        self.std_dev_water_mass = np.std(water_mass_values) if water_mass_values else 0
        self.std_dev_city_population = np.std(city_counts) if city_counts else 0
        self.std_dev_forest_count = np.std(forest_counts) if forest_counts else 0
