import numpy as np
import logging
from config.config_state_handler import get_config
import math


class Particle:
    """
    Represents a single particle (or cell) in the simulation grid. Each particle has attributes such as type,
    temperature, water mass, pollution level, direction, position, and the grid size.

    This class provides methods for updating particle state, calculating movement, and visualizing the particle.
    """
    config = get_config()  # Configuration dictionary shared across all particles

    def __init__(self, cell_type, temperature, water_mass, pollution_level, direction, position, grid_size):
        """
        Initializes a Particle object with specified attributes.

        Args:
            cell_type (int): Type of the cell (e.g., ocean, cloud, forest, etc.).
            temperature (float): Current temperature of the cell.
            water_mass (float): Amount of water contained in the cell.
            pollution_level (float): Pollution level of the cell.
            direction (tuple): Direction of movement as a 3D vector (dx, dy, dz).
            position (tuple): Current position of the cell in the grid (x, y, z).
            grid_size (tuple): Dimensions of the simulation grid (x_max, y_max, z_max).
        """

        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.position = position  # Particle's current position in the grid
        self.grid_size = grid_size  # Grid boundaries to manage particle movement

    ####################################################################################################################
    ###################################### CLASS UTILS #################################################################
    ####################################################################################################################

    def clone(self):
        """
        Creates a copy of the current particle with identical attributes.

        Returns:
            Particle: A new Particle object with the same state as the current one.
        """
        return Particle(
            cell_type=self.cell_type,
            temperature=self.temperature,
            water_mass=self.water_mass,
            pollution_level=self.pollution_level,
            direction=self.direction,
            position=self.position,
            grid_size=self.grid_size
        )

    def get_next_position(self):
        """
        Calculates the next position of the particle based on its direction and grid size.
        If the particle moves beyond the grid boundaries in the x or y directions, it wraps around (toroidal grid).
        In the z-direction, movement is clamped to remain within the grid's height.

        Returns:
            tuple: The new position of the particle (x, y, z).
        """
        if self.direction == (0, 0, 0):  # Static particles do not move
            return self.position

        x, y, z = self.position
        dx, dy, dz = self.direction

        # Wrap x and y positions (toroidal grid behavior)
        new_x = (x + dx) % self.grid_size[0]
        new_y = (y + dy) % self.grid_size[1]
        # Clamp z position (within grid height)
        new_z = max(0, min(self.grid_size[2] - 1, z + dz))

        return (new_x, new_y, new_z)

    def get_color(self, tint=False):
        """
        Determines the visual representation (RGBA color) of the particle based on its type and pollution level.

        Returns:
            tuple: RGBA color of the particle.
        """
        if not tint:
            return self.get_base_color()
        else:  # If tinting based on pollution is enabled and cell type is not
            return self.get_color_tinted_by_attributes()

    def get_color_tinted_by_attributes(self):
        """
        Applies a subtle black tint based on the pollution level or a red tint based on the temperature
        to the base color of the particle.

        Returns:
            tuple: RGBA color with the respective light tint applied.
        """
        base_color = self.get_base_color()
        if base_color is None or len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {self.cell_type}: {base_color}")
            return (1.0, 1.0, 1.0, 0.0)  # Default to transparent

        # Handle vacuum specifically (no tint effects)
        if self.cell_type == 8:
            return base_color  # Vacuum has no properties that affect tint

        # Get baseline pollution level and temperature
        baseline_pollution_lvl = self.config["baseline_pollution_level"][self.cell_type]
        baseline_temperature = self.config["baseline_temperature"][self.cell_type]

        # Calculate pollution and temperature intensity
        pollution_intensity = 0.0
        if baseline_pollution_lvl > 0:
            pollution_intensity = min(
                self.pollution_level / baseline_pollution_lvl, 0.5
            )  # Cap at 0.5 for lighter tints

        temperature_intensity = 0.0
        if baseline_temperature != 0:
            temperature_difference = abs(self.temperature - baseline_temperature)
            temperature_intensity = min(
                temperature_difference / abs(baseline_temperature), 0.5
            )  # Cap at 0.5 for lighter tints

        # Apply black tint based on pollution intensity
        black_tinted_color = [
            base_color[0] * (1.0 - pollution_intensity * 0.5),  # Slightly reduce red
            base_color[1] * (1.0 - pollution_intensity * 0.5),  # Slightly reduce green
            base_color[2] * (1.0 - pollution_intensity * 0.5),  # Slightly reduce blue
        ]

        # Apply red tint based on temperature intensity
        red_tinted_color = [
            min(1.0, base_color[0] + temperature_intensity * 0.5),  # Slightly increase red
            base_color[1] * (1.0 - temperature_intensity * 0.5),    # Slightly reduce green
            base_color[2] * (1.0 - temperature_intensity * 0.5),    # Slightly reduce blue
        ]

        # Determine which effect dominates and blend tints
        blended_color = [
            (black_tinted_color[i] + red_tinted_color[i]) / 2.0
            for i in range(3)
        ]

        # Preserve the alpha (transparency) channel from the base color
        alpha = max(0.0, min(base_color[3], 1.0))

        return (*blended_color, alpha)


    def get_base_color(self):
        """
        Retrieves the base color for the particle based on its type.

        Returns:
            tuple: RGBA base color of the particle.
        """
        base_color = self.config["base_colors"].get(self.cell_type)
        if base_color is None:
            logging.error(f"Base color for cell_type {
                          self.cell_type} is not defined.")
        # Default to white color if the cell type is undefined
        return base_color if base_color[3] != 0.0 else (1.0, 1.0, 1.0, 0.0)

    def calculate_water_transfer(self, neighbors):
        """
        Calculate the water transfer between the current cell and its neighbors.

        Returns a dictionary mapping the positions of neighboring cells to the amount of water transferred.
        """
        transfer_map = {}
        for neighbor in neighbors:
            if neighbor.cell_type in self.config["cell_type_water_transfer_weights"]:
                diff = neighbor.water_mass - self.water_mass
                transfer_weight = self.config["cell_type_water_transfer_weights"][neighbor.cell_type]

                if abs(diff) > self.config["water_transfer_threshold"]:
                    # Compute weighted transfer amount
                    transfer_amount = diff * transfer_weight * self.config["water_transfer_rate"]
                    transfer_map[neighbor.position] = transfer_amount

        return transfer_map

    ####################################################################################################################
    ###################################### CELL UPDATES: ###############################################################
    ####################################################################################################################

    ####################################################################################################################
    ###################################### CELL UPDATES: ###############################################################
    ####################################################################################################################

    def compute_next_state(self, neighbors):
        """
        Computes the next state of the particle based on its type and interactions with neighboring particles.

        Steps:
        - Creates a clone of the current particle to determine the new state.
        - Applies natural decay to pollution and temperature.
        - Equilibrates temperature and pollution levels with neighbors.
        - Executes specific behavior logic for the particle's type.

        Args:
            neighbors (list): List of neighboring particles.

        Returns:
            Particle: The updated particle after applying its next state.
        """

        new_cell = self.clone()
        if new_cell.is_vacuum_cell():
            return new_cell

        # Apply natural decay processes
        neighbors = [n for n in neighbors if not n.is_vacuum_cell()]
        new_cell._apply_natural_decay(neighbors)
        new_cell.equilibrate_temperature(neighbors)
        new_cell.equilibrate_pollution_level(neighbors)

        # Execute specific behavior based on the particle's type
        if self.cell_type == 0:  # Ocean
            new_cell._update_ocean(neighbors)
        elif self.cell_type == 1:  # Desert
            new_cell._update_desert(neighbors)
        elif self.cell_type == 2:  # Cloud
            new_cell._update_cloud(neighbors)
        elif self.cell_type == 3:  # Ice
            new_cell._update_ice(neighbors)
        elif self.cell_type == 4:  # Forest
            new_cell._update_forest(neighbors)
        elif self.cell_type == 5:  # City
            new_cell._update_city(neighbors)
        elif self.cell_type == 6:  # Air
            new_cell._update_air(neighbors)
        elif self.cell_type == 7:  # Rain
            new_cell._update_rain(neighbors)

        return new_cell

    def _update_ocean(self, neighbors):
        """

        Updates the behavior of ocean cells.
        Ocean cells can evaporate into air, freeze into ice, or remain stable.

        Args:
            neighbors (list): List of neighboring particles.
        """
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        # Ocean cells tend to move downward (e.g., gravity)
        self.go_down(neighbors)
        if self.temperature > self.config["evaporation_point"] - 5:
            evaporation_rate = self.config["evaporation_rate"]
            self.water_mass -= evaporation_rate  # Water evaporates
            if self.water_mass <= 0:  # Convert to air if water is fully evaporated
                self.absorb_water_mass(
                    neighbors)  # Share water with neighboring cells
                self.convert_to_air(neighbors)

        # Freeze into ice
        elif self.temperature < self.config["freezing_point"] - 1 and not self.is_surrounded_by_land_cells(neighbors_above) and not self.is_surrounded_by_land_cells(neighbors_aligned) and (self.is_surrounded_by_sea_cells(neighbors_below+neighbors_aligned) or self.is_surrounded_by_sea_cells(neighbors_above)):
            self.convert_to_ice()

    def _update_desert(self, neighbors):
        """
        Updates the behavior of desert cells.
        Deserts may convert into oceans if surrounded by water or into forests if conditions permit.

        Args:
            neighbors (list): List of neighboring particles.
        """
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        pollution_damage_threshold = self.config["pollution_damage_threshold"]
        forest_baseline_temperature = self.config["baseline_temperature"][4]
        # Water mass required to convert a cell to ocean
        ocean_conversion_threshold = self.config["ocean_conversion_threshold"]

        if self.water_mass > ocean_conversion_threshold and (self.is_surrounded_by_sea_cells(neighbors_aligned) or self.is_surrounded_by_sea_cells(neighbors_below)):
            self.convert_to_ocean(neighbors)
        # Surrounded by water
        if self.is_surrounded_by_sea_cells(neighbors_above):
            self.convert_to_ocean(neighbors)
        elif (
            self.is_surrounded_by_land_cells(neighbors_aligned)
            and self.pollution_level <= pollution_damage_threshold
            and forest_baseline_temperature - 10 <= self.temperature <= forest_baseline_temperature + 10
            and (self.is_surrounded_by_desert_cells(neighbors_aligned) or self.is_surrounded_by_forests_cells(neighbors_aligned))
            and not (self.is_surrounded_by_city_cells(neighbors_below) or self.is_surrounded_by_forests_cells(neighbors_below) or self.is_surrounded_by_sea_cells(neighbors_above))
        ):  # Suitable for forest conversion
            self.convert_to_forest(neighbors)

    def _update_cloud(self, neighbors):
        """
        Updates the behavior of cloud cells.
        Clouds exchange water mass with neighbors and may convert to rain if saturated.

        Args:
            neighbors (list): List of neighboring particles.
        """
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        self.absorb_water_mass(
            neighbors)  # Share water with neighboring cells
        saturation_threshold = self.config["cloud_saturation_threshold"]
        if (self.is_surrounded_by_land_cells(neighbors_below) or self.is_surrounded_by_sea_cells(neighbors_below)) and (self.is_surrounded_by_land_cells(neighbors_aligned) or self.is_surrounded_by_sea_cells(neighbors_aligned)):
            self.go_up(neighbors)
        elif self.water_mass >= saturation_threshold:  # Convert to rain if saturated
            self.convert_to_rain(neighbors)
        else:
            self.direction = self.calculate_dynamic_wind_direction(neighbors)

    def _update_ice(self, neighbors):
        """
        Updates the behavior of ice cells.
        Ice can melt into water or stabilize depending on temperature.

        Args:
            neighbors (list): List of neighboring particles.
        """
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        melting_rate = self.config["melting_rate"]
        # Melting conditions
        if self.temperature > self.config["melting_point"] - 5:
            self.water_mass -= melting_rate
            # Convert to ocean when melted
            if self.water_mass <= 0 and (self.is_surrounded_by_sea_cells(neighbors_aligned) or self.is_below_sea_level(neighbors_above) or self.is_surrounded_by_sea_cells(neighbors_below)):
                self.convert_to_ocean(neighbors)
        elif self.is_surrounded_by_land_cells(neighbors_aligned) or self.is_surrounded_by_land_cells(neighbors_above):
            self.convert_to_desert(neighbors)

    def _update_forest(self, neighbors):
        """
        Updates the behavior of forest cells.
        Forests absorb pollution, cool down the environment, or may degrade into other types.

        Args:
            neighbors (list): List of neighboring particles.
        """
        absorption_rate = self.config["forest_pollution_absorption_rate"]
        cooling_effect = self.config["forest_cooling_effect"]
        forest_pollution_extinction_point = self.config["forest_pollution_extinction_point"]
        forest_temperature_extinction_point = self.config["forest_temperature_extinction_point"]
        forest_baseline_temperature = self.config["baseline_temperature"][self.cell_type]
        pollution_damage_threshold = self.config["pollution_damage_threshold"]
        pollution_level_tipping_point = self.config["pollution_level_tipping_point"]
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        neighbors_below= self.get_below_neighbors(neighbors)

        if self.pollution_level > pollution_level_tipping_point:
            absorption_rate *= 0.5  # Reduced absorption under high pollution
            cooling_effect *= 0.5  # Reduced cooling effect under high pollution

        self.pollution_level = max(
            0, self.pollution_level - absorption_rate * self.pollution_level)
        self.temperature -= self.temperature * cooling_effect

        # Surrounded by water
        if self.is_surrounded_by_sea_cells(neighbors_above + neighbors_aligned):
            self.convert_to_ocean(neighbors)
        elif (self.temperature >= forest_temperature_extinction_point or self.pollution_level >= forest_pollution_extinction_point) and self.is_surrounded_by_land_cells(neighbors_above):  # Forest destruction
            self.convert_to_desert(neighbors)
        elif (
            self.pollution_level < pollution_damage_threshold
            and int(self.temperature) == int(forest_baseline_temperature)
            and (self.is_surrounded_by_desert_cells(neighbors_aligned) or self.is_surrounded_by_city_cells(neighbors_aligned))
            and not (self.is_surrounded_by_city_cells(neighbors_below) or self.is_surrounded_by_forests_cells(neighbors_below) or self.is_surrounded_by_sea_cells(neighbors_below))
        ):  # Convert to a city
            self.convert_to_city(neighbors)

    def _update_city(self, neighbors):
        """
        Updates the behavior of city cells.
        Cities increase pollution and temperature and may degrade into deserts or oceans.

        Args:
            neighbors (list): List of neighboring particles.
        """
        pollution_increase_rate = self.config["city_pollution_generation_rate"]
        warming_effect = self.config["city_warming_effect"]
        baseline_pollution_level = self.config["baseline_pollution_level"][self.cell_type]
        baseline_temperature = self.config["baseline_temperature"][self.cell_type]
        city_pollution_extinction_point = self.config["city_pollution_extinction_point"]
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_below = self.get_below_neighbors(neighbors)

        # Update temperature and pollution level
        self.temperature = min(
            city_pollution_extinction_point,
            max(baseline_temperature, self.temperature +
                warming_effect * self.temperature),
        )
        self.pollution_level = min(
            city_pollution_extinction_point,
            max(
                baseline_pollution_level,
                self.pollution_level + pollution_increase_rate * self.pollution_level,
            ),
        )

        # Check for conversions based on conditions
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        # Surrounded by water
        if self.is_surrounded_by_sea_cells(neighbors_above) or self.is_surrounded_by_sea_cells(neighbors_below) or self.is_surrounded_by_sea_cells(neighbors_aligned):
            self.convert_to_ocean(neighbors)
        # Excessive pollution or temperature
        elif (self.pollution_level >= city_pollution_extinction_point or self.temperature >= abs(city_pollution_extinction_point)) or self.is_surrounded_by_sea_cells(neighbors_above+neighbors_aligned):
            self.convert_to_desert(neighbors)

    def _update_air(self, neighbors):
        """
        Updates the behavior of air cells.

        Air cells can:
        - Exchange water mass with neighboring cells.
        - Rise or fall based on their position and surrounding rain particles.
        - Convert into clouds if saturated and at appropriate elevation.
        - Convert into vacuum if surrounded by land cells and rain is above.

        Args:
            neighbors (list): List of neighboring particles.
        """
        # Get rain-related neighbors to influence air behavior
        rain_above = self.get_above_neighbors(
            [n for n in neighbors if n.cell_type == 7])  # Rain particles above
        rain_below = self.get_below_neighbors(
            [n for n in neighbors if n.cell_type == 7])  # Rain particles below
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_align = self.get_below_neighbors(neighbors)

        # Exchange water mass with neighbors (e.g., clouds or other air partic  les)
        self.absorb_water_mass(neighbors)

        # Convert to cloud if the water mass exceeds the saturation threshold
        # and the particle is at or near the top of the grid.
        if self.water_mass >= self.config["cloud_saturation_threshold"] and self.is_surrounded_by_cloud_cells(neighbors_below) and self.position[2] >= self.grid_size[2] // 2:
            self.convert_to_cloud(neighbors)
            self.go_up(neighbors)
        # If rain is above, move downward to support convection and interaction.
        elif rain_above:
            self.go_down(neighbors)

        # Move upward if the particle is near the ground, has rain below, or is below sea/ground level.
        elif (
            self.position[2] <= 2
            or rain_below
            or self.is_below_ground_level(neighbors)
            or self.is_below_sea_level(neighbors)
        ):
            self.go_up(neighbors)
        else:
            self.direction = self.calculate_dynamic_wind_direction(neighbors)

    def _update_rain(self, neighbors):
        """
        Updates the behavior of rain cells.

        Rain cells fall downward until reaching the ground level. At ground level:
        - They convert to oceans if surrounded by sea cells.
        - They evaporate and convert back to air if surrounded by land cells.

        Args:
            neighbors (list): List of neighboring particles.
        """
        # Move rain particles downward to simulate precipitation
        # Check if the particle has reached the ground level
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_align = self.get_below_neighbors(neighbors)
        neighbors_above = self.get_below_neighbors(neighbors)

        if self.position[2] > 0:
            self.go_down(neighbors)
            self.direction = (0, 0, -1)

        elif self.is_surrounded_by_sea_cells(neighbors_below) or self.is_surrounded_by_sea_cells(neighbors_align) or self.is_surrounded_by_sea_cells(neighbors_above):
            self.convert_to_ocean(neighbors)
            # Convert to air (dry up) if surrounded by land cells
        elif self.is_surrounded_by_land_cells(neighbors_below) or self.is_surrounded_by_land_cells(neighbors_align) or self.is_surrounded_by_land_cells(neighbors_above):
            self.convert_to_air(neighbors)

    ####################################################################################################################
    ###################################### CELL CONVERSIONS ###########################################################
    ####################################################################################################################

    def convert_to_ocean(self, neighbors):
        """
        Converts the current cell to an ocean cell.
        Updates water mass, temperature, and stabilizes elevation.

        Ocean cells:
        - Always have full water mass (1.0).
        - Have a baseline temperature defined in the configuration.
        """
        self.cell_type = 0  # Set cell type to ocean
        self.water_mass = 1.0  # Oceans are full of water by default
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize(neighbors)  # Stabilize motion

    def convert_to_desert(self, neighbors):
        """
        Converts the current cell to a desert cell.
        Updates water mass and temperature, and stabilizes motion.

        Desert cells:
        - Have no water mass (0.0).
        - Have a baseline temperature defined in the configuration.
        """
        self.cell_type = 1  # Set cell type to desert
        self.water_mass = 0.0  # Deserts have no water by default
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize(neighbors)  # Stabilize motion

    def convert_to_cloud(self, neighbors):
        """
        Converts the current cell to a cloud cell.
        Updates water mass, decreases temperature, and moves the cell upward.

        Cloud cells:
        - Form by condensation, which increases water mass.
        - Typically cool down during formation.
        """
        self.cell_type = 2  # Set cell type to cloud
        # Condensation increases water mass
        self.water_mass = min(1.0, self.water_mass + 0.5)
        self.temperature -= 2  # Clouds typically cool down during formation
        self.go_up(neighbors)  # Clouds move upward

    def convert_to_ice(self, neighbors):
        """
        Converts the current cell to an ice cell.
        Updates water mass, temperature, and stabilizes motion.

        Ice cells:
        - Retain full water mass (1.0).
        - Have a freezing temperature defined in the configuration.
        """
        self.cell_type = 3  # Set cell type to ice
        self.water_mass = 1.0  # Ice retains full water mass
        # Set to freezing temperature
        self.temperature = self.config["freezing_point"]
        self.stabilize(neighbors)  # Stabilize motion

    def convert_to_forest(self, neighbors):
        """
        Converts the current cell to a forest cell.
        Updates water mass and temperature, and stabilizes motion.

        Forest cells:
        - Do not retain water mass (0.0).
        - Have a baseline temperature defined in the configuration.
        """
        self.cell_type = 4  # Set cell type to forest
        self.water_mass = 0.0  # Forest cells don't retain water mass
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize(neighbors)  # Stabilize motion

    def convert_to_city(self, neighbors):
        """
        Converts the current cell to a city cell.
        Updates water mass, pollution level, temperature, and stabilizes motion.

        City cells:
        - Do not retain water mass (0.0).
        - Start with a baseline pollution level defined in the configuration.
        - Have a baseline temperature defined in the configuration.
        """
        self.cell_type = 5  # Set cell type to city
        self.water_mass = 0.0  # Cities don't retain water mass
        # Set baseline pollution
        self.pollution_level = self.config["baseline_pollution_level"][self.cell_type]
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize(neighbors)  # Stabilize motion

    def convert_to_air(self, neighbors):
        """
        Converts the current cell to an air cell.
        Updates water mass, increases temperature, and moves the cell upward.

        Air cells:
        - Form by evaporation, which reduces water mass.
        - Warm up during evaporation.
        """
        self.cell_type = 6  # Set cell type to air
        # Evaporation reduces water mass
        self.water_mass = max(0.0, self.water_mass - 0.5)
        self.temperature += 2  # Air warms during evaporation
        self.go_up(neighbors)  # Air moves upward

    def convert_to_vacuum(self, neighbors):
        """
        Converts the current cell to a vacuum cell.
        Clears water mass, pollution level, and stabilizes motion.

        Vacuum cells:
        - Have no water mass or pollution.
        - Do not move.
        """
        self.cell_type = 8  # Set cell type to vacuum
        self.water_mass = 0  # No water in vacuum
        self.pollution_level = 0  # No pollution in vacuum
        self.direction = (0, 0, 0)  # No movement
        self.temperature = math.avg([n.temperature for n in neighbors])

    def convert_to_rain(self, neighbors):
        """
        Converts the current cell to a rain cell.
        Updates water mass, decreases temperature, and sets movement downward.

        Rain cells:
        - Have full water mass (1.0).
        - Cool down during formation.
        - Always move downward.
        """
        self.cell_type = 7  # Set cell type to rain
        self.water_mass = 1.0  # Rain has full water mass
        self.temperature -= 1  # Rain cools during formation
        self.direction = (0, 0, -1)  # Move downward
        self.go_down(neighbors)  # Air moves upward

    ####################################################################################################################
    ############################################### CELL EQUILIBRATE ###################################################
    ####################################################################################################################

    def _apply_natural_decay(self, neighbors):
        """
        Apply natural decay to pollution level and temperature.

        Natural decay ensures that:
        - Pollution levels gradually decrease over time based on a decay rate.
        - Temperature stabilizes toward a baseline value defined in the configuration.
        - Pollution and temperature are influenced by neighboring cells but only affect this cell.

        Args:
            neighbors (list of Particle): Neighboring particles around the current cell.
        """
        pollution_decay_rate = self.config["natural_pollution_decay_rate"]
        temperature_decay_rate = self.config["natural_temperature_decay_rate"]
        pollution_diffusion_rate = self.config.get("pollution_diffusion_rate", 0.1)
        temperature_diffusion_rate = self.config.get("temperature_diffusion_rate", 0.1)
        transfer_weights = self.config.get("cell_type_pollution_transfer_weights", {})

        # Step 1: Apply natural decay for pollution and temperature
        self.pollution_level = max(
            0,
            self.pollution_level - (self.pollution_level * pollution_decay_rate)
        )

        baseline_temp = self.config["baseline_temperature"][self.cell_type]
        if self.temperature > baseline_temp:
            self.temperature -= (self.temperature - baseline_temp) * temperature_decay_rate
        elif self.temperature < baseline_temp:
            self.temperature += (baseline_temp - self.temperature) * temperature_decay_rate

        # Step 2: Influence from neighboring cells
        weighted_pollution_influence = 0
        weighted_temperature_influence = 0
        total_pollution_weight = 0
        total_temperature_weight = 0

        for neighbor in neighbors:
            # Skip invalid neighbors (e.g., boundaries or non-polluting cell types)
            if neighbor is None or neighbor.cell_type not in transfer_weights:
                continue

            # Get the pollution transfer weight for the neighbor's cell type
            pollution_weight = transfer_weights[neighbor.cell_type]
            total_pollution_weight += pollution_weight

            # Calculate weighted pollution influence
            pollution_difference = neighbor.pollution_level - self.pollution_level
            weighted_pollution_influence += pollution_difference * pollution_diffusion_rate * pollution_weight

            # Calculate temperature influence (equal influence for all valid neighbors)
            temperature_difference = neighbor.temperature - self.temperature
            temperature_weight = 1  # Assuming equal weighting for temperature influence
            total_temperature_weight += temperature_weight
            weighted_temperature_influence += temperature_difference * temperature_diffusion_rate * temperature_weight

        # Step 3: Apply the averaged influence from neighbors
        if total_pollution_weight > 0:
            self.pollution_level += weighted_pollution_influence / total_pollution_weight

        if total_temperature_weight > 0:
            self.temperature += weighted_temperature_influence / total_temperature_weight

        # Step 4: Ensure pollution and temperature levels remain within valid bounds
        self.pollution_level = max(0, self.pollution_level)
        self.temperature = max(
            baseline_temp - 100,  # Arbitrary lower bound
            min(self.temperature, baseline_temp + 100)  # Arbitrary upper bound
        )

    def equilibrate_temperature(self, neighbors):
        """
        Equilibrates the cell's temperature based on its neighbors' weighted temperatures.

        The new temperature is computed as the weighted average of the neighbors' temperatures,
        with weights defined in the configuration for each cell type.
        """
        total_weight = 0
        weighted_temperature_sum = 0

        for neighbor in neighbors:
            weighted_temperature_sum += neighbor.temperature * \
                self.config["cell_type_temperature_transfer_weights"][neighbor.cell_type]
            total_weight += self.config["cell_type_temperature_transfer_weights"][neighbor.cell_type]

        # Calculate weighted average temperature
        if total_weight > 0:
            self.temperature = (weighted_temperature_sum /
                                total_weight + self.temperature) / 2

    def equilibrate_pollution_level(self, neighbors):
        """
        Equilibrates the cell's pollution level based on its neighbors' weighted pollution levels.

        The new pollution level is computed as the weighted average of the neighbors' pollution levels,
        with weights defined in the configuration for each cell type.
        """
        total_weight = 0
        weighted_pollution_sum = 0

        for neighbor in neighbors:
            weighted_pollution_sum += neighbor.pollution_level * \
                self.config["cell_type_pollution_transfer_weights"][neighbor.cell_type]
            total_weight += self.config["cell_type_pollution_transfer_weights"][neighbor.cell_type]

        # Calculate weighted average pollution level
        if total_weight > 0:
            self.pollution_level = (
                weighted_pollution_sum / total_weight + self.pollution_level) / 2

    def absorb_water_mass(self, neighbors):
        """
        Exchange water mass with neighboring cells based on water transfer weights.

        Water mass is exchanged based on the difference between the current cell's water mass
        and the neighbor's water mass, adjusted by a weight factor and a threshold.
        """
        total_transfer = 0
        for neighbor in neighbors:
            if neighbor.cell_type in self.config["cell_type_water_transfer_weights"]:
                diff = neighbor.water_mass - self.water_mass
                transfer_weight = self.config["cell_type_water_transfer_weights"][neighbor.cell_type]

                if abs(diff) > self.config["water_transfer_threshold"]:
                    # Compute weighted water transfer
                    water_transfer = diff * transfer_weight * self.config["water_transfer_rate"]

                    # Adjust the current cell's water mass
                    self.water_mass += water_transfer
                    total_transfer += abs(water_transfer)

        return total_transfer

    ####################################################################################################################
    ###################################### CELL ELEVATION ##############################################################
    ####################################################################################################################

    def calculate_dynamic_wind_direction(self, neighbors):
        """
        Calculate the dominant wind direction based on neighbors' attributes,
        including water mass, temperature, and pressure gradients.

        Args:
            neighbors (list of Particle): Neighboring particles around the current cell.

        Returns:
            tuple: A direction vector (dx, dy, dz) indicating the dominant wind direction.
        """
        # Initialize accumulators for directional influence and total weight
        weighted_dx, weighted_dy, weighted_dz = 0, 0, 0
        total_influence = 0

        for neighbor in neighbors:
            # Skip non-fluid-like cell types (e.g., solid types)
            if neighbor.cell_type not in {2, 6, 7}:  # Cloud, Air, Rain
                continue

            # Calculate influence factors
            temperature_influence = max(
                neighbor.temperature - self.temperature, 0) / 10.0
            water_mass_influence = neighbor.water_mass
            # Simulates air pressure difference
            altitude_influence = max(
                self.position[2] - neighbor.position[2], 0) / 100.0

            # Total influence combines these factors
            influence = water_mass_influence + temperature_influence + altitude_influence

            # Get the neighbor's directional vector
            dx, dy, dz = neighbor.direction

            # Accumulate weighted contributions
            weighted_dx += dx * influence
            weighted_dy += dy * influence
            weighted_dz += dz * influence
            total_influence += influence

        # Normalize the wind direction if total influence is significant
        if total_influence > 0:
            normalized_dx = weighted_dx / total_influence
            normalized_dy = weighted_dy / total_influence
            normalized_dz = weighted_dz / total_influence
        else:
            # No significant influence; return no wind direction
            return (0, 0, 0)

        # Determine dominant wind direction by rounding to nearest integer (for discrete directions)
        dominant_dx = round(normalized_dx)
        dominant_dy = round(normalized_dy)
        dominant_dz = round(normalized_dz)

        # Return the dominant wind direction as a discrete vector
        return (dominant_dx, dominant_dy, dominant_dz)

    def go_down(self, neighbors):
        """
        Move the particle downward.

        Ensures that the particle doesn't move below the ground level (z = 0).
        """
        if self.position[2] >= 0:  # Ensure it doesn't go below the ground
            dx, dy, dz = self.calculate_dynamic_wind_direction(neighbors)
            self.direction = (dx, dy, -1)

    def go_up(self, neighbors):
        """
        Move the particle upward.

        Ensures that the particle doesn't move above the grid's maximum height.
        """

        if self.position[2] < self.grid_size[2]:
            dx, dy, _ = self.calculate_dynamic_wind_direction(neighbors)
            self.direction = (dx, dy, 1)

    def stabilize(self, neighbors):
        """
        Stabilize the particle, halting its movement.

        Sets the direction to (0, 0, 0) to indicate no movement.
        """
        self.direction = (0, 0, 0)

    ####################################################################################################################
    ###################################### SURROUNDINGS: ###############################################################
    ####################################################################################################################

    def is_surrounded_by_sea_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by sea or ice cells.

        Returns True if the majority of neighbors are of type Sea (0) or Ice (3).
        """
        return sum(n.cell_type in {0, 3} for n in neighbors) > len(neighbors) / 2

    def is_surrounded_by_land_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by land cells.

        Returns True if all neighbors are of type Desert (1), Forest (4), City (5), Air (6), or Vacuum (8).
        """
        return sum(n.cell_type in {1, 4, 5} for n in neighbors) == len(neighbors)

    def is_surrounded_by_desert_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by land cells.

        Returns True if all neighbors are of type Desert (1), Forest (4), City (5), Air (6), or Vacuum (8).
        """
        return sum(n.cell_type in {1} for n in neighbors) == len(neighbors)
    
    def is_surrounded_by_forests_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by land cells.

        Returns True if all neighbors are of type Desert (1), Forest (4), City (5), Air (6), or Vacuum (8).
        """
        return sum(n.cell_type in {4} for n in neighbors) == len(neighbors)

    def is_surrounded_by_city_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by land cells.

        Returns True if all neighbors are of type Desert (1), Forest (4), City (5), Air (6), or Vacuum (8).
        """
        return sum(n.cell_type in {5} for n in neighbors) == len(neighbors)



    def is_surrounded_by_cloud_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by land cells.

        Returns True if all neighbors are of type Desert (1), Forest (4), City (5), Air (6), or Vacuum (8).
        """
        return sum(n.cell_type in {2} for n in neighbors) == len(neighbors)

    def is_surrounded_by_air_cells(self, neighbors):
        return sum(n.cell_type in {6} for n in neighbors) == len(neighbors)

    def is_below_sea_level(self, neighbors):
        """
        Check if the cell is below sea level.

        Returns True if the cell's elevation is lower than all sea-level neighbors.
        """
        return all(self.position[2] < n.position[2] for n in neighbors if n.cell_type in {0, 3})

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.

        Returns True if the cell's elevation is lower than all ground-level neighbors.
        """
        return all(self.position[2] < n.position[2] for n in neighbors if n.cell_type in {1, 4, 5})

    def get_above_neighbors(self, neighbors):
        """
        Get all neighbors that are above the current cell in elevation.
        """
        return [n for n in neighbors if n.position[2] > self.position[2]]

    def get_below_neighbors(self, neighbors):
        """
        Get all neighbors that are below the current cell in elevation.
        """
        return [n for n in neighbors if n.position[2] < self.position[2]]

    def get_aligned_neighbors(self, neighbors):
        """
        Get all neighbors that are at the same elevation as the current cell.
        """
        return [n for n in neighbors if n.position[2] == self.position[2]]

    def is_vacuum_cell(self):
        return self.cell_type == 8
