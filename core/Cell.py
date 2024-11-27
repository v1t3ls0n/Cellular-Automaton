import numpy as np
import logging

# (0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air  | 7: Rain)
baseline_temperature = [15, 25, 5, -10, 20, 30, 10, 12]

base_colors = {
    6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
    2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
    0: (0.0, 0.0, 1.0, 1.0),  # Ocean (blue)
    3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
    7: (0.4, 0.8, 1.0, 0.1),  # Rain (light ctan)
    1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
    4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
    5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
}

freezing_point = -10  # Temperature that cause ocean freeze and convert into ice
melting_point = 50  # Temperature threshold for melting ice
evaporation_point = 100  # Temperature threshold for melting ice


class Cell:
    def __init__(self, cell_type, temperature, water_mass, pollution_level, direction, elevation):

        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction
        self.elevation = elevation

    def clone(self):
        return Cell(
            cell_type=self.cell_type,
            temperature=self.temperature,
            water_mass=self.water_mass,
            pollution_level=self.pollution_level,
            direction=self.direction,
            elevation=self.elevation
        )

    def update_state(self, neighbors, current_position, grid_size):
        """
        Compute the next state of the cell based on its neighbors and position.
        """

        self._apply_natural_decay()
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

        return self

    def move(self, current_position, grid_size):

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
        # Ensure the base_color has exactly 4 components (RGBA)

        return base_color

        if len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {
                          self.cell_type}: {base_color}")
            return None

        # Tint based on pollution level
        # Ensure within 0-1 range
        pollution_intensity = max(0.0, min(self.pollution_level / 100.0, 0.8))
        black_tinted_color = [
            max(0.0, min(base_color[i] * (1.0 - pollution_intensity), 1.0)) for i in range(3)]
        # Ensure alpha is also within 0-1 range
        alpha = max(0.0, min(base_color[3], 1.0))
        return (*black_tinted_color, alpha)

####################################################################################################################
######################################  CELL'S SELF EFFECTS : ######################################################
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
######################################  CELL's NEIGHBORS EFFECTS: ##################################################
####################################################################################################################

