import numpy as np
import logging

baseline_temperature = 15  # Assume a global baseline temperature
freezing_point = 0  # Temperature that cause water freeze and convert into ice
melting_point = 50  # Temperature threshold for melting ice
evaporation_point = 100  # Temperature threshold for melting ice
rain_threshold = 1.0
cloud_threshold = 1.0

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
            elevation = self.elevation
        )

    def update_state(self, neighbors , current_position, grid_size):
        """
        Compute the next state of the cell based on its neighbors and position.
        """
        
        self._apply_natural_decay()

        if self.cell_type == 0:  # Water
            self._update_water(neighbors)

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

        elif self.cell_type == 7: # Rain
            self._update_rain(neighbors)


        return self



####################################################################################################################
######################################  CELL'S SELF EFFECTS : ######################################################
####################################################################################################################

    def _apply_natural_decay(self):

        pollution_decay_rate = 0.1  # Rate at which pollution naturally decreases
        temperature_decay_rate = 0.1  # Rate at which temperature naturally decreases

        # Apply decay to pollution level
        self.pollution_level =  self.pollution_level - (self.pollution_level * pollution_decay_rate)

        # Apply decay to temperature, reducing towards a baseline temperature
        if self.temperature > baseline_temperature:
            self.temperature -= (self.temperature -
                                 baseline_temperature) * temperature_decay_rate
        elif self.temperature < baseline_temperature:
            self.temperature += (baseline_temperature -
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
    

    ############################## Surrounded By ######################################################

    def is_surrounded_by_sky_cells(self, neighbors):
        sky_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {2,6,7}]
        return len(neighbors) == len(sky_cells)
    
    def is_surrounded_by_sea_cells(self, neighbors):
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {0,3}]
        return len(neighbors) == len(sea_cells)

    def is_surrounded_by_ground(self, neighbors):
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {1,4,5,6}]
        return len(neighbors) == len(ground_cells)
    
    ############################## Above level ######################################################

    def is_above_ground_level(self, neighbors):
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {1,4,5}]
        return sum(1 for cell in ground_cells if self.elevation > cell.elevation)  == len(ground_cells)

    def is_above_sea_level(self, neighbors):
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {0,3}]
        return sum(1 for cell in sea_cells if self.elevation > cell.elevation)  == len(sea_cells)


    ############################## Below level ######################################################

    def is_below_sea_level(self, neighbors):
        sea_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {0,3}]
        return sum(1 for cell in sea_cells if self.elevation < cell.elevation)  == len(sea_cells)

    def is_below_ground_level(self, neighbors):
        ground_cells = [neighbor for neighbor in neighbors if neighbor.cell_type in {1,4,5}]
        return sum(1 for cell in ground_cells if self.elevation < cell.elevation)  == len(ground_cells)


        

