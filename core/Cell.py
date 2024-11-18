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
        elif self.cell_type == 2:  # Clouds (affected by pollution)
            # Clouds become darker as pollution increases
            pollution_intensity = min(self.pollution_level / 100.0, 1.0)  # Normalize pollution level to [0, 1]
            color_intensity = 1.0 - pollution_intensity  # Higher pollution means darker color
            return (color_intensity, color_intensity, color_intensity, 1.0)  # Grayscale with full opacity

        elif self.cell_type == 3:  # Icebergs
            return "cyan"
        elif self.cell_type == 4:  # Forests
            return "darkgreen"
        elif self.cell_type == 5:  # Cities
            return "pink"  # Solid pink for cities
        else:
            return "white"  # Default to white
        
    def update(self, neighbors, global_forest_count, global_city_count):
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

            # Land may turn back into forest if conditions improve
            if global_forest_count > global_city_count and np.random.random() < 0.05:
                self.cell_type = 4  # Land turns into forest

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
        elif self.cell_type == 3:  # Icebergs
            if self.temperature > 0:
                melting_rate = min(0.1 + self.temperature * 0.002, 0.5)  # Gradual melting
                self.water_level += melting_rate
                if self.water_level > 10:
                    self.cell_type = 0  # Turns into sea
                    for neighbor in neighbors:
                        if neighbor.cell_type == 0:  # Sea cell
                            neighbor.water_level += melting_rate * 0.5
                        if neighbor.cell_type in [1, 5]:  # Land or Cities near Icebergs
                            neighbor.temperature += 0.2  # Regional heating effect


        # Forests absorb pollution but can be deforested
        elif self.cell_type == 4:
            self.pollution_level = max(0, self.pollution_level - 0.5)
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # Rain
                    absorbed_rain = min(0.1, neighbor.water_level)
                    self.water_level += absorbed_rain
                    neighbor.water_level -= absorbed_rain

            if self.pollution_level > 50:
                self.cell_type = np.random.choice([1, 4], p=[0.4, 0.6])  # Forest may turn into land

        elif self.cell_type == 5:  # Cities
            # עלייה מתונה יותר בזיהום, מבוססת על רמת הזיהום הנוכחית
            pollution_increase = 1 / (1 + 0.05 * self.pollution_level)  # גורם מתון
            self.pollution_level = min(self.pollution_level + pollution_increase, 100)  # הגבלת זיהום ל-100

            # עלייה מתונה בטמפרטורה כתוצאה מהזיהום
            self.temperature += 0.01 * self.pollution_level  # עלייה הדרגתית יותר בטמפרטורה

            for neighbor in neighbors:
                # זיהום מתפשט לשכנים בצורה מתונה יותר
                pollution_spread = 0.01 * self.pollution_level / len(neighbors)  # חלק יחסי מהזיהום
                neighbor.pollution_level = min(neighbor.pollution_level + pollution_spread, 100)

                # טיפול במצבי הכחדת יערות ושינוי שטח
                if neighbor.cell_type == 4 and  np.random.random() < 0.02:  # סיכוי נמוך יותר להפיכת יער לאדמה
                    neighbor.cell_type = 1  # יער הופך לאדמה

                # ערים סמוכות למים עם מפלס גבוה
                if neighbor.cell_type == 0 and neighbor.water_level > 5:
                    if np.random.random() < 0.1:  # סיכוי מופחת להרוס עיר במפלס מים גבוה
                        self.cell_type = 0  # עיר הופכת לים

            # אפקט של זיהום גבוה מאוד
            if self.pollution_level > 80 and np.random.random() < 0.3:  # רק אם זיהום קיצוני
                self.cell_type = 1  # עיר הופכת לאדמה בגלל זיהום גבוה
