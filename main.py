from core import Simulation
from display import Display,MatplotlibDisplay

# יצירת סימולציה
sim = Simulation(grid_size=10, days=365)
sim.run()

# תצוגת Tkinter (דו-ממדית)
display = Display(sim)
display.run()

# תצוגת Matplotlib (תלת-ממדית)
matplotlib_display = MatplotlibDisplay(sim)
matplotlib_display.plot_3d()
