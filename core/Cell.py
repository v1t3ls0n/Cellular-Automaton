import numpy as np
import logging


class Cell:
    def __init__(self, cell_type=6, temperature=0, water_mass=0, pollution_level=0, direction=(0, 0, 0), elevation=None):

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
        next_cell._apply_natural_decay()
        # next_cell._adjust_temperature_with_pollution()

        # Call the appropriate update method based on cell type
        if self.cell_type == 0:  # Sea
            next_cell._update_sea(neighbors)
        elif self.cell_type == 1:  # desert
            next_cell._update_desert(neighbors)
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

    def _adjust_temperature_with_pollution(self):

        pollution_effect = self.pollution_level * 0.1  # Increased scaling factor
        max_effect = 5  # Higher maximum effect to reflect significant pollution impact
        self.temperature += min(pollution_effect, max_effect)

        # Stronger effect for very high pollution levels
        if self.pollution_level > 50:
            extra_effect = (self.pollution_level - 50) * \
                0.2  # Additional temperature increase
            # Limit extra effect to 10 degrees
            self.temperature += min(extra_effect, 3)

        # Apply natural cooling if pollution is very low
        if self.pollution_level < 10:
            self.temperature = max(0, self.temperature - 0.2)

    def _apply_natural_decay(self):

        pollution_decay_rate = 0.05  # Rate at which pollution naturally decreases
        temperature_decay_rate = 0.05  # Rate at which temperature naturally decreases

        # Apply decay to pollution level
        self.pollution_level = max(
            0, self.pollution_level - (self.pollution_level * pollution_decay_rate))

        # Apply decay to temperature, reducing towards a baseline temperature
        baseline_temperature = 25  # Assume a global baseline temperature
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

    def convert_to_desert(self):
        if self.cell_type in [4, 5]:
            self.cell_type = 1
            self.pollution_level = 0
            self.water_mass = 0
            self.temperature -= 1

    def _update_forest(self, neighbors):

        # Pollution reduction rate for forests
        pollution_absorption_rate = 0.3
        cooling_effect = 0.3  # Cooling effect proportional to pollution

        # Reduce forest pollution
        self.pollution_level = max(
            0, self.pollution_level - pollution_absorption_rate * self.pollution_level)

        # Cool the forest temperature
        self.temperature -= self.pollution_level * cooling_effect

        # Interact with neighboring cells
        for neighbor in neighbors:
            # Absorb pollution from neighbors
            if neighbor.pollution_level > 0:
                absorbed_pollution = min(
                    0.2, pollution_absorption_rate * neighbor.pollution_level)
                neighbor.pollution_level -= absorbed_pollution

            # Reduce the temperature of neighbors
            neighbor.temperature -= (cooling_effect * self.pollution_level) if neighbor.temperature > 15 else 0

        # Convert forest to desert or city based on conditions
        if self.pollution_level > 100 or (self.temperature > 50 or self.temperature < 0) and np.random.uniform() < 0.1:
            self.convert_to_desert()
        elif self.pollution_level == 0 and self.temperature <= 25 and np.random.uniform() < 0.1:
            self.convert_to_city()

    def _update_desert(self, neighbors):
        surrounding_sea_count = sum(
            1 for neighbor in neighbors if neighbor.cell_type == 0)
        if surrounding_sea_count > len(neighbors) * 0.6 and self.water_mass > 1.0:
            self.cell_type = 0
            self.water_mass = 1.0
            self.pollution_level = 0
            return

        if self.pollution_level == 0 and self.temperature < 30 and np.random.uniform() < 0.5:
            self.cell_type = 4
            self.pollution_level = 0
            self.water_mass = 0

    def _update_city(self, neighbors):

        # Pollution and temperature increase rates for cities
        pollution_increase_rate = 0.1
        temperature_increase_rate = 0.1

        # Increase city pollution and temperature
        self.pollution_level += pollution_increase_rate * self.pollution_level
        self.temperature += temperature_increase_rate * self.temperature

        # Interact with neighboring cells
        for neighbor in neighbors:
            # Spread pollution to neighbors
            pollution_spread = 0.1 * self.pollution_level
            neighbor.pollution_level += pollution_spread

            # Increase temperature of neighbors
            temperature_increase = 0.1 * self.temperature
            neighbor.temperature += temperature_increase

        # Convert city to desert if conditions are extreme
        if (self.temperature > 60 or self.temperature <= 0) or self.pollution_level > 100:
            self.convert_to_desert()

    def _update_ice(self, neighbors):

        freezing_point = 40  # Temperature threshold for melting ice

        if self.temperature > freezing_point:
            self.cell_type = 3  # Convert Ice to Sea (Water)
            water_increase = 0.01  # Amount of water added when ice melts
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
            if neighbor.cell_type in [0, 1]:  # Water or desert
                neighbor.temperature -= 0.1  # Cooling effect

    def _update_sea(self, neighbors):

        evaporation_rate = max(0.01, 0.02 * (self.temperature - 15))
        self.water_mass = max(0, self.water_mass - evaporation_rate)
        if self.temperature >= 100:
            self.direction =  (neighbor.direction[0], neighbor.direction[1], 1)
            self.cell_type = 6
            self.water_mass = 0
        for neighbor in neighbors:
            # if neighbor.temperature >= 100 and neighbor.cell_type == 0:
            #     self.direction =  (neighbor.direction[0], neighbor.direction[1], -1)
            #     self.cell_type = 2
            if neighbor.cell_type == 6:  # Neighbor is Air
                # Transfer evaporated water to air cells
                neighbor.water_mass += evaporation_rate * 0.5
                neighbor.temperature += 0.1 * \
                    (self.temperature - neighbor.temperature)
                # Pass some pollution to the air
                neighbor.pollution_level += 0.05 * self.pollution_level

    def _update_air(self, neighbors):
        rain_threshold = 1.0  # Threshold for water mass to trigger conversion to cloud
        pollution_diffusion_rate = 0.05
        temperature_diffusion_rate = 0.05
        

        # Convert to cloud if enough water mass is present and neighbors include clouds
        if self.water_mass > rain_threshold:
            self.direction =  (0,0, -1)
            # self.cell_type = 0
        for neighbor in neighbors:
                if neighbor.cell_type == 2:  # Neighbor is a Cloud
                    # self.cell_type = 2  # Convert to Cloud
                    self.pollution_level = neighbor.pollution_level  # Inherit pollution
                    # Stabilize initial cloud water mass
                    self.water_mass = self.water_mass + neighbor.water_mass
                    logging.debug(
                        "Air cell converted to Cloud due to nearby cloud and sufficient water mass.")
                    return

        # Diffuse pollution and temperature with neighbors
        for neighbor in neighbors:
            temp_diffusion = temperature_diffusion_rate * \
                (self.temperature - neighbor.temperature)
            self.temperature -= temp_diffusion
            neighbor.temperature += temp_diffusion

            pollution_diffusion = pollution_diffusion_rate * \
                (self.pollution_level - neighbor.pollution_level)
            self.pollution_level -= pollution_diffusion
            neighbor.pollution_level += pollution_diffusion
            # if neighbor.water_mass > rain_threshold:
            #     neighbor.direction =  (self.direction[0], self.direction[1], -1)
            #     self.cell_type = 0

        # Gradually evaporate water mass if not near clouds
        # Reduced evaporation rate
        self.water_mass = max(0, self.water_mass - 0.005)

    def _update_cloud(self, neighbors, current_position, grid_size):
        rain_threshold = 1.0
        cloud_threshold = 1.0
        minimum_water_mass = 0.1  # Adjusted threshold for stable clouds
        evaporation_to_air_rate = 0.002  # Slower evaporation rate
        if  self.water_mass > rain_threshold:
                        self.cell_type = 0
                        self.direction = (0,0, -1)
        elif self.water_mass > cloud_threshold:
                        self.cell_type = 0
                        self.direction = (0,0, 1)
        # Distribute rainwater to neighbors
        for neighbor in neighbors:
            if neighbor.cell_type == 6:
                rain =  self.water_mass  # Controlled rain rate
                neighbor.water_mass += rain/len(neighbors)
                neighbor.temperature -= self.temperature/len(neighbors)
                self.water_mass -=  rain/len(neighbors)
                self.temperature+=neighbor.temperature
                logging.debug(f"Cloud rained on {
                              neighbor.cell_type}. Water mass: {self.water_mass}")
        


            # Transfer temperature and pollution to air cells
            if neighbor.cell_type == 6:  # Air
                temp_diffusion = 0.05 * \
                    (self.temperature - neighbor.temperature)
                self.temperature -= temp_diffusion
                neighbor.temperature += temp_diffusion

                pollution_diffusion = 0.03 * \
                    (self.pollution_level - neighbor.pollution_level)
                self.pollution_level -= pollution_diffusion
                neighbor.pollution_level += pollution_diffusion

                # Transfer water vapor to neighboring air cells
                water_diffusion = evaporation_to_air_rate
                # Prevent excessive loss
                self.water_mass = max(
                    self.water_mass - water_diffusion, minimum_water_mass)
                neighbor.water_mass += water_diffusion
            
            if self.water_mass < cloud_threshold:
                self.cell_type = 6
                self.water_mass = min(self.water_mass, 0)
                


    def move(self, current_position, grid_size):

        if self.direction == (0, 0, 0):  # No movement for static cells
            return current_position

        x, y, z = current_position
        dx, dy, dz = self.direction
        new_z = z + dz
        
        if new_z <= 0:
            new_z = 0
        elif new_z >= grid_size[2]:
            new_z = grid_size[2] - 1
        
        new_x = (x + dx) % grid_size[0]
        new_y = (y + dy) % grid_size[1]

        return new_x, new_y, new_z

    def get_color(self):
        """Get the color of the cell."""
        base_colors = {
            0: (0.0, 0.0, 1.0, 1.0),  # Sea (blue)
            1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
            2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
            3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
            5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
            6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
        }

        # Get the base color for the cell type or default to transparent white
        base_color = base_colors.get(self.cell_type, (1.0, 1.0, 1.0, 0.01))

        # Ensure the base_color has exactly 4 components (RGBA)
        if len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {self.cell_type}: {base_color}")
            return None

        # Tint based on pollution level
        pollution_intensity = max(0.0, min(self.pollution_level / 100.0, 1.0))  # Ensure within 0-1 range
        black_tinted_color = [max(0.0, min(base_color[i] * (1.0 - pollution_intensity), 1.0)) for i in range(3)]
        alpha = max(0.0, min(base_color[3], 1.0))  # Ensure alpha is also within 0-1 range

        return (*black_tinted_color, alpha)
