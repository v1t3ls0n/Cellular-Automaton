import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Display:
    def __init__(self, simulation):
        self.simulation = simulation
        self.grid_size = simulation.grid_size
        self.day = 0
        self.z_layer = 0  # השכבה הנוכחית

        # יצירת חלון Tkinter
        self.root = tk.Tk()
        self.root.title("Simulation Viewer")

        # מסגרת ראשית להצגת Canvas
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.LEFT)

        # Canvas להצגת מפת הרשת
        self.canvas = tk.Canvas(self.main_frame, width=self.grid_size * 20, height=self.grid_size * 20, bg="white")
        self.canvas.pack()

        # תווית מידע
        self.info_label = tk.Label(self.main_frame, text=f"Day: {self.day}, Z-Layer: {self.z_layer}, Mode: Pollution")
        self.info_label.pack()

        # מסגרת אגדה
        self.legend_frame = tk.Frame(self.root, bg="white")
        self.legend_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # מסגרת לגרפים
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # כפתורי ניווט
        self.root.bind("<Left>", self.previous_day)
        self.root.bind("<Right>", self.next_day)
        self.root.bind("<Up>", self.next_layer)
        self.root.bind("<Down>", self.previous_layer)
        self.root.bind("w", self.show_water_levels)
        self.root.bind("p", self.show_pollution_levels)

        # הוספת אגדה
        self.add_legend()

        # תצוגה ראשונית
        self.update_canvas("pollution")
        self.show_graph()

    def add_legend(self):
        legend_items = [
            ("Blue", "Sea"),
            ("Green", "Land"),
            ("Gray", "Clouds"),
            ("White", "Icebergs"),
            ("Dark Green", "Forests"),
            ("Red", "Cities")
        ]

        title_label = tk.Label(self.legend_frame, text="Legend", font=("Arial", 12, "bold"), bg="white")
        title_label.pack()

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
                cell = state.grid[x, y, self.z_layer]
                if cell.cell_type == 0:  # ים
                    color = "#0000FF"
                elif cell.cell_type == 1:  # יבשה
                    color = "#00FF00"
                elif cell.cell_type == 2:  # עננים
                    color = "#AAAAAA"
                elif cell.cell_type == 3:  # קרחונים
                    color = "#FFFFFF"
                elif cell.cell_type == 4:  # יערות
                    color = "#228B22"
                elif cell.cell_type == 5:  # ערים
                    color = "#FF0000"
                self.canvas.create_rectangle(
                    y * 20, x * 20, (y + 1) * 20, (x + 1) * 20, fill=color
                )
        self.info_label.config(text=f"Day: {self.day}, Z-Layer: {self.z_layer}, Mode: {mode.capitalize()}")

    def show_graph(self):
        # יצירת גרף
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        # חישוב ממוצעי זיהום יומיים
        days = range(len(self.simulation.states))
        avg_pollution = [
            sum(
                cell.pollution_level for x in range(self.grid_size) for y in range(self.grid_size) for z in range(self.grid_size)
                for cell in [state.grid[x, y, z]]
            ) / (self.grid_size ** 3)
            for state in self.simulation.states
        ]

        # ציור הגרף
        ax.plot(days, avg_pollution, label="Average Pollution", color="red")
        ax.set_title("Average Pollution Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Pollution Level")
        ax.legend()

        # שילוב הגרף ב-Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def previous_day(self, event):
        if self.day > 0:
            self.day -= 1
            self.update_canvas("pollution")

    def next_day(self, event):
        if self.day < self.simulation.days - 1:
            self.day += 1
            self.update_canvas("pollution")

    def next_layer(self, event):
        if self.z_layer < self.grid_size - 1:
            self.z_layer += 1
            self.update_canvas("pollution")

    def previous_layer(self, event):
        if self.z_layer > 0:
            self.z_layer -= 1
            self.update_canvas("pollution")

    def show_pollution_levels(self, event=None):
        self.update_canvas("pollution")

    def show_water_levels(self, event=None):
        self.update_canvas("water")

    def run(self):
        self.root.mainloop()
