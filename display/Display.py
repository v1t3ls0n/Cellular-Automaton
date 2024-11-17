import tkinter as tk

class Display:
    def __init__(self, simulation):
        self.simulation = simulation
        self.grid_size = simulation.grid_size
        self.day = 0

        # יצירת החלון הראשי
        self.root = tk.Tk()
        self.root.title("Simulation Viewer")

        # יצירת מסגרת ראשית
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT)

        # Canvas להצגת הסימולציה
        self.canvas = tk.Canvas(self.main_frame, width=self.grid_size * 20, height=self.grid_size * 20, bg="white")
        self.canvas.pack()

        # תווית למידע
        self.info_label = tk.Label(self.main_frame, text=f"Day: {self.day}, Mode: Pollution")
        self.info_label.pack()

        # מסגרת לצד הצבעים
        self.legend_frame = tk.Frame(self.root, bg="white")
        self.legend_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # כפתורי ניווט
        self.root.bind("<Left>", self.previous_day)
        self.root.bind("<Right>", self.next_day)
        self.root.bind("w", self.show_water_levels)
        self.root.bind("p", self.show_pollution_levels)

        # הוספת אגדה לצבעים
        self.add_legend()

        # תצוגה ראשונית
        self.update_canvas("pollution")

    def add_legend(self):
        # רשימת הצבעים והתיאורים
        legend_items = [
            ("Blue", "Sea"),
            ("Green", "Land"),
            ("Gray", "Clouds"),
            ("White", "Icebergs"),
            ("Dark Green", "Forests"),
            ("Red", "Cities")
        ]

        # יצירת כותרת למסגרת
        title_label = tk.Label(self.legend_frame, text="Legend", font=("Arial", 12, "bold"), bg="white")
        title_label.pack()

        # יצירת תווית לכל פריט באגדה
        for color, description in legend_items:
            frame = tk.Frame(self.legend_frame, bg="white")
            frame.pack(anchor="w", pady=2)

            color_box = tk.Canvas(frame, width=20, height=20, bg=color.lower(), highlightthickness=0)
            color_box.pack(side=tk.LEFT, padx=5)

            text_label = tk.Label(frame, text=description, font=("Arial", 10), bg="white")
            text_label.pack(side=tk.LEFT)

    def update_canvas(self, mode):
        self.canvas.delete("all")
        state = self.simulation.get_state(self.day)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                cell = state.grid[x, y, 0]
                if cell.cell_type == 0:  # ים
                    color = "#0000FF"  # כחול
                elif cell.cell_type == 1:  # יבשה
                    color = "#00FF00"  # ירוק
                elif cell.cell_type == 2:  # עננים
                    color = "#AAAAAA"  # אפור
                elif cell.cell_type == 3:  # קרחונים
                    color = "#FFFFFF"  # לבן
                elif cell.cell_type == 4:  # יערות
                    color = "#228B22"  # ירוק כהה
                elif cell.cell_type == 5:  # ערים
                    color = "#FF0000"  # אדום
                self.canvas.create_rectangle(
                    y * 20, x * 20, (y + 1) * 20, (x + 1) * 20, fill=color
                )
        self.info_label.config(text=f"Day: {self.day}, Mode: {mode.capitalize()}")

    def previous_day(self, event):
        if self.day > 0:
            self.day -= 1
            self.update_canvas("pollution")

    def next_day(self, event):
        if self.day < self.simulation.days - 1:
            self.day += 1
            self.update_canvas("pollution")

    def show_pollution_levels(self, event=None):
        self.update_canvas("pollution")

    def show_water_levels(self, event=None):
        self.update_canvas("water")

    def run(self):
        self.root.mainloop()
