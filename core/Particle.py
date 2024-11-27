import numpy as np
import logging
from core.conf import config


class Particle:
    config = config

    def __init__(self, cell_type, temperature, water_mass, pollution_level, direction, elevation, position):
        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.elevation = elevation
        self.position = position  # Add position

    ####################################################################################################################
    ###################################### CLASS UTILS #################################################################
    ####################################################################################################################

    def clone(self):
        return Particle(
            cell_type=self.cell_type,
            temperature=self.temperature,
            water_mass=self.water_mass,
            pollution_level=self.pollution_level,
            direction=self.direction,
            elevation=self.elevation,
            position=self.position
        )

    def get_next_position(self, current_position, grid_size):

        if self.direction == (0, 0, 0):  # No movement for static cells
            return current_position

        x, y, z = current_position
        dx, dy, dz = self.direction

        new_x = (x + dx) % grid_size[0]
        new_y = (y + dy) % grid_size[1]
        new_z = (z + dz)

        if new_z <= 0:
            new_z = 0
            # self.direction = (dx,dy,0)
        elif new_z >= grid_size[2] - 1:
            new_z = grid_size[2] - 1
            # self.direction = (dx,dy,0)

        self.elevation = new_z

        return new_x, new_y, new_z

    def get_color(self):
        """Get the color of the cell."""
        # Get the base color for the cell type or default to transparent white
        base_color = self.config["base_colors"].get(self.cell_type)
        return base_color

        if base_color is None or len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {
                          self.cell_type}: {base_color}")
            return None

        # Tint based on pollution level
        # Pollution intensity affects the red tint (scaled to 0.0 to 1.0 range)
        pollution_intensity = max(0.0, min(self.pollution_level / 100.0, 1.0))

        red_tinted_color = [
            # Increase red channel
            min(1.0, base_color[0] + pollution_intensity),
            # Reduce green channel
            max(0.0, base_color[1] * (1.0 - pollution_intensity)),
            # Reduce blue channel
            max(0.0, base_color[2] * (1.0 - pollution_intensity)),
        ]

        # Ensure alpha remains unchanged
        alpha = max(0.0, min(base_color[3], 1.0))

        return (*red_tinted_color, alpha)


