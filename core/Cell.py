import numpy as np

class Cell:
    def __init__(self, cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level=0):
        self.cell_type = cell_type  # Type: Sea, Land, Clouds, Icebergs, Forests, Cities
        self.temperature = temperature  # Temperature
        self.wind_strength = wind_strength  # Wind strength
        self.wind_direction = wind_direction  # Wind direction as a tuple (dx, dy, dz)
        self.pollution_level = pollution_level  # Pollution level
        self.water_level = water_level  # Water level (e.g., sea, icebergs, or rain in clouds)

    def get_color(self):
        """Return the color for the cell, dynamically based on its state."""
        if self.cell_type == 0:  # Sea
            return "blue"
        elif self.cell_type == 1:  # Land
            return "yellow"
        elif self.cell_type == 2:  # Clouds
            intensity = min(1.0, self.pollution_level / 50.0)
            return (0.7, 0.7, 0.7, intensity)  # Gray with transparency
        elif self.cell_type == 3:  # Icebergs
            return (0.5, 1.0, 1.0) if self.water_level > 0 else "cyan"
        elif self.cell_type == 4:  # Forests
            return "darkgreen"
        elif self.cell_type == 5:  # Cities
            intensity = min(1.0, self.pollution_level / 50.0)
            return (1.0, 1.0 - intensity, 1.0 - intensity)  # Red with intensity
        else:
            return "white"  # Default to white

    def update(self, neighbors):
        """Update the cell based on its type and interactions with neighbors."""
        # Sea remains constant
        if self.cell_type == 0:
            return

        # Land absorbs water and is affected by drought
        elif self.cell_type == 1:
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_water = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_water
                    neighbor.water_level -= absorbed_water
            if self.temperature > 35:  # Drought
                self.water_level = max(0, self.water_level - 0.5)

        # Clouds spread pollution and rain
        elif self.cell_type == 2:
            if self.water_level > 0:
                for neighbor in neighbors:
                    if neighbor.cell_type in [0, 1]:  # Rain on sea or land
                        rain = min(0.2, self.water_level)
                        neighbor.water_level += rain
                        self.water_level -= rain

            # Spread pollution based on wind strength
            for neighbor in neighbors:
                pollution_spread = min(0.1 * self.pollution_level, 5.0)  # Cap pollution spread
                neighbor.pollution_level += pollution_spread
                self.pollution_level -= pollution_spread

        # Icebergs melt due to temperature
        elif self.cell_type == 3:
            if self.temperature > 0:
                melting_rate = min(0.1 + self.temperature * 0.002, 0.5)  # Gradual melting
                self.water_level += melting_rate
                if self.water_level > 10:
                    self.cell_type = 0  # Turns into sea
                    for neighbor in neighbors:  # Raise sea level for adjacent water cells
                        if neighbor.cell_type == 0:
                            neighbor.water_level += melting_rate * 0.5

        # Forests absorb pollution but can be deforested
        elif self.cell_type == 4:
            self.pollution_level = max(0, self.pollution_level - 0.5)
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_rain = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_rain
                    neighbor.water_level -= absorbed_rain

            if self.pollution_level > 30:
                self.cell_type = 1  # Forest turns into land

        # Cities generate pollution and increase temperature
        elif self.cell_type == 5:
            self.pollution_level = min(self.pollution_level + 1, 100)  # Slower pollution increase
            self.temperature += 0.05 * self.pollution_level  # Pollution gradually increases temperature
            for neighbor in neighbors:
                neighbor.pollution_level = min(neighbor.pollution_level + self.pollution_level * 0.01, 100)
                if neighbor.cell_type == 4 and np.random.random() < 0.05:
                    neighbor.cell_type = 1  # Deforestation

            if self.water_level > 5:  # Flooding
                if np.random.random() < 0.02:
                    self.cell_type = 0  # City destroyed, becomes sea

        # Cap temperature
        self.temperature = min(self.temperature, 50)  # Avoid runaway temperature
