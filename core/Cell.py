class Cell:
    def __init__(self, cell_type=6, temperature=0.0, water_mass=0.0, pollution_level=0.0, direction=(0, 0)):
        self.cell_type = cell_type  # 0: Sea, 1: Land, 2: Cloud, 3: Ice, 4: Forest, 5: City, 6: Air
        self.phase = self.determine_phase(cell_type)  # Automatically assign phase based on cell type
        self.temperature = temperature
        self.water_mass = water_mass
        self.pollution_level = pollution_level
        self.direction = direction  # Represents (dx, dy)

    @staticmethod
    def determine_phase(cell_type):
        """Determine the phase of the cell based on its type."""
        if cell_type in [1, 4, 5, 3]:  # Solid: Land, Forest, City, Ice
            return "solid"
        elif cell_type in [0]:  # Liquid: Sea
            return "liquid"
        elif cell_type in [2, 6]:  # Gas: Cloud, Air
            return "gas"
        else:
            return "unknown"  # Fallback for undefined cell types

    def update(self, neighbors):
        if self.phase == "gas":
            self._update_gas(neighbors)
        elif self.phase == "liquid":
            self._update_liquid(neighbors)
        elif self.phase == "solid":
            self._update_solid(neighbors)

    def _update_gas(self, neighbors):
        if self.cell_type == 6:  # Air
            self._update_air(neighbors)
        elif self.cell_type == 2:  # Cloud
            self._update_cloud(neighbors)

    def _update_air(self, neighbors):
        for neighbor in neighbors:
            if neighbor.cell_type == 2:  # Cloud
                neighbor.direction = self.direction  # Air influences Cloud direction
        for neighbor in neighbors:
            neighbor.temperature += 0.1 * (self.temperature - neighbor.temperature)
            neighbor.pollution_level += 0.1 * (self.pollution_level - neighbor.pollution_level)

    def _update_cloud(self, neighbors):
        for neighbor in neighbors:
            if neighbor.cell_type == 6:  # Air
                self.direction = neighbor.direction
        if self.water_mass > 0.5:
            for neighbor in neighbors:
                if neighbor.phase == "liquid":  # Rain on water-based cells
                    transfer = min(0.1, self.water_mass)
                    self.water_mass -= transfer
                    neighbor.water_mass += transfer
        self.move()

    def move(self):
        # Placeholder for movement logic; requires grid updates in State class
        pass

    def _update_liquid(self, neighbors):
        if self.cell_type == 0:  # Sea
            if self.temperature > 25 and self.water_mass > 0.5:
                self.water_mass -= 0.1
                for neighbor in neighbors:
                    if neighbor.cell_type == 6:  # Air
                        neighbor.cell_type = 2  # Turn Air into Cloud
                        neighbor.phase = "gas"
                        neighbor.water_mass += 0.1

    def _update_solid(self, neighbors):
        if self.cell_type == 4:  # Forest
            self.pollution_level = max(0, self.pollution_level - 0.5)
            if self.pollution_level > 50 or self.temperature > 35:
                self.cell_type = 1  # Land
                self.phase = "solid"
        elif self.cell_type == 3:  # Ice
            if self.temperature > 0:
                self.cell_type = 0  # Sea
                self.phase = "liquid"



    def get_color(self):
        """
        Get the color of the cell based on its type and pollution level.
        Pollution affects the hue of air cells.
        """
        base_colors = {
            0: (0.0, 0.0, 1.0),  # Sea (blue)
            1: (1.0, 1.0, 0.0),  # Land (yellow)
            2: (0.5, 0.5, 0.5),  # Cloud (gray)
            3: (0.0, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0),  # Forest (dark green)
            5: (0.5, 0.0, 0.5),  # City (purple)
            6: (1.0, 1.0, 1.0, 0.2),  # Air (light white with low opacity)
        }

        # Base color for the current cell type
        base_color = base_colors.get(self.cell_type, (0.0, 0.0, 0.0))  # Default to black if type is unknown

        if self.cell_type == 6:  # Air
            pollution_factor = min(self.pollution_level / 100, 1.0)  # Scale pollution [0, 1]
            # Adjust the base white color to reflect pollution levels
            adjusted_color = tuple(base * (1 - pollution_factor) for base in base_color[:3]) + (base_color[3],)
            return adjusted_color

        # Return the base color for other cell types without adjusting transparency
        if len(base_color) == 3:  # If color doesn't have alpha, add default alpha
            return base_color + (1.0,)
        else:
            return base_color
    
    def get_color_dynamic(self):
        """
        Get the color of the cell based on its type and pollution level.
        Pollution affects the transparency (alpha) of the color.
        """
        base_colors = {
            0: (0.0, 0.0, 1.0),  # Sea (blue)
            1: (1.0, 1.0, 0.0),  # Land (yellow)
            2: (0.5, 0.5, 0.5),  # Cloud (gray)
            3: (0.0, 1.0, 1.0),  # Ice (cyan)
            4: (0.0, 0.5, 0.0),  # Forest (dark green)
            5: (0.5, 0.0, 0.5),  # City (purple)
            6: (1.0, 1.0, 1.0, 0.2),  # Air (light white with low opacity)
        }

        # Base color for the current cell type
        base_color = base_colors.get(self.cell_type, (0.0, 0.0, 0.0))  # Default to black if type is unknown

        if self.cell_type == 6:  # Air
            pollution_factor = min(self.pollution_level / 100, 1.0)  # Scale pollution [0, 1]
            # Adjust the base white color to reflect pollution levels
            adjusted_color = tuple(base * (1 - pollution_factor) for base in base_color[:3]) + (base_color[3],)
            return adjusted_color

        # For all other cell types, apply pollution transparency
        alpha = 1.0 - min(self.pollution_level / 100, 1.0)  # More pollution = lower alpha
        if len(base_color) == 3:  # If color doesn't have alpha, add it
            return base_color + (alpha,)
        else:
            return base_color[:3] + (alpha,)
