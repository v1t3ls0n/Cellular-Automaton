import numpy as np
import logging
from core.conf import config


class Particle:
    config = config
    ####################################################################################################################
    ###################################### CLASS UTILS #################################################################
    ####################################################################################################################

    def __init__(self, cell_type, temperature, water_mass, pollution_level, direction, elevation):

        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.elevation = elevation

    def clone(self):
        return Particle(
            cell_type=self.cell_type,
            temperature=self.temperature,
            water_mass=self.water_mass,
            pollution_level=self.pollution_level,
            direction=self.direction,
            elevation=self.elevation
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
        if self.is_below_sea_level(neighbors):
            self.go_down()
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

        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_desert()
            self.go_down()
            self.convert_to_ocean()
        elif self.pollution_level > 100 or abs(self.temperature) >= self.config["evaporation_point"]:
            self.convert_to_desert()

    def _update_ice(self, neighbors):
        # Ice melts into ocean if temperature exceeds melting point
        if self.temperature > self.config["melting_point"]:
            self.convert_to_ocean()

    def _update_ocean(self, neighbors):
        # Ocean freezes if temperature is below freezing point
        if self.temperature <= self.config["freezing_point"]:
            self.convert_to_ice()
        # Ocean evaporates into air if temperature exceeds evaporation point
        elif self.temperature >= self.config["evaporation_point"]:
            self.convert_to_air()

    def _update_rain(self, neighbors):
        """
        Update logic for rain cells. Rain moves downward and interacts with the environment.
        """
        neighbors_below = [
            neighbor for neighbor in neighbors if neighbor.elevation < self.elevation]

        # Check conditions to convert rain to ocean or land-based cells
        if self.is_above_sea_level(neighbors):
            self.convert_to_ocean()
        elif self.is_above_ground_level(neighbors):
            self.convert_to_desert()  # Convert to desert if hitting land without enough water
        elif neighbors_below:
            if self.contains_sea(neighbors_below):
                self.convert_to_ocean()
            elif self.contains_land(neighbors_below):
                self.convert_to_forest()
            else:
                self.go_down()  # Continue moving downward

        # Handle evaporation conditions for rain
        if self.temperature > self.config["evaporation_point"]:
            self.convert_to_air()

    def _update_air(self, neighbors):
        self.equilibrate_pollution_level(neighbors)
        # If air is at cloud level, attempt conversion to cloud
        if self.is_at_clouds_level(neighbors):
            self.convert_to_cloud()
        elif self.water_mass > 0.2:  # Threshold for cloud formation
            # Move upward for cloud formation
            self.go_up()
        else:
            self.go_static()  # Stabilize air

    def _update_cloud(self, neighbors):
        """
        Update logic for cloud cells. Clouds gain water from neighbors, stabilize at cloud level,
        or convert to rain or ice based on conditions.
        """
        freezing_point = self.config["freezing_point"]
        cloud_saturation_threshold = self.config["cloud_saturation_threshold"]

        # Exchange water with neighboring clouds or air
        self.exchange_water_mass(neighbors)

        # Convert to ice if temperature is below freezing
        if self.temperature < freezing_point:
            self.convert_to_ice()
            return

        # Convert to rain if water mass exceeds saturation threshold
        if self.water_mass >= cloud_saturation_threshold:
            self.convert_to_rain()
            return

        # Stabilize clouds at the proper height
        if self.is_at_clouds_level(neighbors):
            self.go_static()
        else:
            self.go_up()  # Move upward if not yet at cloud level


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
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_city(self):
        self.cell_type = 5
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_desert(self):
        self.cell_type = 1
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature -= 0.2 * self.temperature

    def convert_to_ocean(self):
        self.cell_type = 0
        self.water_mass = 1.0
        self.temperature = self.config["baseline_temperature"][self.cell_type]

    def convert_to_ice(self):
        self.cell_type = 3
        self.water_mass = 1.0
        self.temperature = self.config["baseline_temperature"][self.cell_type]
        self.go_down()

    def convert_to_air(self):
        self.cell_type = 6
        self.water_mass = 0.0

    def convert_to_rain(self):
        logging.info(f"Cloud at elevation {
                     self.elevation} converted into rain.")
        self.cell_type = 7  # Rain
        self.water_mass = 1.0
        self.go_down()  # Move rain downward

    def convert_to_cloud(self):
        logging.info(f"Air at elevation {
                     self.elevation} converted into cloud.")
        self.cell_type = 2  # Cloud
        self.water_mass = 1.0
        self.go_up()  # Move cloud upward

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
        self.temperature = (self.calc_neighbors_avg_temperature(
            neighbors) + self.temperature)/2

    def equilibrate_pollution_level(self, neighbors):
        self.pollution_level = (self.calc_neighbors_avg_pollution(
            neighbors) + self.temperature)/2

    def exchange_water_mass(self, neighbors):
        """
        Exchange water mass with neighboring clouds or air.
        Updates the current particle's water mass; neighbors adjust during their own updates.
        """
        total_transfer = 0
        for neighbor in neighbors:
            if neighbor.cell_type in {2, 6}:  # Cloud or Air
                # Calculate water mass transfer rate
                water_transfer = (neighbor.water_mass - self.water_mass) * 0.05
                self.water_mass += water_transfer
                total_transfer += water_transfer
        return total_transfer

####################################################################################################################
###################################### CELL ELEVATION ##############################################################
####################################################################################################################

    def go_down(self):
        self.direction = (self.direction[0], self.direction[1], -1)

    def go_up(self):
        self.direction = (self.direction[0], self.direction[1], 1)

    def go_static(self):
        self.direction = (self.direction[0], self.direction[1], 0)

    def stabilize(self):
        self.direction = (0, 0, 0)  # Stop movement

####################################################################################################################
######################################  CALC HELPER FUNCTIONS: #####################################################
####################################################################################################################


############################################### AVERAGES ###########################################################


    def calc_neighbors_avg_temperature(self, neighbors):
        return (sum(neighbor.temperature for neighbor in neighbors)) / len(neighbors)

    def calc_neighbors_avg_pollution(self, neighbors):
        return (sum(neighbor.pollution_level for neighbor in neighbors)) / len(neighbors)

    def calc_neighbors_avg_water_mass(self, neighbors):
        return (sum(neighbor.water_mass for neighbor in neighbors)) / len(neighbors)


######################################  SURROUNDINGS: ##############################################################


    def contains_land(neighbors_below):
        return any(neighbor.cell_type in {1, 4, 5} for neighbor in neighbors_below)

    def contains_sea(neighbors_below):
        return any(neighbor.cell_type in {0, 3} for neighbor in neighbors_below)

    def is_surrounded_by_sky_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by air or cloud cells.
        """
        sky_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            2, 6}]  # Only Cloud or Air
        # All neighbors must be sky cells
        return len(sky_cells) == len(neighbors)

    def is_surrounded_by_sea_cells(self, neighbors):
        """
        Check if the cell is surrounded entirely by sea or ice cells.
        """
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            0, 3}]  # Only Sea or Ice
        # All neighbors must be sea cells
        return len(sea_cells) == len(neighbors)

    def is_surrounded_by_ground(self, neighbors):
        """
        Check if the cell is surrounded entirely by ground-related cells (desert, forest, city).
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5}]  # Only Land-based cells
        # All neighbors must be ground cells
        return len(ground_cells) == len(neighbors)

