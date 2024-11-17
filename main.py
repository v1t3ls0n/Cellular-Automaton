from core import Simulation
from display import MatplotlibDisplay, GraphDisplay

# יצירת סימולציה
sim = Simulation(grid_size=10, days=365)
sim.run()

# תצוגת Matplotlib (תלת-ממדית)
matplotlib_display = MatplotlibDisplay(sim)
matplotlib_display.plot_3d()

metrics = GraphDisplay(sim)
metrics.plot_average_pollution()
