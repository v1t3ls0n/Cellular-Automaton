class Cell:
    def __init__(self, cell_type, temperature, wind_strength, wind_direction, pollution_level, water_level=0):
        self.cell_type = cell_type  # סוג התא: ים, יבשה, עננים, קרחונים, יערות, ערים
        self.temperature = temperature  # טמפרטורה
        self.wind_strength = wind_strength  # עוצמת רוח
        self.wind_direction = wind_direction  # כיוון רוח
        self.pollution_level = pollution_level  # רמת זיהום
        self.water_level = water_level  # מפלס מים (למשל, לים, קרחונים, או גשם בעננים)

    def update(self, neighbors):
        # **ים**
        if self.cell_type == 0:  # ים
            return  # ים אינו משתנה

        # **יבשה**
        if self.cell_type == 1:  # יבשה
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # גשם
                    self.water_level += neighbor.water_level * 0.1
                    neighbor.water_level -= neighbor.water_level * 0.1
            if self.temperature > 35:  # התייבשות
                self.water_level = max(0, self.water_level - 0.5)

        # **עננים**
        if self.cell_type == 2:  # עננים
            if self.water_level > 0:
                for neighbor in neighbors:
                    if neighbor.cell_type in [0, 1]:  # גשם יורד על ים או יבשה
                        neighbor.water_level += self.water_level * 0.2
                        self.water_level -= self.water_level * 0.2

        # **קרחונים**
        if self.cell_type == 3:  # קרחונים
            if self.temperature > 0:
                self.water_level += 1
                if self.water_level > 10:
                    self.cell_type = 0  # הופך לים

        # **יערות**
        if self.cell_type == 4:  # יערות
            self.pollution_level = max(0, self.pollution_level - 0.5)  # הפחתת זיהום סמוך
            for neighbor in neighbors:
                if neighbor.cell_type == 2 and neighbor.water_level > 0:  # גשם
                    neighbor.water_level -= 0.1  # היער "שואב" מים מגשם

        # **ערים**
        if self.cell_type == 5:  # ערים
            self.pollution_level += 1  # ייצור זיהום
            for neighbor in neighbors:
                neighbor.pollution_level += self.pollution_level * 0.05  # זיהום מתפשט
            if self.water_level > 5:  # שיטפון
                self.pollution_level += 5