####################################################################################################################
###################################### CELL UPDATES: ###############################################################
####################################################################################################################


    def update_state(self, neighbors):
        """
        Compute the next state of the cell based on its neighbors and position.
        """

        if self.pollution_level < self.config["pollution_threshold"]:
            self._apply_natural_decay()

        self.equilibrate_temperature(neighbors)

        if self.cell_type == 0:  # Ocean
            self._update_ocean(neighbors)

        elif self.cell_type == 1:  # desert
            self._update_desert(neighbors)

        elif self.cell_type == 2:  # Cloud
            self._update_cloud(neighbors)

        elif self.cell_type == 3:  # Ice
            self._update_ice(neighbors)

        elif self.cell_type == 4:  # Forest
            self.equilibrate_pollution_level(neighbors)
            self._update_forest(neighbors)

        elif self.cell_type == 5:  # City
            self._update_city(neighbors)

        elif self.cell_type == 6:  # Air
            self.equilibrate_pollution_level(neighbors)
            self._update_air(neighbors)

        elif self.cell_type == 7:  # Rain
            self._update_rain(neighbors)

    def _update_forest(self, neighbors):
        aabsorption_rate = self.config["forest_pollution_absorption_rate"]
        cooling_effect = self.config["forest_cooling_effect"]
        self.pollution_level = max(
            0, self.pollution_level - aabsorption_rate * self.pollution_level)
        self.temperature = self.temperature - self.temperature * cooling_effect
        # Ensure forest stays on ground level and doesn't stack

        if self.is_below_sea_level(neighbors):
            self.go_down()
        elif not self.is_at_ground_level(neighbors):
            self.convert_to_desert()
        elif (self.temperature >= abs(self.config["evaporation_point"]) or self.pollution_level >= 100):
            self.convert_to_desert()
        elif (self.pollution_level == 0 and 0 < self.temperature <= self.config["baseline_temperature"][self.cell_type]):
            self.convert_to_city()

    def _update_desert(self, neighbors):
        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_ocean()
        elif self.is_above_sea_level(neighbors) and self.pollution_level == 0 and self.temperature in range(self.config["baseline_temperature"][self.cell_type]):
            self.convert_to_forest()

    def _update_city(self, neighbors):
        pollution_increase_rate = self.config["city_pollution_increase_rate"]
        warming_effect = self.config["city_warming_effect"]

        baseline_pollution_level = self.config["baseline_pollution_level"][self.cell_type]
        baseline_temperature = self.config["baseline_temperature"][self.cell_type]

        self.temperature = max(
            baseline_temperature, self.temperature + warming_effect * self.temperature)
        self.pollution_level = max(
            baseline_pollution_level, self.pollution_level + pollution_increase_rate * self.pollution_level)
        self.temperature += self.temperature + \
            (self.pollution_level * warming_effect)
    # Prevent city stacking

        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_desert()
            self.go_down()
            self.convert_to_ocean()
        elif not self.is_at_ground_level(neighbors):
            self.convert_to_desert()
        elif self.pollution_level > 100 or abs(self.temperature) >= self.config["evaporation_point"]:
            self.convert_to_desert()

    def _update_ice(self, neighbors):
        # Ice melts into ocean if temperature exceeds melting point
        dx, dy, dz = self.calculate_dominant_wind_direction(neighbors)
        if self.temperature > self.config["evaporation_point"]:
            # self.exchange_water_mass(neighbors)
            self.convert_to_air()
            dz = 1
        elif self.temperature > min(self.config["baseline_temperature"][self.cell_type], self.config["melting_point"]):
            self.convert_to_ocean()
            dz = -1
        else:
            dz = 0

        self.direction = (dx, dy, dz)

    def _update_ocean(self, neighbors):
        dx, dy, dz = self.calculate_dominant_wind_direction(neighbors)
        neighbors_below = [
            neighbor for neighbor in neighbors if neighbor.elevation < self.elevation]
        if self.is_surrounded_by_ground(neighbors_below):
            # self.exchange_water_mass(neighbors_below)
            self.convert_to_air()
            dz = 1

        elif self.temperature >= self.config["melting_point"]:
            self.convert_to_air()
            dz = 1
        # Ocean freezes if temperature is below freezing point
        elif self.temperature <= self.config["freezing_point"]:
            self.convert_to_ice()
            dz = -1
        else:
            dz = 0
        # Ocean evaporates into air if temperature exceeds evaporation point
        self.direction = (dx, dy, dz)

    def _update_air(self, neighbors):
        self.equilibrate_pollution_level(neighbors)
        dx, dy, dz = self.calculate_dominant_wind_direction(neighbors)

        # If air is at cloud level, attempt conversion to cloud
        if self.is_at_clouds_level(neighbors):
            self.convert_to_cloud()
            dz = -1
        # elif self.water_mass > 0.2:  # Threshold for cloud formation
            # Move upward for cloud formation
            # self.go_up()
        # else:
            # self.stabilize()  # Stabilize air
        self.direction = (dx, dy, dz)

    def _update_rain(self, neighbors):
        """
        Update logic for rain cells. Rain should move downward and convert to ocean or land.
        """
        neighbors_below = [
            neighbor for neighbor in neighbors if neighbor.elevation < self.elevation]
        dx, dy, dz = self.calculate_dominant_wind_direction(neighbors)

        # Rain moves downward

        if self.temperature >= self.config["baseline_temperature"][0]:
            self.convert_to_ocean()
            dz = -1
        elif self.is_surrounded_by_ground(neighbors_below):
            # self.exchange_water_mass(neighbors_below)
            self.convert_to_air()
            dz = -1
        elif self.contains_sea(neighbors_below):
            if self.is_surrounded_by_sea_cells(neighbors):
                logging.info(f"Rain at elevation {
                             self.elevation} converted into ocean.")
                self.convert_to_ocean()
                dz = 0
            elif self.is_surrounded_by_ground(neighbors_below):
                logging.info(f"Rain at elevation {
                             self.elevation} converted into forest or desert.")
                self.convert_to_ocean()
                dz = -1
        else:
            # If no neighbors below, rain evaporates if the temperature is too high
            if self.temperature > self.config["evaporation_point"]:
                logging.info(f"Rain at elevation {
                             self.elevation} evaporated due to high temperature.")
                # self.exchange_water_mass(neighbors_below)
                self.convert_to_air()
                dz = 1
            else:
                self.convert_to_air()

        self.direction = (dx, dy, dz)

    def _update_cloud(self, neighbors):
        """
        Update logic for cloud cells. Clouds gain water from neighbors, stabilize at cloud level,
        or convert to rain or ice based on conditions.
        """
        freezing_point = self.config["freezing_point"]
        cloud_saturation_threshold = self.config["cloud_saturation_threshold"]
        dx, dy, dz = self.calculate_dominant_wind_direction(neighbors)

        # Gain water mass from neighbors
        # self.exchange_water_mass(neighbors)
        if self.temperature >= self.config["baseline_temperature"][0]:
            self.convert_to_ocean()
            dz = -1
        # Convert to ice if below freezing point
        if self.temperature < freezing_point:
            logging.info(f"Cloud at elevation {
                         self.elevation} converted into ice due to low temperature.")
            self.convert_to_ice()
            dz = -1

        # Convert to rain if water mass exceeds saturation threshold
        if self.water_mass >= cloud_saturation_threshold:
            logging.info(f"Cloud at elevation {
                         self.elevation} converted into rain due to water saturation.")
            self.convert_to_rain()
            dz = -1

        # Stabilize at cloud level
        if self.is_at_clouds_level(neighbors):
            # self.stabilize()
            dz = 0
        else:
            # self.go_up()  # Move upward if not yet at cloud level
            dz = 1
    
        self.direction = (dx, dy, dz)
    


