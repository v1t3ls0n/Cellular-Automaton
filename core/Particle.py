import numpy as np
import logging
from core.conf import config

baseline_temperature, base_colors, freezing_point, melting_point, evaporation_point, pollution_threshold = (
    config["baseline_temperature"],
    config["base_colors"],
    config["freezing_point"],
    config["melting_point"],
    config["evaporation_point"],
    config["pollution_threshold"],
)


class Particle:
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
        base_color = base_colors.get(self.cell_type)

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

        if self.pollution_level < pollution_threshold:
            self._apply_natural_decay()
        else:
            self.equilibrate_temperature(neighbors)
            self.equilibrate_pollution_level(neighbors)

        if self.cell_type == 0:  # Ocean
            self._update_ocean(neighbors)

        elif self.cell_type == 1:  # desert
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

    def _update_forest(self, neighbors):
        pollution_absorption_rate = 0.1
        cooling_effect = 0.1
        self.pollution_level = max(
            0, self.pollution_level - pollution_absorption_rate * self.pollution_level)
        self.temperature = self.temperature - self.temperature * cooling_effect
        if self.is_below_sea_level(neighbors):
            self.go_down()
        elif (self.temperature >= abs(evaporation_point) or self.pollution_level >= 100):
            self.convert_to_desert()
        elif (self.pollution_level == 0 and 0 < self.temperature <= baseline_temperature[self.cell_type]):
            self.convert_to_city()

    def _update_desert(self, neighbors):
        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_ocean()
        elif self.is_above_sea_level(neighbors) and self.pollution_level == 0 and self.temperature in range(baseline_temperature[self.cell_type]):
            self.convert_to_forest()

    def _update_city(self, neighbors):
        pollution_increase_rate = 0.4
        warming_effect = 0.4
        self.pollution_level = max(self.pollution_level, 2.0)
        self.pollution_level += max(self.pollution_level *
                                    pollution_increase_rate, 1.0)
        self.temperature = self.temperature + \
            max(self.temperature * warming_effect, 1.0)
        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_desert()
            self.go_down()
            self.convert_to_ocean()
        elif self.pollution_level > 100 or abs(self.temperature) >= evaporation_point:
            self.convert_to_desert()

    def _update_ice(self, neighbors):
        # Ice melts into ocean if temperature exceeds melting point
        if self.temperature > melting_point:
            self.convert_to_ocean()

    def _update_ocean(self, neighbors):
        # Ocean freezes if temperature is below freezing point
        if self.temperature <= freezing_point:
            self.convert_to_ice()
        # Ocean evaporates into air if temperature exceeds evaporation point
        elif self.temperature >= evaporation_point:
            self.convert_to_air()

    def _update_rain(self, neighbors):
        logging.debug(f"Rain cell at elevation {self.elevation} updating...")
        if self.is_above_ground_level(neighbors):
            if self.is_above_sea_level(neighbors):
                logging.debug("Rain converting to ocean...")
                self.convert_to_ocean()
            else:
                logging.debug("Rain evaporating to desert...")
                self.convert_to_desert(neighbors)
        elif self.is_below_ground_level(neighbors):
            logging.debug("Rain sinking to ocean...")
            self.go_down()

    def _update_air(self, neighbors):
        # If air is at cloud level, attempt conversion to cloud
        if self.is_at_clouds_level(neighbors):
            self.convert_to_cloud()
        elif self.water_mass > 0.2:  # Threshold for cloud formation
            # Move upward for cloud formation
            self.go_up()
        else:
            self.go_static()  # Stabilize air

    def _update_cloud(self, neighbors):
        # Clouds should form at specific heights and stabilize
        if self.is_at_clouds_level(neighbors):
            # Convert to rain if conditions for rain are met
            if self.water_mass > 0.5:  # Threshold for rain formation
                self.convert_to_rain()
            else:
                self.go_static()  # Stabilize cloud
        else:
            self.go_up()  # Move upward to stabilize


####################################################################################################################
###################################### CELL  CONVERSIONS ###########################################################
####################################################################################################################

    def convert_to_forest(self):
        self.cell_type = 4
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature[self.cell_type]

    def convert_to_city(self):
        self.cell_type = 5
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature[self.cell_type]

    def convert_to_desert(self):
        self.cell_type = 1
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature -= 0.2 * self.temperature

    def convert_to_ocean(self):
        self.cell_type = 0
        self.water_mass = 1.0
        self.temperature = baseline_temperature[self.cell_type]

    def convert_to_ice(self):
        self.cell_type = 3
        self.water_mass = 1.0
        self.temperature = baseline_temperature[self.cell_type]
        self.go_down()

    def convert_to_rain(self):
        self.cell_type = 7
        self.water_mass = 1.0  # Rain drops
        self.go_down()

    def convert_to_air(self):
        self.cell_type = 6
        self.water_mass = 0.0

    def convert_to_cloud(self):
        self.cell_type = 2
        self.water_mass = 1.0  # Clouds hold water
        self.go_up()


####################################################################################################################
##################################### CELL NATURAL DECAY : #########################################################
####################################################################################################################


    def _apply_natural_decay(self):

        pollution_decay_rate = 0.1  # Rate at which pollution naturally decreases
        temperature_decay_rate = 0.1  # Rate at which temperature naturally decreases

        # Apply decay to pollution level
        self.pollution_level = self.pollution_level - \
            (self.pollution_level * pollution_decay_rate)

        # Apply decay to temperature, reducing towards a baseline temperature
        if self.temperature > baseline_temperature[self.cell_type]:
            self.temperature -= (self.temperature -
                                 baseline_temperature[self.cell_type]) * temperature_decay_rate
        elif self.temperature < baseline_temperature[self.cell_type]:
            self.temperature += (baseline_temperature[self.cell_type] -
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

####################################################################################################################
###################################### CELL ELEVATION ##############################################################
####################################################################################################################

    def go_down(self):
        dx, dy, _ = self.direction
        self.direction = (dx, dy, -1)  # Move downward

    def go_up(self):
        dx, dy, _ = self.direction
        self.direction = (dx, dy, 1)  # Move upward

    def go_static(self):
        dx, dy, _ = self.direction
        self.direction = (dx, dy, 0)  # Stop vertical movement


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
            0, 3, 7}]  # Only sea and ice
        return (len(sea_cells) >= 0 and len(sea_cells) == len(neighbors)) or all(self.elevation <= cell.elevation for cell in sea_cells)

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.
        A cell is below ground level if all ground neighbors are at a higher elevation.
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5, 6}]  # Desert, Forest, City
        return (len(ground_cells) > 0 and all(self.elevation < cell.elevation for cell in ground_cells))
