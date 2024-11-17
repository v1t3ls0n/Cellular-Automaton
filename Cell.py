class Cell:
    def __init__(self, cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level=0):
        self.cell_type = cell_type  # סוג התא: ים, יבשה, עננים, קרחונים, ערים וכו'
        self.temperature = temperature  # טמפרטורה בתא
        self.wind_strength = wind_strength  # עוצמת רוח בתא
        self.wind_direction = wind_direction  # כיוון רוח: וקטור (dx, dy, dz)
        self.pollution_level = pollution_level  # רמת זיהום אוויר בתא
        self.water_level = water_level  # כמות המים בתא (למשל גשם)

    def update(self, neighbors):
        # עדכון זיהום: זיהום אוויר מתפשט לשכנים
        for neighbor in neighbors:
            if neighbor.cell_type != 2:  # לא ענן
                neighbor.pollution_level += self.pollution_level * 0.05

        # זיהום משפיע על טמפרטורה
        self.temperature += self.pollution_level * 0.1

        # חום ממיס קרחונים
        if self.cell_type == 3 and self.temperature > 0:  # סוג "קרחון"
            self.water_level += 1  # הקרחון נמס
            self.cell_type = 1 if self.water_level > 10 else self.cell_type  # קרחון הופך לים

        # גשם מהעננים
        if self.cell_type == 2 and self.temperature < 0 and self.wind_strength > 5:
            self.water_level += 5  # גשם מתווסף