####################################################################################################################
###################################### CELL  CONVERSIONS ###########################################################
####################################################################################################################


    def convert_to_forest_or_desert(self):
        """
        Convert rain to either a forest or desert based on water mass and pollution level.
        """
        if self.water_mass > 0.5:  # Sufficient water mass for forest formation
            self.convert_to_forest()
        else:
            self.convert_to_desert()

    def convert_to_forest(self):
        self.cell_type = 4
        # self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_city(self):
        self.cell_type = 5
        # self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_desert(self):
        self.cell_type = 1
        # self.water_mass = 0
        self.direction = (0, 0, 0)
        # self.temperature -= 0.2 * self.temperature
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_ocean(self):
        self.cell_type = 0
        # self.water_mass = 1.0
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_ice(self):
        self.cell_type = 3
        # self.water_mass = 1.0
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.go_down()

    def convert_to_air(self):
        self.cell_type = 6
        # self.water_mass = 0.0

    def convert_to_rain(self):
        logging.info(f"Cloud at elevation {
                     self.elevation} converted into rain.")
        self.cell_type = 7
        # self.water_mass = 1.0
        self.go_down()

    def convert_to_cloud(self):
        logging.info(f"Air at elevation {
                     self.elevation} converted into cloud.")
        self.cell_type = 2
        # self.water_mass = 1.0
        self.go_up()


####################################################################################################################
##################################### CELL NATURAL DECAY : #########################################################
####################################################################################################################

    def _apply_natural_decay(self):

        # Rate at which pollution naturally decreases
        pollution_decay_rate = self.config["natural_pollution_decay_rate"]
        # Rate at which temperature naturally decreases
        temperature_decay_rate = self.config["natural_temperature_decay_rate"]

        # Apply decay to pollution level
        self.pollution_level = self.pollution_level - \
            (self.pollution_level * pollution_decay_rate)

        # Apply decay to temperature, reducing towards a baseline temperature
        if self.temperature > self.config["baseline_temperature"][self.cell_type]:
            self.temperature -= (self.temperature -
                                 self.config["baseline_temperature"][self.cell_type]) * temperature_decay_rate
        elif self.temperature < self.config["baseline_temperature"][self.cell_type]:
            self.temperature += (self.config["baseline_temperature"][self.cell_type] -
                                 self.temperature) * temperature_decay_rate

####################################################################################################################
############################################### CELL EQUILIBRATE ###################################################
####################################################################################################################

    def equilibrate_temperature(self, neighbors):
        """
        Equilibrates the cell's temperature based on its neighbors.
        """
        self.temperature = (self.calc_neighbors_avg_temperature(
            neighbors) + self.temperature) / 2

    def equilibrate_pollution_level(self, neighbors):
        """
        Equilibrates the cell's pollution level based on its neighbors.
        """
        self.pollution_level = (self.calc_neighbors_avg_pollution(
            neighbors) + self.pollution_level) / 2

    def exchange_water_mass(self, neighbors):
        """
        Exchange water mass with neighboring clouds or air.
        """
        total_transfer = 0
        for neighbor in neighbors:
            if neighbor.cell_type in {2, 6}:  # Cloud or Air
                # Calculate water mass transfer rate
                water_transfer = (neighbor.water_mass - self.water_mass) * 0.05
                if water_transfer > 0:
                    self.water_mass += water_transfer
                    total_transfer += water_transfer
        logging.debug(f"Cloud at elevation {self.elevation} exchanged {
                      total_transfer:.2f} water mass.")
        return total_transfer