##################################################  At #############################################################
    def is_at_clouds_level(self, neighbors):
        """
        Check if the cell is at cloud level (majority of neighbors are clouds).
        """
        if not neighbors:  # Handle cases with no neighbors
            return False
        # Count cloud neighbors
        clouds_cells_count = sum(1 for nei in neighbors if nei.cell_type == 2)
        # Strict majority clouds
        return clouds_cells_count >= len(neighbors) / 2

    def is_at_air_level(self, neighbors):
        """
        Check if the cell is at air level (i.e., no non-air or rain neighbors).
        """
        non_air_nor_rain_cells = [
            # Exclude Air
            neighbor for neighbor in neighbors if neighbor.cell_type not in {6}]
        return len(non_air_nor_rain_cells) == 0  # All neighbors must be air

################################################  Above  ###########################################################
    def is_above_ground_level(self, neighbors):
        """
        Check if the cell is above ground level (i.e., higher elevation than all ground neighbors).
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5}]  # Desert, Forest, City
        # Higher than all ground neighbors
        return len(ground_cells) > 0 and all(self.elevation > cell.elevation for cell in ground_cells)

    def is_above_sea_level(self, neighbors):
        """
        Check if the cell is above sea level (all neighbors are not sea or ice, and their elevation is lower).
        """
        sea_or_ice_neighbors = [
            # Sea or Ice neighbors
            nei for nei in neighbors if nei.cell_type in {0, 3}]
        return all(self.elevation > nei.elevation for nei in sea_or_ice_neighbors) if sea_or_ice_neighbors else True

############################################  Below Level ##########################################################
    def is_below_sea_level(self, neighbors):
        """
        Check if the cell is below sea level.
        A cell is below sea level if all sea/ice neighbors are at a higher elevation.
        """
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            0, 3}]  # Sea or Ice
        return len(sea_cells) > 0 and all(self.elevation < cell.elevation for cell in sea_cells)

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.
        A cell is below ground level if all ground neighbors are at a higher elevation.
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5}]  # Land types
        return len(ground_cells) > 0 and all(self.elevation < cell.elevation for cell in ground_cells)