####################################################################################################################
###################################### CELL_TYPE UPDATES: ##########################################################
####################################################################################################################


    def _update_forest(self, neighbors):
        pollution_absorption_rate = 0.1
        cooling_effect = 0.1
        self.pollution_level = max(
                0, self.pollution_level - pollution_absorption_rate * self.pollution_level)
        self.temperature = self.temperature - self.temperature * cooling_effect

        if self.is_below_sea_level(neighbors):
            self.sink_to_ocean(neighbors)
    
        elif self.temperature >= abs(evaporation_point) or self.pollution_level >= 100:
            self.convert_to_desert(neighbors)

        elif self.pollution_level == 0 and 0 < self.temperature <= baseline_temperature:
            self.convert_to_city(neighbors)

    def _update_desert(self, neighbors):
        if self.is_below_sea_level(neighbors):
            self.sink_to_ocean(neighbors)
        elif self.pollution_level == 0 and self.temperature <= baseline_temperature:
            self.convert_to_forest(neighbors)

    def _update_city(self, neighbors):
        pollution_increase_rate = 0.4
        warming_effect = 0.4
        self.pollution_level = max(self.pollution_level, 2.0)
        
        # self.pollution_level = max(0, self.pollution_level + max(pollution_increase_rate * self.pollution_level, 5.0))
        self.pollution_level += max(self.pollution_level * pollution_increase_rate,1)
        self.temperature = self.temperature + max(self.temperature * warming_effect, 0.1)

        if self.is_below_sea_level(neighbors):
            self.sink_to_ocean(neighbors)
        elif self.pollution_level > 100 or abs(self.temperature) >= evaporation_point:
            self.convert_to_desert(neighbors)

    def _update_ice(self, neighbors):
        new_temperature = (self.calc_neighbors_avg_temperature(neighbors) + self.temperature)/2
        self.temperature = new_temperature

        for neighbor in neighbors:
            self.temperature += (neighbor.temperature -self.temperature) 

        if self.temperature > melting_point:
            self.convert_to_water(neighbors)

    def _update_water(self, neighbors):
        new_temperature = (self.calc_neighbors_avg_temperature(neighbors) + self.temperature)/2
        self.temperature = new_temperature

        if self.temperature <= freezing_point:
            self.convert_to_ice(neighbors)
        elif self.temperature >= evaporation_point:
            self.temperature -= 0.5 * self.temperature
            self.water_mass = 1.0
            self.convert_to_air(neighbors)

    def _update_air(self, neighbors):   
        new_temperature = (self.calc_neighbors_avg_temperature(neighbors) + self.temperature)/2
        new_pollution_level = (self.calc_neighbors_avg_pollution(neighbors) + self.pollution_level)/2
        self.temperature = new_temperature
        self.pollution_level = new_pollution_level

        # if self.water_mass == 1.0 and self.is_below_ground_level(neighbors):
        #     self.sink_to_ocean(neighbors)
        if self.water_mass > 0: 
            if self.is_surrounded_by_sky_cells(neighbors):
                self.convert_to_cloud(neighbors)
            elif self.is_below_sea_level(neighbors):
                self.sink_to_ocean(neighbors)

        # else:
        #     (neighbors)
        
                  
    def _update_rain(self, neighbors):
        if self.is_below_ground_level(neighbors):
            self.sink_to_ocean(neighbors)


    def _update_cloud(self, neighbors):
        for neighbor in neighbors:
            self.temperature += (neighbor.temperature -self.temperature) 

        # (neighbors)
        if self.water_mass == 1.0 and self.is_surrounded_by_sky_cells(neighbors):
            self.convert_to_rain(neighbors)
        




####################################################################################################################
###################################### CELL_TYPE CONVERSIONS ##########################################################
####################################################################################################################
    def sink_to_ocean(self,neighbors):

        if self.temperature <= freezing_point:
            self.convert_to_ice(neighbors)
        else:
            self.convert_to_water(neighbors)

    def convert_to_forest(self,neighbors):
        self.cell_type = 4
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature
    def convert_to_city(self,neighbors):
        self.cell_type = 5
        self.direction = (0, 0, 0)
    def convert_to_desert(self,neighbors):
        self.cell_type = 1
        self.water_mass = 0
        self.temperature -= self.temperature * 0.2
        self.direction = (0, 0, 0)

    def convert_to_water(self,neighbors):
        self.cell_type = 0
        self.water_mass = 1.0
        dx,dy, _ = self.direction
        self.direction = (dx,dy,-1)
    def convert_to_ice(self,neighbors):
        self.cell_type = 3
        self.water_mass = 1.0
        dx,dy, _ = self.direction
        self.direction = (dx,dy,-1)
    def convert_to_rain(self,neighbors):
        self.cell_type = 7
        dx,dy, _ = self.direction
        self.direction = (dx,dy,-1)


    def convert_to_air(self,neighbors):
        self.cell_type = 6
        dx,dy, _ = self.direction
        self.direction = (dx,dy,1)

    def convert_to_cloud(self,neighbors):
        self.cell_type = 2
        dx,dy, _ = self.direction
        self.direction = (dx,dy,1)





####################################################################################################################
###################################### CELL UTILS FUNCTIONS: ##########################################################
####################################################################################################################
    
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
        elif new_z >= grid_size[2] - 1:
            new_z = grid_size[2] - 1

        self.elevation = new_z

        return new_x, new_y, new_z

    def get_color(self):
        """Get the color of the cell."""
        base_colors = {
            6: (1.0, 1.0, 1.0, 0.01), # Air (transparent white)
            2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
            0: (0.0, 0.0, 1.0, 1.0),  # Water (blue)
            3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
            7: (0.2, 0.3, 0.5, 1.0),  # Rain (gray blue)
            1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
            4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
            5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
        }

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