############################## Calc Neighbors Attributes's Average ######################################################

    def calc_neighbors_avg_temperature(self, neighbors):
        return (sum(neighbor.temperature for neighbor in neighbors)) / len(neighbors)

    def calc_neighbors_avg_pollution(self, neighbors):
        return (sum(neighbor.pollution_level for neighbor in neighbors)) / len(neighbors)

    def calc_neighbors_avg_water_mass(self, neighbors):
        return (sum(neighbor.water_mass for neighbor in neighbors)) / len(neighbors)

    def equilibrate_temperature(self, neighbors):
        self.temperature = (self.calc_neighbors_avg_temperature(
            neighbors) + self.temperature)/2

    def equilibrate_pollution_level(self, neighbors):
        self.pollution_level = (self.calc_neighbors_avg_pollution(
            neighbors) + self.temperature)/2

    ############################## Surrounded By ######################################################

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

    ############################## Above level ######################################################

    def is_at_air_level(self, neighbors):
        """
        Check if the cell is at air level (i.e., no non-air or rain neighbors).
        """
        non_air_nor_rain_cells = [
            # Exclude Air
            neighbor for neighbor in neighbors if neighbor.cell_type not in {6}]
        return len(non_air_nor_rain_cells) == 0  # All neighbors must be air

    def is_above_ground_level(self, neighbors):
        """
        Check if the cell is above ground level (i.e., higher elevation than all ground neighbors).
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5}]  # Desert, Forest, City
        # Higher than all ground neighbors
        return len(ground_cells) > 0 and all(self.elevation > cell.elevation for cell in ground_cells)

    def is_at_clouds_level(self, neighbors):
        """
        Check if the cell is at cloud level (majority of neighbors are clouds).
        """
        if not neighbors:  # Handle cases with no neighbors
            return False
        clouds_cells_count = sum(1 for nei in neighbors if nei.cell_type == 2)  # Count cloud neighbors
        return clouds_cells_count >= len(neighbors) / 2  # Strict majority clouds

    def is_above_sea_level(self, neighbors):
        """
        Check if the cell is above sea level (all neighbors are not sea or ice, and their elevation is lower).
        """
        sea_or_ice_neighbors = [
            # Sea or Ice neighbors
            nei for nei in neighbors if nei.cell_type in {0, 3}]
        return all(self.elevation > nei.elevation for nei in sea_or_ice_neighbors) if sea_or_ice_neighbors else True

    ############################## Below level ######################################################

    def is_below_sea_level(self, neighbors):
        """
        Check if the cell is below sea level.
        A cell is below sea level if all sea/ice neighbors are at a higher elevation.
        """
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {0, 3, 7}]  # Only sea and ice
        return (len(sea_cells) >= 0 and len(sea_cells) == len(neighbors)) or all(self.elevation <= cell.elevation for cell in sea_cells)

    def is_below_ground_level(self, neighbors):
        """
        Check if the cell is below ground level.
        A cell is below ground level if all ground neighbors are at a higher elevation.
        """
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {
            1, 4, 5, 6}]  # Desert, Forest, City
        return (len(ground_cells) > 0 and all(self.elevation < cell.elevation for cell in ground_cells))

####################################################################################################################
###################################### CELL_TYPE UPDATES: ##########################################################
####################################################################################################################

    def _update_forest(self, neighbors):
        pollution_absorption_rate = 0.1
        cooling_effect = 0.1
        self.pollution_level = max(
            0, self.pollution_level - pollution_absorption_rate * self.pollution_level)
        self.temperature = self.temperature - self.temperature * cooling_effect
        rand = np.random.uniform(0, 1)
        if self.is_below_sea_level(neighbors):
            self.sink_to_ocean(neighbors)
        elif (self.temperature >= abs(evaporation_point) or self.pollution_level >= 100) and rand < 0.4:
            self.convert_to_desert(neighbors)
        elif (self.pollution_level == 0 and 0 < self.temperature <= baseline_temperature[self.cell_type]) and rand < 0.2:
            self.convert_to_city(neighbors)

    def _update_desert(self, neighbors):
        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_ocean(neighbors)
        elif self.is_above_sea_level(neighbors) and self.pollution_level == 0 and self.temperature in range(baseline_temperature[self.cell_type]):
            self.convert_to_forest(neighbors)

    def _update_city(self, neighbors):
        pollution_increase_rate = 0.4
        warming_effect = 0.4
        self.pollution_level = max(self.pollution_level, 2.0)
        self.pollution_level += max(self.pollution_level *
                                    pollution_increase_rate, 1.0)
        self.temperature = self.temperature + \
            max(self.temperature * warming_effect, 1.0)
        if self.is_surrounded_by_sea_cells(neighbors):
            self.convert_to_ocean(neighbors)
        elif self.pollution_level > 100 or abs(self.temperature) >= evaporation_point:
            self.convert_to_desert(neighbors)







    def _update_ice(self, neighbors):
        # Ice melts into ocean if temperature exceeds melting point
        if self.temperature > melting_point:
            self.convert_to_ocean(neighbors)





    def _update_ocean(self, neighbors):
        # Ocean freezes if temperature is below freezing point
        if self.temperature <= freezing_point:
            self.convert_to_ice(neighbors)
        # Ocean evaporates into air if temperature exceeds evaporation point
        elif self.temperature >= evaporation_point:
            self.convert_to_air(neighbors)






    def _update_rain(self, neighbors):
        logging.debug(f"Rain cell at elevation {self.elevation} updating...")
        if self.is_above_ground_level(neighbors):
            if self.is_above_sea_level(neighbors):
                logging.debug("Rain converting to ocean...")
                self.convert_to_ocean(neighbors)
            else:
                logging.debug("Rain evaporating to desert...")
                self.convert_to_desert(neighbors)
        elif self.is_below_ground_level(neighbors):
            logging.debug("Rain sinking to ocean...")
            self.sink_to_ocean(neighbors)
                
            # else:
            #     logging.debug("Rain evaporating to desert...")
            #     self.convert_to_desert(neighbors)
        # elif self.is_below_ground_level(neighbors):
        #     logging.debug("Rain sinking to ocean...")
        #     self.sink_to_ocean(neighbors)






    def _update_air(self, neighbors):
        # If air is at cloud level, attempt conversion to cloud
        if self.is_at_clouds_level(neighbors):
            self.convert_to_cloud(neighbors)
        elif self.water_mass > 0.2:  # Threshold for cloud formation
            self.elevate_to_clouds_height(neighbors)  # Move upward for cloud formation
        else:
            self.stop_elevation_change(neighbors)  # Stabilize air

    def _update_cloud(self, neighbors):
        # Clouds should form at specific heights and stabilize
        self.randomize_z_direction()
        if self.is_at_clouds_level(neighbors):
            # Convert to rain if conditions for rain are met
            if self.water_mass > 0.5:  # Threshold for rain formation
                self.convert_to_rain(neighbors)
            else:
                self.stop_elevation_change(neighbors)  # Stabilize cloud
        else:
            self.elevate_to_clouds_height(neighbors)  # Move upward to stabilize

####################################################################################################################
###################################### CELL ELEVATION (Z-Direction) Updates ########################################
####################################################################################################################

    def randomize_xy_direction(self):
        dx, dy, dz = self.direction
        if dx == 0:
                dx = np.random.choice([-1,0, 1])
        if dy == 0:
                dx = np.random.choice([-1,0, 1])

        self.direction = (dx,dy,dz)
        

    def randomize_z_direction(self):
        dx, dy, dz = self.direction
        if dz == 0:
            dz = np.random.choice([0, 1, -1])

        self.direction = (dx,dy,dz)
        






    def sink_to_ocean(self, neighbors):
        self.randomize_xy_direction()
        dx, dy, _ = self.direction
        self.direction = (dx, dy, -1)  # Move downward



    def elevate_to_clouds_height(self, neighbors):
        if not self.is_at_clouds_level(neighbors):
            self.randomize_xy_direction()
            dx, dy, _ = self.direction
            self.direction = (dx, dy, 1)  # Move upward
        else:
            self.stop_elevation_change(neighbors)  # Stabilize at cloud height




    def stop_elevation_change(self, neighbors):
        self.randomize_xy_direction()
        dx, dy, _ = self.direction
        self.direction = (dx, dy, 0)  # Stop vertical movement







    def elevate_to_sea_surface(self, neighbors):
        self.randomize_xy_direction()
        dx, dy, _ = self.direction
        dz = 0 if self.is_below_ground_level(neighbors) else -1
        self.direction = (dx, dy, dz)

    def elevate_air(self, neighbors):
        self.randomize_xy_direction()
        dx, dy, _ = self.direction
        self.direction = (dx, dy, 1)


####################################################################################################################
###################################### CELL_TYPE CONVERSIONS #######################################################
####################################################################################################################


    def convert_to_forest(self, neighbors):
        self.cell_type = 4
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature[self.cell_type]

    def convert_to_city(self, neighbors):
        self.cell_type = 5
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature[self.cell_type]

    def convert_to_desert(self, neighbors):
        self.cell_type = 1
        self.water_mass = 0
        self.direction = (0, 0, 0)
        self.temperature -= 0.2 * self.temperature

    def convert_to_ocean(self, neighbors):
        self.cell_type = 0
        self.water_mass = 1.0
        self.temperature = baseline_temperature[self.cell_type]
        # self.sink_to_ocean(neighbors)

    def convert_to_ice(self, neighbors):
        self.cell_type = 3
        self.water_mass = 1.0
        self.temperature = baseline_temperature[self.cell_type]
        self.sink_to_ocean(neighbors)




    def convert_to_rain(self, neighbors):
        self.cell_type = 7
        self.water_mass = 1.0  # Rain drops
        self.sink_to_ocean(neighbors)





    def convert_to_air(self, neighbors):
        self.cell_type = 6
        self.water_mass = 0.0
        self.randomize_z_direction(neighbors)
        # self.elevate_air(neighbors)





    def convert_to_cloud(self, neighbors):
        self.cell_type = 2
        self.water_mass = 1.0  # Clouds hold water
        self.elevate_to_clouds_height(neighbors)



####################################################################################################################
###################################### CELL UTILS FUNCTIONS: ##########################################################
####################################################################################################################
