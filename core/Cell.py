import numpy as np
import logging

class Cell:
    def __init__(self, cell_type, temperature=0.0, water_mass=0.0, pollution_level=0.0, direction=(0, 0)):
        self.cell_type = cell_type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction

    def update(self, neighbors, current_position=None, grid_size=None):
        self._adjust_temperature_with_pollution()
        has_neighboring_cities = any(neighbor.cell_type == 5 for neighbor in neighbors)

        if not has_neighboring_cities:
            # Decrease pollution and temperature if no neighboring cities
            pollution_decay = 0.1  # Adjust this value for pollution decay rate
            temperature_decay = 0.1  # Adjust this value for temperature decay rate
            self.pollution_level = max(0, self.pollution_level - pollution_decay)
            self.temperature = max(0, self.temperature - temperature_decay)

        if self.cell_type == 0:  # Sea
            self._update_sea(neighbors)
        elif self.cell_type == 1:  # Land
            self._update_land(neighbors)
        elif self.cell_type == 2:  # Cloud
            self._update_cloud(neighbors, current_position, grid_size)
        elif self.cell_type == 3:  # Ice
            self._update_ice(neighbors)
        elif self.cell_type == 4:  # Forest
            self._update_forest(neighbors)
        elif self.cell_type == 5:  # City
            self._update_city(neighbors)
        elif self.cell_type == 6:  # Air
            self._update_air(neighbors)

    def _adjust_temperature_with_pollution(self):
        pollution_effect = self.pollution_level * 0.05
        max_effect = 10
        self.temperature += min(pollution_effect, max_effect)
        if self.pollution_level < 10:
            self.temperature = max(0, self.temperature - 0.1)

    def convert_to_ice(self):
        if self.cell_type == 0:  # Sea
            self.cell_type = 3  # Convert to ice
            # Water mass remains, but ice is solid

    def convert_to_city(self):
        if self.cell_type == 4:
            self.cell_type = 5
            # self.pollution_level = 10
            self.pollution_level = 0
            # self.water_mass = 0
            self.temperature += 2

    def convert_to_land(self):
        if self.cell_type in [4, 5]:
            self.cell_type = 1
            self.pollution_level = 0
            # self.water_mass = 0
            self.temperature -= 1

    def _update_forest(self, neighbors):
        """
        Update logic for forests. Forests absorb pollution and may convert to land or city.
        """
        self.pollution_level = max(0, self.pollution_level - 0.02 * self.pollution_level)
        cooling_effect = min(0.1, self.pollution_level * 0.02)
        self.temperature -= cooling_effect

        for neighbor in neighbors:
            # Absorb pollution from neighboring cells
            if neighbor.pollution_level > 0:
                absorbed_pollution = min(0.1, neighbor.pollution_level * 0.1)
                neighbor.pollution_level -= absorbed_pollution
                self.pollution_level += absorbed_pollution

            # Handle rainfall
            if neighbor.cell_type == 2 and neighbor.water_mass > 0:  # Cloud neighbor
                rain = min(0.1, neighbor.water_mass)
                self.water_mass += rain
                neighbor.water_mass -= rain

        # Convert to land if pollution and temperature are too high
        if self.pollution_level > 80 and self.temperature > 50 and np.random.random() < 0.02:
            self.convert_to_land()

        # Convert to city under suitable conditions
        elif self.pollution_level == 0 and self.temperature <= 25 and np.random.random() < 0.05:
            self.convert_to_city()
            
    def _update_land(self, neighbors):
        """
        Update logic for land cells. Land can turn into forest, sea, or remain based on conditions.
        """
        surrounding_sea_count = sum(1 for neighbor in neighbors if neighbor.cell_type == 0)

        # If surrounded by sea and has high water mass, convert to sea
        if surrounding_sea_count > len(neighbors) * 0.6 and self.water_mass > 1.0:
            self.cell_type = 0  # Convert to sea
            # self.water_mass = 1.0
            self.pollution_level = 0
            return

        # Recovery: Land can turn into forest if conditions are met
        if self.pollution_level == 0 and self.temperature < 25:
            recovery_chance = 0.1
            if np.random.random() < recovery_chance:
                self.cell_type = 4  # Convert to forest
                self.pollution_level = 0

        # Handle pollution spread
        for neighbor in neighbors:
            if neighbor.cell_type == 6 or neighbor.cell_type == 0:  # Air or sea
                pollution_transfer = (self.pollution_level - neighbor.pollution_level) * 0.05
                neighbor.pollution_level += pollution_transfer
                self.pollution_level -= pollution_transfer


    def _update_city(self, neighbors):
        self.pollution_level += 0.2 * self.pollution_level
        self.temperature += 0.2 * self.temperature

        for neighbor in neighbors:
            pollution_spread = 0.1 * self.pollution_level
            neighbor.pollution_level += pollution_spread

        if self.temperature > 60 and self.pollution_level > 100 and np.random.random() < 0.2:
            self.convert_to_land()

    def _update_ice(self, neighbors):
        """
        Update logic for ice cells. Ice melts into sea or adds water mass to nearby cells.
        """
        if self.temperature > 0:
            # Melt into sea
            self.cell_type = 0  # Convert to sea
            # Water mass remains unchanged

        for neighbor in neighbors:
            if neighbor.cell_type == 0:  # Sea
                # Add water mass to nearby sea cells
                neighbor.water_mass += self.water_mass
                self.water_mass = 0  # Transfer water mass to sea
            elif neighbor.cell_type == 6:  # Air
                # Slight evaporation from ice into air
                evaporation = min(0.01, self.water_mass)
                self.water_mass -= evaporation
                neighbor.pollution_level += evaporation * 0.1  # Ice may carry pollution


    def _update_sea(self, neighbors):
        """
        Update logic for sea cells. Ensure water transitions into other states (clouds, ice).
        """
        # Evaporation logic: water mass turns into clouds
        evaporation_rate = max(0.01, 0.02 * (self.temperature - 15))
        evaporated_water = min(evaporation_rate, self.water_mass)
        self.water_mass -= evaporated_water

        for neighbor in neighbors:
            if neighbor.cell_type == 2:  # Cloud
                # Add evaporated water to neighboring clouds
                neighbor.water_mass += evaporated_water / len(neighbors)

            elif neighbor.cell_type == 0:  # Other sea cells
                # Redistribute water evenly
                water_diffusion = (self.water_mass - neighbor.water_mass) * 0.1
                neighbor.water_mass += water_diffusion
                self.water_mass -= water_diffusion

        # If temperature drops below freezing, convert to ice
        if self.temperature < -2.0 and self.water_mass > 0:
            self.cell_type = 3  # Convert to ice
            # Preserve the water mass when converting to ice
            self.pollution_level = max(self.pollution_level, 0)  # Retain pollution in ice

   
    def _update_air(self, neighbors):
        """
        Update logic for air cells. Air pollution propagates to water (sea, ice) and other air cells.
        """
        for neighbor in neighbors:
            if neighbor.cell_type in [0, 3]:  # Sea or Ice
                pollution_transfer = self.pollution_level * 0.05  # Transfer rate
                neighbor.pollution_level += pollution_transfer
                self.pollution_level -= pollution_transfer

            elif neighbor.cell_type == 6:  # Neighboring air cell
                pollution_transfer = (self.pollution_level - neighbor.pollution_level) * 0.05
                neighbor.pollution_level += pollution_transfer
                self.pollution_level -= pollution_transfer


    def _update_cloud(self, neighbors, current_position, grid_size):
        """
        Update logic for clouds. Clouds should redistribute water and generate rain.
        """
        self.move(current_position, grid_size)

        if self.water_mass > 0:
            for neighbor in neighbors:
                if neighbor.cell_type in [0, 1, 4]:  # Sea, Land, Forest
                    # Rainfall logic
                    rain = min(0.1, self.water_mass)
                    neighbor.water_mass += rain
                    self.water_mass -= rain

        # Water mass conservation: clouds should not "lose" water arbitrarily
        if self.water_mass <= 0 and self.pollution_level <= 10:
            self.cell_type = 6  # Dissipate into air if empty

    def move(self, current_position, grid_size):
        if self.cell_type in [2, 6, 0, 3]:
            x, y, z = current_position
            dx, dy = self.direction
            new_x = (x + dx) % grid_size[0]
            new_y = (y + dy) % grid_size[1]
            return new_x, new_y, z
        return current_position
    
    def get_color(self):
        """Get the color of the cell."""

        # if self.cell_type == 6: # Air (Transparent)
        #     return None

        base_colors = {
            0: (0.0, 0.0, 1.0, 1.0),  # Sea (blue)
            1: (1.0, 0.84, 0.0, 1.0),  # Land (gold)
            2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
            3: (0.0, 1.0, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
            5: (1.0, 0.0, 0.0, 1.0),  # City (Red)
            6: (1.0, 1.0, 1.0, 0.01),  # Air (White)

        }

        base_color = base_colors[self.cell_type]
        # Tint towards black based on pollution level
        pollution_intensity = min(1.0, self.pollution_level / 100.0)
        black_tinted_color = tuple(
            base_color[i] * (1.0 - pollution_intensity) for i in range(4)
        )

        return black_tinted_color
