import numpy as np
import logging


class Cell:
    def __init__(self, cell_type=6, temperature=0, water_mass=0, pollution_level=0, direction=(0, 0), elevation=None):
        """
        Initialize a Cell object.
        :param cell_type: Integer representing the cell type.
        :param temperature: Initial temperature of the cell.
        :param water_mass: Initial water mass of the cell.
        :param pollution_level: Initial pollution level of the cell.
        :param direction: Tuple indicating the cell's movement direction.
        :param elevation: Elevation of the cell (used for terrain cells).
        """
        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.elevation = elevation  # Optional attribute for terrain-related logic

    def clone(self):
        return Cell(
            cell_type=self.cell_type,
            temperature=self.temperature,
            water_mass=self.water_mass,
            pollution_level=self.pollution_level,
            direction=self.direction,
            elevation=self.elevation,
        )


    def get_next_state(self, neighbors, current_position=None, grid_size=None):
        """
        Compute the next state of the cell based on its neighbors and position.
        """
        next_cell = self.clone()
        next_cell._adjust_temperature_with_pollution()

        # Call the appropriate update method based on cell type
        if self.cell_type == 0:  # Sea
            next_cell._update_sea(neighbors)
        elif self.cell_type == 1:  # Land
            next_cell._update_land(neighbors)
        elif self.cell_type == 2:  # Cloud
            next_cell._update_cloud(neighbors, current_position, grid_size)
        elif self.cell_type == 3:  # Ice
            next_cell._update_ice(neighbors)
        elif self.cell_type == 4:  # Forest
            next_cell._update_forest(neighbors)
        elif self.cell_type == 5:  # City
            next_cell._update_city(neighbors)
        elif self.cell_type == 6:  # Air
            next_cell._update_air(neighbors)

        return next_cell

    def _apply_natural_decay(self):
        """Apply natural decay to pollution and temperature levels."""
        pollution_decay_rate = 0.01
        temperature_decay_rate = 0.005
        baseline_temperature = 15

        self.pollution_level = max(0, self.pollution_level - self.pollution_level * pollution_decay_rate)
        if self.temperature > baseline_temperature:
            self.temperature -= (self.temperature - baseline_temperature) * temperature_decay_rate
        elif self.temperature < baseline_temperature:
            self.temperature += (baseline_temperature - self.temperature) * temperature_decay_rate

    def _adjust_temperature_with_pollution(self):
        """
        Adjust the temperature based on pollution level.
        Higher pollution levels cause more noticeable temperature increases.
        """
        pollution_effect = self.pollution_level * 0.1  # Increased scaling factor
        max_effect = 20  # Higher maximum effect to reflect significant pollution impact
        self.temperature += min(pollution_effect, max_effect)

        # Stronger effect for very high pollution levels
        if self.pollution_level > 50:
            extra_effect = (self.pollution_level - 50) * 0.2  # Additional temperature increase
            self.temperature += min(extra_effect, 10)  # Limit extra effect to 10 degrees

        # Apply natural cooling if pollution is very low
        if self.pollution_level < 10:
            self.temperature = max(0, self.temperature - 0.1)



    def elevate_and_update(self, elevation_limit):
        """
        Update the cell state based on its elevation.
        Convert water to clouds if elevation is beyond the threshold.
        """
        if self.cell_type == 0 and self.elevation is not None and self.elevation >= elevation_limit:
            # Convert water to cloud
            self.cell_type = 2  # Cloud
            self.pollution_level = 0  # Reset pollution
            self.water_mass = 0.2  # Initial water mass for cloud
            logging.debug(f"Water at elevation {self.elevation} converted to Cloud.")


    def _apply_natural_decay(self):
        """
        Apply natural decay to temperature and pollution levels.
        """
        pollution_decay_rate = 0.01  # Rate at which pollution naturally decreases
        temperature_decay_rate = 0.005  # Rate at which temperature naturally decreases

        # Apply decay to pollution level
        self.pollution_level = max(
            0, self.pollution_level - (self.pollution_level * pollution_decay_rate))

        # Apply decay to temperature, reducing towards a baseline temperature
        baseline_temperature = 15  # Assume a global baseline temperature
        if self.temperature > baseline_temperature:
            self.temperature -= (self.temperature -
                                 baseline_temperature) * temperature_decay_rate
        elif self.temperature < baseline_temperature:
            self.temperature += (baseline_temperature -
                                 self.temperature) * temperature_decay_rate

    def convert_to_city(self):
        if self.cell_type == 4:
            self.cell_type = 5
            self.pollution_level = 10
            self.water_mass = 0
            self.temperature += 2

    def convert_to_land(self):
        if self.cell_type in [4, 5]:
            self.cell_type = 1
            self.pollution_level = 0
            self.water_mass = 0
            self.temperature -= 1

    def _update_forest(self, neighbors):
        self.pollution_level = max(
            0, self.pollution_level - 0.02 * self.pollution_level)
        cooling_effect = self.pollution_level * 0.02
        self.temperature -= cooling_effect

        for neighbor in neighbors:
            if neighbor.pollution_level > 0:
                absorbed_pollution = min(0.1, neighbor.pollution_level * 0.1)
                neighbor.pollution_level -= absorbed_pollution
                self.pollution_level += absorbed_pollution

            if neighbor.cell_type == 2 and neighbor.water_mass > 0:
                rain = min(0.1, neighbor.water_mass)
                self.water_mass += rain
                neighbor.water_mass -= rain

        if (self.pollution_level > 100 or (self.temperature > 50 or self.temperature <= 0)) and np.random.random() < 0.2:
            self.convert_to_land()
        elif self.pollution_level == 0 and self.temperature <= 25 and np.random.random() < 0.2:
            self.convert_to_city()

    def _update_land(self, neighbors):
        surrounding_sea_count = sum(
            1 for neighbor in neighbors if neighbor.cell_type == 0)
        if surrounding_sea_count > len(neighbors) * 0.6 and self.water_mass > 1.0:
            self.cell_type = 0
            self.water_mass = 1.0
            self.pollution_level = 0
            return

        if self.pollution_level == 0 and self.temperature in range(25):
            recovery_chance = 0.1
            if np.random.random() < recovery_chance:
                self.cell_type = 4
                self.pollution_level = 0

    def _update_city(self, neighbors):
        self.pollution_level += 0.02 * self.pollution_level
        self.temperature += 0.02 * self.temperature

        for neighbor in neighbors:
            pollution_spread = 0.1 * self.pollution_level
            neighbor.pollution_level += pollution_spread

        if self.temperature > 60 or self.temperature <= 0 or self.pollution_level > 100:
            self.convert_to_land()

    def _update_ice(self, neighbors):
        """
        Update the properties of an Ice cell.
        Handles melting and cooling of neighboring cells.
        """
        freezing_point = 0  # Temperature threshold for melting ice

        if self.temperature > freezing_point:
            self.cell_type = 0  # Convert Ice to Sea (Water)
            water_increase = 1.0  # Amount of water added when ice melts
            self.water_mass += water_increase
            logging.debug(f"Ice melted into Water: {self}")

            # Spread water level increase to neighboring Sea cells
            for neighbor in neighbors:
                if neighbor.cell_type == 0:  # Neighbor is Sea
                    water_share = water_increase / len(neighbors)
                    neighbor.water_mass += water_share
                    self.water_mass -= water_share

        # Cooling effect for neighboring cells
        for neighbor in neighbors:
            if neighbor.cell_type in [0, 1]:  # Water or Land
                neighbor.temperature -= 0.1  # Cooling effect

    def _update_sea(self, neighbors):
        """
        Update Sea cells:
        - Evaporate water into nearby air cells.
        - Adjust temperature and water mass.
        """
        evaporation_rate = max(0.01, 0.02 * (self.temperature - 15))
        self.water_mass = max(0, self.water_mass - evaporation_rate)

        for neighbor in neighbors:
            if neighbor.cell_type == 6:  # Neighbor is Air
                # Transfer evaporated water to air cells
                neighbor.water_mass += evaporation_rate * 0.5
                neighbor.temperature += 0.1 * (self.temperature - neighbor.temperature)
                neighbor.pollution_level += 0.05 * self.pollution_level  # Pass some pollution to the air

    def _update_air(self, neighbors):
        rain_threshold = 0.2  # Threshold for water mass to trigger conversion to cloud
        pollution_diffusion_rate = 0.05
        temperature_diffusion_rate = 0.05

        # Convert to cloud if enough water mass is present and neighbors include clouds
        if self.water_mass > rain_threshold:
            for neighbor in neighbors:
                if neighbor.cell_type == 2:  # Neighbor is a Cloud
                    self.cell_type = 2  # Convert to Cloud
                    self.pollution_level = neighbor.pollution_level  # Inherit pollution
                    self.water_mass = max(self.water_mass, 0.2)  # Stabilize initial cloud water mass
                    logging.debug("Air cell converted to Cloud due to nearby cloud and sufficient water mass.")
                    return

        # Diffuse pollution and temperature with neighbors
        for neighbor in neighbors:
            temp_diffusion = temperature_diffusion_rate * (self.temperature - neighbor.temperature)
            self.temperature -= temp_diffusion
            neighbor.temperature += temp_diffusion

            pollution_diffusion = pollution_diffusion_rate * (self.pollution_level - neighbor.pollution_level)
            self.pollution_level -= pollution_diffusion
            neighbor.pollution_level += pollution_diffusion

        # Gradually evaporate water mass if not near clouds
        self.water_mass = max(0, self.water_mass - 0.005)  # Reduced evaporation rate


    def _update_cloud(self, neighbors, current_position, grid_size):
        rain_threshold = 0.1
        minimum_water_mass = 0.1  # Adjusted threshold for stable clouds
        evaporation_to_air_rate = 0.002  # Slower evaporation rate

        # Distribute rainwater to neighbors
        for neighbor in neighbors:
            if neighbor.cell_type in {0, 1, 4} and self.water_mass > rain_threshold:
                rain = min(0.05, self.water_mass)  # Controlled rain rate
                neighbor.water_mass += rain
                self.water_mass -= rain
                logging.debug(f"Cloud rained on {neighbor.cell_type}. Water mass: {self.water_mass}")

            # Transfer temperature and pollution to air cells
            if neighbor.cell_type == 6:  # Air
                temp_diffusion = 0.05 * (self.temperature - neighbor.temperature)
                self.temperature -= temp_diffusion
                neighbor.temperature += temp_diffusion

                pollution_diffusion = 0.03 * (self.pollution_level - neighbor.pollution_level)
                self.pollution_level -= pollution_diffusion
                neighbor.pollution_level += pollution_diffusion

                # Transfer water vapor to neighboring air cells
                water_diffusion = evaporation_to_air_rate
                self.water_mass = max(self.water_mass - water_diffusion, minimum_water_mass)  # Prevent excessive loss
                neighbor.water_mass += water_diffusion

        if self.water_mass < minimum_water_mass:
            logging.debug(f"Cloud converted to Air due to low water mass: {self.water_mass}")
            self.cell_type = 6  # Convert back to Air
            self.water_mass = 0.1  # Leave a small initial water mass for air


    def move(self, current_position, grid_size):
        if self.cell_type in [2, 6, 3]:
            x, y, z = current_position
            dx, dy = self.direction
            new_x = (x + dx) % grid_size[0]
            new_y = (y + dy) % grid_size[1]
            return new_x, new_y, z
        return current_position
    
    def get_color(self):
        """Get the color of the cell."""
        base_colors = {
            0: (0.0, 0.0, 1.0, 1.0),  # Sea (blue)
            1: (1.0, 0.84, 0.0, 1.0),  # Land (gold)
            2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
            3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
            5: (1.0, 0.0, 0.0, 1.0),  # City (red)
            6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
        }

        # Get the base color for the cell type or default to transparent white
        base_color = base_colors.get(self.cell_type, (1.0, 1.0, 1.0, 0.01))

        # Ensure the base_color has exactly 4 components (RGBA)
        if len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {self.cell_type}: {base_color}")
            return None

        # Tint based on pollution level
        pollution_intensity = min(1.0, self.pollution_level / 100.0)
        black_tinted_color = tuple(base_color[i] * (1.0 - pollution_intensity) for i in range(3))
        alpha = base_color[3]  # Keep the original alpha value

        return (*black_tinted_color, alpha)