####################################################################################################################
###################################### CELL ELEVATION ##############################################################
####################################################################################################################

    def go_down(self):
        self.direction = (self.direction[0], self.direction[1], -1)

    def go_up(self):
        self.direction = (self.direction[0], self.direction[1], 1)

    def go_left_or_right_only(self):
        dx, dy, _ = self.direction
        if abs(max(dx, dy)) == 0:
            if self.position[0] > self.position[1]:
                self.go_right()
            else:
                self.go_left()

    def go_right(self):
        dx, dy, dz = self.direction
        self.direction = (1, dy, dz)

    def go_left(self):
        dx, dy, dz = self.direction
        self.direction = (dx, 1, dz)

    def stabilize(self):
        self.direction = (0, 0, 0)  # Stop movement

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
                # Calculate water mass transfer rate
                water_transfer = (neighbor.water_mass - self.water_mass) * 0.05
                if water_transfer != 0:
                    # Store transfer amount for the neighbor
                    transfer_data[neighbor] = water_transfer
        return transfer_data

    def calculate_dominant_wind_direction(self, neighbors):

        total_dx = 0
        total_dy = 0
        total_dz = 0

        # מעבר על כל השכנים כדי לסכם את תרומת הכיוונים שלהם
        for neighbor in neighbors:
            dx, dy, dz = neighbor.direction  # קבלת כיוון החלקיק השכן
            total_dx += dx
            total_dy += dy
            total_dz += dz

        # קביעה של הכיוון הדומיננטי עבור כל ציר
        dominant_dx = 1 if total_dx > 0 else (-1 if total_dx < 0 else 0)
        dominant_dy = 1 if total_dy > 0 else (-1 if total_dy < 0 else 0)
        dominant_dz = 1 if total_dz > 0 else (-1 if total_dz < 0 else 0)

        return (dominant_dx, dominant_dy, dominant_dz)

######################################  SURROUNDINGS: ##############################################################

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

    def is_surrounded_by_sky_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by air or cloud cells.
        """
        sky_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {2, 6}]
        return len(sky_cells) == len(neighbors)

    def is_surrounded_by_sea_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by sea or ice cells.
        """
        sea_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {0, 3}]
        return len(sea_cells) == len(neighbors)

    def is_surrounded_by_ground(self, neighbors):
        """
        Check if the cell is surrounded entirely by ground-related cells (desert, forest, city).
        """
        ground_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {1, 4, 5}]
        return len(ground_cells) == len(neighbors)

##################################################  At #############################################################
    def is_at_ground_level(self, neighbors):
        """
        Check if the cell is at ground level (has no neighbors below it).
        """
        return all(neighbor.elevation >= self.elevation for neighbor in neighbors)

    def is_at_air_level(self, neighbors):
        """
        Check if the cell is at air level (i.e., no non-air or rain neighbors).
        """
        non_air_nor_rain_cells = [
            # Exclude Air
            neighbor for neighbor in neighbors if neighbor.cell_type not in {6}]
        return len(non_air_nor_rain_cells) == 0  # All neighbors must be air

    def is_at_clouds_level(self, neighbors):
        """
        Check if the cell is at cloud level (majority of neighbors are clouds).
        """
        if not neighbors:
            return False
        clouds_cells_count = sum(
            1 for neighbor in neighbors if neighbor.cell_type == 2)
        return clouds_cells_count >= len(neighbors) / 2

    def is_above_ground_level(self, neighbors):
        """
        Check if the cell is above ground level (i.e., higher elevation than all ground neighbors).
        """
        ground_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {1, 4, 5}]
        return len(ground_cells) > 0 and all(self.elevation > cell.elevation for cell in ground_cells)

    def is_above_sea_level(self, neighbors):
        """
        Check if the cell is above sea level (all neighbors are not sea or ice, and their elevation is lower).
        """
        sea_or_ice_neighbors = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {0, 3}]
        return all(self.elevation > nei.elevation for nei in sea_or_ice_neighbors) if sea_or_ice_neighbors else True

    def is_below_sea_level(self, neighbors):
        """
        Check if the cell is below sea level.
        """
        sea_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {0, 3}]
        return len(sea_cells) > 0 and all(self.elevation < cell.elevation for cell in sea_cells)

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.
        """
        ground_cells = [
            neighbor for neighbor in neighbors if neighbor.cell_type in {1, 4, 5}]
        return len(ground_cells) > 0 and all(self.elevation < cell.elevation for cell in ground_cells)
