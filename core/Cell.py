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
        self.pollution_level = max(0, self.pollution_level - 0.02 * self.pollution_level)
        cooling_effect = min(0.1, self.pollution_level * 0.02)
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

        if self.pollution_level > 80 and self.temperature > 50 and np.random.random() < 0.2:
            self.convert_to_land()
        elif self.pollution_level == 0 and self.temperature <= 25 and np.random.random() < 0.05:
            self.convert_to_city()

    def _update_land(self, neighbors):
        surrounding_sea_count = sum(1 for neighbor in neighbors if neighbor.cell_type == 0)
        if surrounding_sea_count > len(neighbors) * 0.6 and self.water_mass > 1.0:
            self.cell_type = 0
            self.water_mass = 1.0
            self.pollution_level = 0
            return

        if self.pollution_level == 0 and self.temperature < 25:
            recovery_chance = 0.1
            if np.random.random() < recovery_chance:
                self.cell_type = 4
                self.pollution_level = 0

    def _update_city(self, neighbors):
        self.pollution_level += 0.2 * self.pollution_level
        self.temperature += 0.2 * self.temperature

        for neighbor in neighbors:
            pollution_spread = 0.1 * self.pollution_level
            neighbor.pollution_level += pollution_spread

        if self.temperature > 60 and self.pollution_level > 100 and np.random.random() < 0.2:
            self.convert_to_land()

    def _update_ice(self, neighbors):
        if self.temperature > 0:
            self.cell_type = 0
            self.water_mass += 1

        for neighbor in neighbors:
            if neighbor.cell_type == 0 and neighbor.temperature < 0.0:
                neighbor.cell_type = 3
                neighbor.water_mass = 0
            neighbor.temperature -= 0.1

    def _update_sea(self, neighbors):
        evaporation_rate = max(0.01, 0.02 * (self.temperature - 15))
        self.water_mass = max(0, self.water_mass - evaporation_rate)

        for neighbor in neighbors:
            temp_diffusion = (self.temperature - neighbor.temperature) * 0.2
            neighbor.temperature += temp_diffusion
            self.temperature -= temp_diffusion / len(neighbors)

            if neighbor.cell_type == 2:
                neighbor.water_mass += evaporation_rate / 2

            if neighbor.cell_type == 0:
                water_diffusion = (self.water_mass - neighbor.water_mass) * 0.1
                neighbor.water_mass += water_diffusion
                self.water_mass -= water_diffusion

            if self.temperature < -2.0 and self.water_mass > 0:
                self.cell_type = 3
                self.water_mass = 0

    def _update_air(self, neighbors):
        for neighbor in neighbors:
            neighbor.temperature += 0.4 * (self.temperature - neighbor.temperature)
            neighbor.pollution_level += 0.5 * (self.pollution_level - neighbor.pollution_level)

    def _update_cloud(self, neighbors, current_position, grid_size):
        self.move(current_position, grid_size)

        if self.water_mass > 0:
            for neighbor in neighbors:
                if neighbor.cell_type in [0, 1, 4]:
                    rain = min(0.1, self.water_mass)
                    neighbor.water_mass += rain
                    self.water_mass -= rain

        for neighbor in neighbors:
            if neighbor.cell_type in [1, 4, 5]:
                pollution_spread = 0.05 * self.pollution_level
                neighbor.pollution_level = min(100, neighbor.pollution_level + pollution_spread)

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
