import numpy as np
import logging
from core.conf import config


class Particle:
    config = config

    def __init__(self, cell_type, temperature, water_mass, pollution_level, direction,  position, grid_size):
        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.position = position  # Particle's current position in the grid
        self.grid_size = grid_size

    ####################################################################################################################
    ###################################### CLASS UTILS #################################################################
    ####################################################################################################################

    def clone(self):
        """
        Creates a copy of the current particle with identical attributes.
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

        Args:
            current_position (tuple): Current position of the particle (x, y, z).
            grid_size (tuple): Dimensions of the grid (x_max, y_max, z_max).

        Returns:
            tuple: New position of the particle (x, y, z).
        """
        if self.direction == (0, 0, 0):  # No movement for static cells
            return self.position

        x, y, z = self.position
        grid_size = self.grid_size
        dx, dy, dz = self.direction

        # Ensure position wraps around in x and y, but is clamped in z
        new_x = (x + dx) % grid_size[0]
        new_y = (y + dy) % grid_size[1]
        new_z = max(0, min(grid_size[2] - 1, z + dz))

        return new_x, new_y, new_z

    def get_color(self):
        """
        Get the visual representation of the particle based on its type and pollution level.

        Returns:
            tuple: RGBA color of the particle.
        """
        if self.config["tint"]:
            return self.get_color_red_tinted_by_pollution()
        else:
            return self.get_base_color()

    def get_base_color(self):
        """
        Get the base color for the particle's cell type.

        Returns:
            tuple: RGBA base color.
        """
        base_color = self.config["base_colors"].get(self.cell_type)
        if base_color is None:
            logging.error(f"Base color for cell_type {
                          self.cell_type} is not defined.")
        # Default to white if undefined
        return base_color or (1.0, 1.0, 1.0, 1.0)

    def get_color_red_tinted_by_pollution(self):
        """
        Apply a red tint to the base color based on the pollution level.

        Returns:
            tuple: RGBA color with red tint.
        """
        base_color = self.get_base_color()

        if base_color is None or len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {
                          self.cell_type}: {base_color}")
            return (1.0, 1.0, 1.0, 1.0)  # Default to white

        # Scale pollution intensity to [0.0, 1.0]
        pollution_intensity = max(0.0, min(self.pollution_level / 100.0, 1.0))

        # Apply red tint
        red_tinted_color = [
            # Increase red channel
            min(1.0, base_color[0] + pollution_intensity),
            # Decrease green channel
            max(0.0, base_color[1] * (1.0 - pollution_intensity)),
            # Decrease blue channel
            max(0.0, base_color[2] * (1.0 - pollution_intensity)),
        ]

        # Preserve alpha channel
        alpha = max(0.0, min(base_color[3], 1.0))

        return (*red_tinted_color, alpha)

    ####################################################################################################################
    ###################################### CELL UPDATES: ###############################################################
    ####################################################################################################################

    def update_state(self, neighbors):
        """
        Compute the next state of the cell based on its neighbors and position.
        """
        # if self.pollution_level < self.config["pollution_damage_threshold"]:
        self._apply_natural_decay()
        self.equilibrate_temperature(neighbors)
        self.equilibrate_pollution_level(neighbors)


        if self.cell_type == 0:  # Ocean
            self._update_ocean(neighbors)

        elif self.cell_type == 1:  # Desert
            self._update_desert(neighbors)

        elif self.cell_type == 2:  # Cloud
            self._update_cloud(neighbors)

        elif self.cell_type == 3:  # Ice
            self._update_ice(neighbors)

        elif self.cell_type == 4:  # Forest
            self._update_forest(neighbors)

        elif self.cell_type == 5:  # City
            self._update_city(neighbors)

        elif self.cell_type == 6:  # Air
            self._update_air(neighbors)

        elif self.cell_type == 7:  # Rain
            self._update_rain(neighbors)

    def _update_ocean(self, neighbors):
        """
        Ocean behavior: evaporates, freezes, or stabilizes.
        """
        self.go_down()
        if self.temperature > self.config["evaporation_point"] - 5:
            evaporation_rate = self.config["evaporation_rate"]
            self.water_mass -= evaporation_rate  # Partial melting
            if self.water_mass <= 0:
                self.convert_to_air()
        elif self.temperature <= self.config["freezing_point"]:
            self.convert_to_ice()
        else:
            self.stabilize()

    def _update_desert(self, neighbors):
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)

        if self.is_surrounded_by_sea_cells(neighbors_above+neighbors_aligned):
            self.convert_to_ocean()
        elif self.is_surrounded_by_land_cells(neighbors_aligned) and self.pollution_level == 0 and self.temperature in range(self.config["baseline_temperature"][self.cell_type]):
            self.convert_to_forest()

    def _update_cloud(self, neighbors):
        """
        Update cloud behavior based on water mass, temperature, and neighbors.
        """
        freezing_point = self.config["freezing_point"]
        saturation_threshold = self.config["cloud_saturation_threshold"]

        self.exchange_water_mass(neighbors)

        if self.water_mass >= saturation_threshold:
            self.convert_to_rain()
        elif self.temperature <= freezing_point:
            self.convert_to_ice()
        elif not self.is_surrounded_by_cloud_cells(neighbors):
            self.go_up()
        else:
            self.stabilize()

    def _update_ice(self, neighbors):
        """
        Ice behavior: melts, stabilizes, or converts.
        """
        dx, dy, _ = self.calculate_dominant_wind_direction(neighbors)
        melting_rate = self.config["melting_rate"]

        if self.temperature > self.config["melting_point"] - 5:
            self.water_mass -= melting_rate  # Partial melting
            if self.water_mass <= 0:
                self.convert_to_ocean()

        self.direction = (dx, dy, 0)

    def _update_forest(self, neighbors):
        absorption_rate = self.config["forest_pollution_absorption_rate"]
        cooling_effect = self.config["forest_cooling_effect"]
        pollution_level_tipping_point = self.config["pollution_level_tipping_point"]

        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)

        if self.pollution_level > pollution_level_tipping_point:
            absorption_rate *= 0.5
            cooling_effect *= 0.5
        if self.is_surrounded_by_sea_cells(neighbors_above+neighbors_aligned):
            self.convert_to_ocean()
        elif self.temperature >= abs(self.config["evaporation_point"]) or self.pollution_level >= 100:
            self.convert_to_desert()
        elif self.pollution_level == 0 and 0 < self.temperature <= self.config["baseline_temperature"][self.cell_type]:
            self.convert_to_city()
        else:
            self.pollution_level = max(0, self.pollution_level - absorption_rate * self.pollution_level)
            self.temperature -= self.temperature * cooling_effect


    def _update_city(self, neighbors):
        pollution_increase_rate = self.config["city_pollution_increase_rate"]
        warming_effect = self.config["city_warming_effect"]

        baseline_pollution_level = self.config["baseline_pollution_level"][self.cell_type]
        baseline_temperature = self.config["baseline_temperature"][self.cell_type]
        city_temperature_upper_limit = self.config["city_temperature_upper_limit"]
        city_pollution_upper_limit = self.config["city_pollution_upper_limit"]


        self.temperature = min(city_temperature_upper_limit, max(
            baseline_temperature, self.temperature + warming_effect * self.temperature))
        self.pollution_level = min(city_pollution_upper_limit, max(
            baseline_pollution_level, self.pollution_level +
            pollution_increase_rate * self.pollution_level
        ))
        self.temperature += self.pollution_level * warming_effect

        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)
        if self.is_surrounded_by_sea_cells(neighbors_above+neighbors_aligned):
            self.convert_to_ocean()
        elif self.pollution_level > 100 or abs(self.temperature) >= self.config["extinction_point"]:
            self.convert_to_desert()

    def _update_air(self, neighbors):
        """
        Air updates behavior to rise, stabilize, or convert into clouds.
        """
        self.direction = self.calculate_dominant_wind_direction(neighbors)

        if self.position[2] <= 2 or self.is_below_ground_level(neighbors) or self.is_below_sea_level(neighbors):  
            self.go_up()
        
        # Convert to cloud if saturated and in realistic height
        elif self.water_mass > self.config["cloud_saturation_threshold"] and self.position[2] >= (self.grid_size[2] - 3):
            self.convert_to_cloud()


    def _update_rain(self, neighbors):
        """
        Rain moves downward and converts to ocean or land.
        """
        neighbors_below = self.get_below_neighbors(neighbors)
        neighbors_above = self.get_above_neighbors(neighbors)
        neighbors_aligned = self.get_aligned_neighbors(neighbors)

        if self.is_surrounded_by_sea_cells(neighbors_aligned+neighbors_below):  # If at the lowest level, convert to ocean or land
            self.convert_to_ocean()
        else:
            self.go_down()

        if self.temperature > self.config["evaporation_point"]:
            self.convert_to_air()

    ####################################################################################################################
    ###################################### CELL  CONVERSIONS ###########################################################
    ####################################################################################################################

    def convert_to_ocean(self):
        self.cell_type = 0  # Set cell type to ocean
        self.water_mass = 1.0  # Oceans are full of water by default
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize()  # Stabilize motion

    def convert_to_desert(self):
        self.cell_type = 1  # Set cell type to desert
        self.water_mass = 0.0  # Deserts have no water by default
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize()  # Stabilize motion

    def convert_to_cloud(self):
        logging.info(f"Air at elevation {
                     self.position[2]} converted into cloud.")
        self.cell_type = 2  # Set cell type to cloud
        # Condensation increases water mass
        self.water_mass = min(1.0, self.water_mass + 0.5)
        self.temperature -= 2  # Clouds typically cool down during formation
        self.go_up()  # Clouds move upward

    def convert_to_ice(self):
        self.cell_type = 3  # Set cell type to ice
        self.water_mass = 1.0  # Ice retains full water mass
        # Set to freezing temperature
        self.temperature = self.config["freezing_point"]
        # self.stabilize()  # Stabilize motion

    def convert_to_forest(self):
        self.cell_type = 4  # Set cell type to forest
        self.water_mass = 0.0  # Forest cells don't retain water mass
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize()  # Stabilize motion

    def convert_to_city(self):
        self.cell_type = 5  # Set cell type to city
        self.water_mass = 0.0  # Cities don't retain water mass
        # Set baseline pollution
        self.pollution_level = self.config["baseline_pollution_level"][self.cell_type]
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.stabilize()  # Stabilize motion

    def convert_to_air(self):
        self.cell_type = 6  # Set cell type to air
        # Evaporation reduces water mass
        self.water_mass = max(0.0, self.water_mass - 0.5)
        self.temperature += 2  # Air warms during evaporation
        self.go_up()  # Air moves upward

    def convert_to_rain(self):
        self.cell_type = 7  # Set cell type to rain
        self.water_mass = 1.0  # Rain has full water mass
        self.temperature -= 1  # Rain cools during formation
        self.direction = (0, 0, -1)  # Move downward


    ####################################################################################################################
    ##################################### CELL NATURAL DECAY : #########################################################
    ####################################################################################################################

    def _apply_natural_decay(self):
        """Apply natural decay to pollution level and temperature."""
        pollution_decay_rate = self.config["natural_pollution_decay_rate"]
        temperature_decay_rate = self.config["natural_temperature_decay_rate"]

        # Pollution decay
        self.pollution_level = max(
            0, self.pollution_level -
            (self.pollution_level * pollution_decay_rate)
        )

        # Temperature decay towards baseline
        baseline_temp = self.config["baseline_temperature"][self.cell_type]
        if self.temperature > baseline_temp:
            self.temperature -= (self.temperature -
                                 baseline_temp) * temperature_decay_rate

        elif self.temperature < baseline_temp:
            self.temperature += (baseline_temp -
                                 self.temperature) * temperature_decay_rate

    ####################################################################################################################
    ############################################### CELL EQUILIBRATE ###################################################
    ####################################################################################################################

    def equilibrate_temperature(self, neighbors):
        """
        Equilibrates the cell's temperature based on its neighbors' weighted temperatures.
        """
        total_weight = 0
        weighted_temperature_sum = 0

        for neighbor in neighbors:
            weight = self.config["cell_type_weights"].get(
                neighbor.cell_type, 1.0)
            weighted_temperature_sum += neighbor.temperature * weight
            total_weight += weight

        # Calculate weighted average temperature
        if total_weight > 0:
            self.temperature = (weighted_temperature_sum /
                                total_weight + self.temperature) / 2

    def equilibrate_pollution_level(self, neighbors):
        """
        Equilibrates the cell's pollution level based on its neighbors' weighted pollution levels.
        """
        total_weight = 0
        weighted_pollution_sum = 0

        for neighbor in neighbors:
            weight = self.config["cell_type_weights"].get(
                neighbor.cell_type, 1.0)
            weighted_pollution_sum += neighbor.pollution_level * weight
            total_weight += weight

        # Calculate weighted average pollution level
        if total_weight > 0:
            self.pollution_level = (
                weighted_pollution_sum / total_weight + self.pollution_level) / 2

    def exchange_water_mass(self, neighbors):
        """
        Exchange water mass with neighboring cells (Cloud or Air).
        Updates water_mass for self and indirectly affects neighbors via transfer_map.
        """
        total_transfer = 0
        for neighbor in neighbors:
            if neighbor.cell_type in {2, 6}:  # Cloud or Air
                diff = abs(neighbor.water_mass - self.water_mass)
                weight = self.config["cell_type_weights"].get(
                    neighbor.cell_type, 1.0)
                water_transfer = (
                    diff * 0.05 * weight) if diff < self.config["water_transfer_threshold"] else 0
                if water_transfer > 0:
                    self.water_mass += water_transfer
                    total_transfer += water_transfer
        return total_transfer

    ####################################################################################################################
    ###################################### CELL ELEVATION ##############################################################
    ####################################################################################################################

    def go_down(self):
        if self.position[2] != 0:
            dx,dy,_= self.direction
            self.direction = (dx,dy, -1)

    def go_up(self):
        """
        Move the particle upward.
        """
        if self.position[2] < self.grid_size[2]:
            dx,dy,_ = self.direction
            self.direction = (dx,dy,1)

    def stabilize(self):
        """
        Stabilize the particle, halting movement.
        """
        self.direction = (0, 0, 0)

    ####################################################################################################################
    ######################################  CALC HELPER FUNCTIONS: #####################################################
    ####################################################################################################################

    ############################################### AVERAGES ###########################################################

    def calc_neighbors_avg_temperature(self, neighbors):
        """
        Calculates the average temperature of the neighbors.
        """
        return sum(neighbor.temperature for neighbor in neighbors) / len(neighbors)

    def calc_neighbors_avg_pollution(self, neighbors):
        """
        Calculates the average pollution level of the neighbors.
        """
        return sum(neighbor.pollution_level for neighbor in neighbors) / len(neighbors)

    def calc_neighbors_avg_water_mass(self, neighbors):
        """
        Calculates the average water mass of the neighbors.
        """
        return sum(neighbor.water_mass for neighbor in neighbors) / len(neighbors)

    def calculate_water_transfer(self, neighbors):
        """
        Calculate water transfer amounts for neighboring cells.
        Returns a dictionary with positions as keys and transfer amounts as values.
        """
        transfer_data = {}
        for neighbor in neighbors:
            if neighbor.cell_type in {2, 6}:  # Cloud or Air
                water_transfer = (neighbor.water_mass - self.water_mass) * 0.05
                if water_transfer != 0:
                    transfer_data[neighbor] = water_transfer
        return transfer_data

    def calculate_dominant_wind_direction(self, neighbors):
        """
        Calculate the dominant wind direction based on neighbors.
        """
        total_dx, total_dy, total_dz = 0, 0, 0

        for neighbor in neighbors:
            dx, dy, dz = neighbor.direction
            total_dx += dx
            total_dy += dy
            total_dz += dz

        dominant_dx = 1 if total_dx > 0 else (-1 if total_dx < 0 else 0)
        dominant_dy = 1 if total_dy > 0 else (-1 if total_dy < 0 else 0)
        dominant_dz = 1 if total_dz > 0 else (-1 if total_dz < 0 else 0)

        return dominant_dx, dominant_dy, dominant_dz

    ######################################  SURROUNDINGS: ##############################################################

    def is_at_lowest_level(self):
        _, _, z = self.position
        return z == 0

    def contains_sea(self, neighbors_below):
        """
        Check if any of the neighbors below are of type Sea (0) or Ice (3).
        """
        result = any(neighbor.cell_type in {0, 3}
                     for neighbor in neighbors_below)
        logging.debug(f"Neighbors below contain sea: {result}")
        return result

    def contains_land(self, neighbors_below):
        """
        Check if any of the neighbors below are of type Land (1, 4, 5).
        """
        result = any(neighbor.cell_type in {1, 4, 5}
                     for neighbor in neighbors_below)
        logging.debug(f"Neighbors below contain land: {result}")
        return result

    def is_surrounded_by_sea_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by sea or ice cells.
        """
        # return all(neighbor.cell_type in {0, 3} for neighbor in neighbors)
        # Majority are sea cells
        return sum(n.cell_type == 0 for n in neighbors) > len(neighbors) / 2

    def is_surrounded_by_cloud_cells(self, neighbors):
        """
        Check if the air particle is at cloud level.
        """
        return sum(n.cell_type == 2 for n in neighbors) > len(neighbors) / 2  # Majority are sea cells

    def is_surrounded_by_land_cells(self, neighbors):
        """
        Check if the air particle is at cloud level.
        """
        return sum(n.cell_type in {1,4,5,6} for n in neighbors) == len(neighbors)   # Majority are sea cells

    def is_at_ground_level(self, neighbors):
        """
        Check if the cell is at ground level.
        """
        return self.position[2] == 0

    def is_above_sea_level(self, neighbors):
        """
        Check if the cell is above sea level.
        """
        return all(self.position[2] > n.position[2] for n in neighbors if n.cell_type in {0, 3})

    def is_below_sea_level(self, neighbors):
        """
        Check if the cell is below sea level.
        """
        return all(self.position[2] < n.position[2] for n in neighbors if n.cell_type in {0, 3})

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.
        """
        return all(self.position[2] < n.position[2] for n in neighbors if n.cell_type in {1, 4, 5})

    def get_above_neighbors(self,neighbors):
         return [n for n in neighbors if n.position[2] > self.position[2]]
    def get_below_neighbors(self,neighbors):
         return [n for n in neighbors if n.position[2] < self.position[2]]
    def get_aligned_neighbors(self,neighbors):
         return [n for n in neighbors if n.position[2] == self.position[2]]


