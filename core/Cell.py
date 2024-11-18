import numpy as np


class Cell:
    def __init__(self, cell_type=6, temperature=0.0, wind_strength=0.0, wind_direction=(0, 0, 0), pollution_level=0.0, water_level=0.0):
        self.cell_type = cell_type  # Default type is 6 which is for6 blank cell
        self.temperature = temperature
        self.wind_strength = wind_strength
        self.wind_direction = wind_direction
        self.pollution_level = pollution_level
        self.water_level = water_level

    def get_color(self):
        """Return the color for the cell, dynamically based on its state."""
        if self.cell_type == 0:  # Sea
            return "blue"
        elif self.cell_type == 1:  # Land
            return "yellow"
        elif self.cell_type == 2:  # Clouds (affected by pollution)
            # Normalize pollution level to [0, 1]
            pollution_intensity = min(float(self.pollution_level), 1.0)
            # Semi-transparent grayscale
            return (0.8, 0.8, 0.8, pollution_intensity)
            # return "darkgray"
        elif self.cell_type == 3:  # Icebergs
            return "cyan"
        elif self.cell_type == 4:  # Forests
            return "darkgreen"
        elif self.cell_type == 5:  # Cities
            return "purple"  # Solid purple for cities
        elif self.cell_type == 6:  # Air
            return "white"

    def update(self, neighbors, global_forest_count, global_city_count):
        """Update the cell based on its type and interactions with neighbors."""
        # Air interactions
        if self.cell_type == 6:
            for neighbor in neighbors:
                if neighbor.cell_type == 2:  # Cloud neighbor
                    # Absorb some pollution from clouds
                    pollution_diffusion = min(
                        0.01 * neighbor.pollution_level, 1.0)
                    self.pollution_level += pollution_diffusion

                    # Absorb some heat from clouds
                    temperature_diffusion = 0.05 * neighbor.temperature
                    self.temperature += temperature_diffusion
            return


    def update(self, neighbors, global_forest_count, global_city_count):
        """Update the cell based on its type and interactions with neighbors."""

        # Sea interactions
        if self.cell_type == 0:  # Sea
            for neighbor in neighbors:
                # Spread temperature to neighbors
                if neighbor.cell_type in [1, 4, 5]:  # Land, Forest, or City
                    temperature_diffusion = 0.1 * \
                        (self.temperature - neighbor.temperature)
                    neighbor.temperature += temperature_diffusion

                # Flooding logic
                if neighbor.cell_type in [1, 4, 5]:  # Land, Forest, or City
                    if neighbor.water_level < self.water_level:  # Neighbor is lower
                        flooding_amount = min(
                            self.water_level - neighbor.water_level, 0.5)
                        neighbor.water_level += flooding_amount
                        self.water_level -= flooding_amount

                        # Transform the flooded cell into sea if fully flooded
                        if neighbor.water_level > 5:  # Arbitrary threshold for flooding
                            neighbor.cell_type = 0  # Transform to sea
                            neighbor.temperature = self.temperature  # Match sea temperature
            return

        # Other interactions (Land, Clouds, Icebergs, Forests, Cities) remain the same
        # Land absorbs water and is affected by drought
        if self.cell_type == 1:
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_water = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_water
                    neighbor.water_level -= absorbed_water
            if self.temperature > 35:  # Drought
                self.water_level = max(0, self.water_level - 0.5)

            # Land may turn back into forest if conditions improve
            if global_forest_count > global_city_count and np.random.random() < 0.05:
                self.cell_type = 4  # Land turns into forest

        elif self.cell_type == 2:  # Clouds
            # Rain logic
            if self.water_level > 0:
                for neighbor in neighbors:
                    if neighbor.cell_type in [0, 1]:  # Rain on sea or land
                        rain = min(0.2, self.water_level)
                        neighbor.water_level += rain
                        self.water_level -= rain

            # Spread horizontally based on wind direction
            for neighbor in neighbors:
                if neighbor.cell_type == 6 and np.random.random() < 0.2:  # 20% chance to spread
                    neighbor.cell_type = 2  # Turn air into cloud
                    neighbor.pollution_level = self.pollution_level * 0.5  # Spread some pollution
                    temperature_diffusion = 0.01 * neighbor.temperature
                    self.temperature += temperature_diffusion

            # Reduce pollution to ensure clouds persist longer
            if self.pollution_level > 1:
                self.pollution_level -= 0.5

            # Icebergs melt due to temperature
        elif self.cell_type == 3:  # Icebergs
            if self.temperature > 0:
                melting_rate = min(0.1 + self.temperature *
                                0.002, 0.5)  # Gradual melting
                self.water_level += melting_rate
                if self.water_level > 10:
                    self.cell_type = 0  # Turns into sea
                    for neighbor in neighbors:
                        if neighbor.cell_type == 0:  # Sea cell
                            neighbor.water_level += melting_rate * 0.5
                        # Land or Cities near Icebergs
                        if neighbor.cell_type in [1, 5]:
                            neighbor.temperature += 0.2  # Regional heating effect

            # Spread icebergs if temperature is low and adjacent sea cells exist
            if self.temperature < -5:
                for neighbor in neighbors:
                    if neighbor.cell_type == 0 and np.random.random() < 0.3:  # 30% chance to spread
                        neighbor.cell_type = 3  # Turn sea into iceberg
                        neighbor.temperature = self.temperature  # Match temperature

                        if neighbor.cell_type == 0:  # Sea cell
                            neighbor.water_level += melting_rate * 0.5
                        # Land or Cities near Icebergs
                        if neighbor.cell_type in [1, 5]:
                            neighbor.temperature += 0.2  # Regional heating effect

            # Forests absorb pollution but can be deforested
        elif self.cell_type == 4:
            self.pollution_level = max(0, self.pollution_level - 0.5)
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_rain = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_rain
                    neighbor.water_level -= absorbed_rain
            # Forest extinction based on global pollution and temperature
            if global_forest_count < global_city_count:
                self.pollution_level += 0.5  # Absorb more pollution if forests are fewer
                if self.pollution_level > 50:
                    self.cell_type = 1  # Forest turns into land

        elif self.cell_type == 5:  # Cities
            # Increase pollution
            pollution_increase = 1 / (1 + 0.05 * self.pollution_level)  # Moderate growth
            self.pollution_level = min(self.pollution_level + pollution_increase, 100)

            # Increase temperature due to pollution
            self.temperature += 0.01 * self.pollution_level

            # קשר עם יערות סמוכים
            forests_nearby = sum(1 for neighbor in neighbors if neighbor.cell_type == 4)
            if forests_nearby == 0:
                # סיכון מוגבר להכחדת עיר אם אין יערות סמוכים
                extinction_chance = 0.1 + (1 / global_forest_count if global_forest_count > 0 else 1)
                if np.random.random() < extinction_chance:
                    self.cell_type = 1  # עיר הופכת לאדמה
                    global_city_count -= 1

            for neighbor in neighbors:
                # Spread pollution to neighbors
                pollution_spread = 0.01 * self.pollution_level / len(neighbors)
                neighbor.pollution_level = min(neighbor.pollution_level + pollution_spread, 100)

                # Deforestation effect
                if neighbor.cell_type == 4 and np.random.random() < 0.02:
                    neighbor.cell_type = 1  # Forest turns into land

                # High water levels affect cities
                if neighbor.cell_type == 0 and neighbor.water_level > 5:
                    if np.random.random() < 0.1:
                        self.cell_type = 0  # City turns into sea

            # Extreme pollution effect
            if self.pollution_level > 80 and np.random.random() < 0.3:
                self.cell_type = 1  # City turns into land

            # Air interactions
        elif self.cell_type == 6:
            for neighbor in neighbors:
                if neighbor.cell_type == 2:  # Cloud neighbor
                    # Absorb some pollution from clouds
                    pollution_diffusion = min(0.01 * neighbor.pollution_level, 1.0)
                    self.pollution_level += pollution_diffusion

                    # Absorb some heat from clouds
                    temperature_diffusion = 0.05 * neighbor.temperature
                    self.temperature += temperature_diffusion
            return
