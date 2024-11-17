import numpy as np


class Cell:
    def __init__(self, cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level=0):
        self.cell_type = cell_type  # Type: Sea, Land, Clouds, Icebergs, Forests, Cities
        self.temperature = temperature  # Temperature
        self.wind_strength = wind_strength  # Wind strength
        self.wind_direction = wind_direction  # Wind direction
        self.pollution_level = pollution_level  # Pollution level
        self.water_level = water_level  # Water level (e.g., sea, icebergs, or rain in clouds)

    def get_color(self):
        """Return the color for the cell, dynamically based on its state."""
        if self.cell_type == 0:  # Sea
            return "blue"
        elif self.cell_type == 1:  # Land
            return "yellow"  # Base yellow for land
        elif self.cell_type == 2:  # Clouds
            intensity = min(1.0, self.pollution_level / 50.0)  # Normalize pollution
            return (0.7, 0.7, 0.7, intensity)  # Gray with transparency based on pollution
        elif self.cell_type == 3:  # Icebergs
            return (0.5, 1.0, 1.0) if self.water_level > 0 else "cyan"  # Cyan for submerged, light cyan otherwise
        elif self.cell_type == 4:  # Forests
            return "darkgreen"  # Constant dark green for forests
        elif self.cell_type == 5:  # Cities
            intensity = min(1.0, self.pollution_level / 50.0)  # Normalize pollution
            return (1.0, 1.0 - intensity, 1.0 - intensity)  # Red with increasing intensity
        else:
            return (1.0, 1.0, 1.0)  # Default to white

    def update(self, neighbors):
        """
        Update the cell based on its type and interactions with neighboring cells.
        """
        # Sea
        if self.cell_type == 0:
            return  # Sea remains constant

        # Land
        elif self.cell_type == 1:
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_water = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_water
                    neighbor.water_level -= absorbed_water
            if self.temperature > 35:  # Drought
                self.water_level = max(0, self.water_level - 0.5)

        # Clouds
        elif self.cell_type == 2:
            if self.water_level > 0:
                for neighbor in neighbors:
                    if neighbor.cell_type in [0, 1]:  # Rain on sea or land
                        rain = min(0.2, self.water_level)
                        neighbor.water_level += rain
                        self.water_level -= rain


        # Icebergs
        elif self.cell_type == 3:
            if self.pollution_level > 20 or self.temperature > 0:  # Pollution speeds up melting
                self.water_level += 0.5  # Slow melting
                if self.water_level > 10:
                    self.cell_type = 0  # Turns into sea

        # Forests
        elif self.cell_type == 4:
            self.pollution_level = max(0, self.pollution_level - 0.5)  # Absorb pollution
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_rain = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_rain
                    neighbor.water_level -= absorbed_rain
            # Higher pollution destroys forests
            if self.pollution_level > 30:
                self.cell_type = 1  # Forest turns into land

        # Cities
        elif self.cell_type == 5:
            self.pollution_level += 2  # Generate pollution
            for neighbor in neighbors:
                neighbor.pollution_level += self.pollution_level * 2 # Spread pollution
                if neighbor.cell_type == 4:  # Forest nearby
                    if np.random.random() < 0.1:  # 10% chance of deforestation
                        neighbor.cell_type = 1
                if self.water_level > 5:  # Slow flooding destruction
                    if np.random.random() < 0.1:  # 5% chance of city destruction
                        self.cell_type = 0  # City destroyed, becomes sea
