import tkinter as tk
from tkinter import ttk

class SimulationSettings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulation Settings")

        # משתנים להגדרה
        self.initial_cities = tk.IntVar(value=100)
        self.initial_forests = tk.IntVar(value=200)
        self.initial_pollution = tk.DoubleVar(value=5.0)
        self.initial_temperature = tk.DoubleVar(value=12.0)
        self.initial_water_level = tk.DoubleVar(value=1.0)

        # יצירת ממשק הגדרות
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Initial Number of Cities:").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.initial_cities).grid(row=0, column=1)

        ttk.Label(self.root, text="Initial Number of Forests:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.initial_forests).grid(row=1, column=1)

        ttk.Label(self.root, text="Initial Pollution Level:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.initial_pollution).grid(row=2, column=1)

        ttk.Label(self.root, text="Initial Temperature:").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.initial_temperature).grid(row=3, column=1)

        ttk.Label(self.root, text="Initial Water Level:").grid(row=4, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.initial_water_level).grid(row=4, column=1)

        # כפתור להתחלת הסימולציה
        ttk.Button(self.root, text="Start Simulation", command=self.start_simulation).grid(row=5, column=0, columnspan=2)

    def start_simulation(self):
        # הדפסת ערכים שנבחרו
        print(f"Initial Cities: {self.initial_cities.get()}")
        print(f"Initial Forests: {self.initial_forests.get()}")
        print(f"Initial Pollution: {self.initial_pollution.get()}")
        print(f"Initial Temperature: {self.initial_temperature.get()}")
        print(f"Initial Water Level: {self.initial_water_level.get()}")

        # סגירת החלון
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# הפעלת החלון
if __name__ == "__main__":
    settings = SimulationSettings()
    settings.run()

    # לאחר סגירת החלון, ניתן להשתמש בערכים שנבחרו להרצת הסימולציה
    print("Simulation starting with the selected settings...")
