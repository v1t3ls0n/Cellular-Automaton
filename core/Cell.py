import numpy as np
import logging

baseline_temperature = 15  # Assume a global baseline temperature
freezing_point = 0  # Temperature threshold for melting ice
melting_point = 40  # Temperature threshold for melting ice
rain_threshold = 1.0
cloud_threshold = 1.0

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
        # next_cell._apply_natural_decay()
        # next_cell.adjust_temperature_with_pollution()

        # Call the appropriate update method based on cell type
        if self.cell_type == 0:  # sea
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
        elif self.cell_type == 7: # Rain
            next_cell._update_rain(neighbors)


        return next_cell


    
    def _update_forest(self, neighbors):
        if not self.sink_if_surrounded_by_sea_or_ice(neighbors):
            self.adjust_cell_temperature_to_neighbors(neighbors)
            self.adjust_cell_pollution_to_neighbors(neighbors)

            if np.random.uniform() < 0.3:
                if self.temperature > 60:
                    self.convert_to_desert()
                elif self.pollution_level == 0 and 0 < self.temperature <= baseline_temperature:
                    self.convert_to_city()

    def _update_desert(self, neighbors):
        for neighbor in neighbors:
            if neighbor.cell_type == 7:
                self.water_mass += neighbor.water_mass
                neighbor.water_mass = 0

        if not self.sink_if_surrounded_by_sea_or_ice(neighbors):
            if self.pollution_level == 0 and self.temperature < 30 and np.random.uniform() < 0.5:
                self.convert_to_forest()

    def _update_city(self, neighbors):
        self.adjust_cell_temperature_to_neighbors(neighbors)
        self.adjust_cell_pollution_to_neighbors(neighbors)
        if not self.sink_if_surrounded_by_sea_or_ice(neighbors):
            # Pollution and temperature increase rates for cities
            pollution_increase_rate = 0.3
            temperature_increase_rate = self.pollution_level * 0.3

            # Increase city pollution and temperature
            self.pollution_level += pollution_increase_rate * self.pollution_level
            self.temperature += temperature_increase_rate * self.temperature


            # Convert city to desert if conditions are extreme
            if ((self.temperature > 60 or self.temperature <= 0) or self.pollution_level > 100) and np.random.uniform() < 0.5:
                self.convert_to_desert()

    def _update_ice(self, neighbors):
        self.adjust_cell_temperature_to_neighbors(neighbors)
        if self.temperature > melting_point:
            self.convert_to_sea()
            return

    def _update_sea(self, neighbors):
        self.adjust_cell_temperature_to_neighbors(neighbors)
        self.adjust_cell_pollution_to_neighbors(neighbors)
        if self.temperature < freezing_point:
            self.convert_to_ice()
        elif self.temperature > melting_point:
            self.convert_to_air(neighbors)

    def _update_air(self, neighbors):
        self.adjust_cell_temperature_to_neighbors(neighbors)
        self.adjust_cell_pollution_to_neighbors(neighbors)
        # self.adjust_air_z_direction(neighbors)

        for neighbor in neighbors:
            if neighbor.cell_type == 4:
                self.forest_pollution_absorb()
        
        if self.is_surrounded_by_clouds(neighbors):
            self.convert_to_cloud()
        
    

            

    def _update_cloud(self, neighbors, current_position, grid_size):
        air_cells_neighbors_count = sum(1 if neighbor.cell_type == 6 else 0 for neighbor in neighbors)
        clouds_cells_neighbors_count = sum(1 if neighbor.cell_type == 2 else 0 for neighbor in neighbors)
        if clouds_cells_neighbors_count + air_cells_neighbors_count == len(neighbors):
            self.convert_to_rain()

    
    def _update_rain(self, neighbors):
        if self.water_mass == 0:
            self.convert_to_air()
            return

    def adjust_air_z_direction(self, neighbors):
        neighbors_avg_temp = self.calc_neighbors_avg_temperature(neighbors)
        if self.temperature > min(neighbors_avg_temp, melting_point, baseline_temperature):
            self.direction = (self.direction[0], self.direction[1], 1)
        elif self.temperature < max(freezing_point, neighbors_avg_temp):
            self.direction = (self.direction[0], self.direction[1], -1)
        else:
            self.direction = (self.direction[0], self.direction[1], 0)

    def adjust_temperature_with_pollution(self):

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

        pollution_decay_rate = 0.1  # Rate at which pollution naturally decreases
        temperature_decay_rate = 0.1  # Rate at which temperature naturally decreases

        # Apply decay to pollution level
        self.pollution_level = max(
            0, self.pollution_level - (self.pollution_level * pollution_decay_rate))

        # Apply decay to temperature, reducing towards a baseline temperature
        if self.temperature > baseline_temperature:
            self.temperature -= (self.temperature -
                                 baseline_temperature) * temperature_decay_rate
        elif self.temperature < baseline_temperature:
            self.temperature += (baseline_temperature -
                                 self.temperature) * temperature_decay_rate




    def absorb_rain_water_mass(self, neighbors):
        land_cells_count = sum(1 for neighbor in neighbors if neighbor.cell_type in {1,4,5}) 
        water_mass_to_absorb = self.water_mass
        for neighbor in neighbors:
            if neighbor.cell_type in {1,4,5}:
                neighbor.water_mass += water_mass_to_absorb/2


    def is_surrounded_by_clouds(self, neighbors):
        return sum(1 for neighbor in neighbors if neighbor.cell_type == 2) >= 0.5 * len(neighbors)

    def sink_if_surrounded_by_sea_or_ice(self, neighbors):
        if sum(1 for neighbor in neighbors if neighbor.cell_type in {0, 3}) >= 0.5 * len(neighbors):
            if self.temperature <= freezing_point:
                self.convert_to_ice()
            else:
                self.convert_to_sea()
            return True

        return False



    def calc_neighbors_avg_temperature(self, neighbors):
        return sum(neighbor.temperature for neighbor in neighbors)/len(neighbors)

    def calc_neighbors_avg_pollution(self, neighbors):
        return sum(neighbor.temperature for neighbor in neighbors)/len(neighbors)

    def adjust_cell_temperature_to_neighbors(self, neighbors):
        self.temperature = (self.temperature +
                            self.calc_neighbors_avg_temperature(neighbors))/2

    def adjust_cell_pollution_to_neighbors(self, neighbors):
        self.pollution_level = (self.pollution_level +
                                self.calc_neighbors_avg_pollution(neighbors))/2

    def forest_pollution_absorb(self):
        pollution_absorption_rate = 0.2
        cooling_effect = 0.2
        self.pollution_level = max(
            0, self.pollution_level - pollution_absorption_rate * self.pollution_level)
        self.temperature = max(
            self.temperature - self.temperature * cooling_effect, baseline_temperature)


    def convert_to_city(self):
        self.cell_type = 5
        self.water_mass = 0
        self.temperature += 2
        self.direction = (0, 0, 0)

    def convert_to_desert(self):
        self.cell_type = 1
        self.water_mass = 0
        self.temperature -= self.temperature * 0.2
        self.direction = (0, 0, 0)

    def convert_to_sea(self):
        self.cell_type = 0
        self.water_mass = 1.0
        self.direction = (self.direction[0], self.direction[1], 0)

    def convert_to_ice(self):
        self.cell_type = 3
        self.water_mass = 1.0
        self.pollution_level = 0
        self.direction = (self.direction[0], self.direction[1], 0)

    def convert_to_air(self, neighbors):
        self.cell_type = 6
        self.direction = (self.direction[0], self.direction[1], 1)
        # self.adjust_air_z_direction(neighbors)
    
    def convert_to_rain(self):
        self.cell_type = 7
        self.direction = (self.direction[0], self.direction[1], -1)

    def convert_to_forest(self):
        self.cell_type = 4
        self.direction = (0, 0, 0)
        self.temperature = baseline_temperature
        self.pollution_level = 0
        # self.water_mass = 0
    
    def convert_to_cloud(self):
        self.cell_type = 2
        self.direction = (self.direction[0], self.direction[1], 0)




    
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
            0: (0.0, 0.0, 1.0, 1.0),  # sea (blue)
            1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
            2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
            3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
            5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
            6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
            7: (0.2, 0.3, 0.5, 1.0), # Rain (Dark Blue-Grey)
        }

        # Get the base color for the cell type or default to transparent white
        base_color = base_colors.get(self.cell_type, (1.0, 1.0, 1.0, 0.01))

        # Ensure the base_color has exactly 4 components (RGBA)
        if len(base_color) != 4:
            logging.error(f"Invalid color definition for cell_type {
                          self.cell_type}: {base_color}")
            return None

        # Tint based on pollution level
        # Ensure within 0-1 range
        pollution_intensity = max(0.0, min(self.pollution_level / 100.0, 1.0))
        black_tinted_color = [
            max(0.0, min(base_color[i] * (1.0 - pollution_intensity), 1.0)) for i in range(3)]
        # Ensure alpha is also within 0-1 range
        alpha = max(0.0, min(base_color[3], 1.0))

        return (*black_tinted_color, alpha)
