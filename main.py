from core import Simulation
from display import Display, GraphDisplay

sim = Simulation(grid_size=10, days=365)
display = Display(sim)
graph_display = GraphDisplay(sim)

# יצירת סימולציה
sim = Simulation(grid_size=10, days=365)
# הרצת הסימולציה
sim.run()

# הצגת התוצאות
display = Display(sim)
display.run()


graph_display = GraphDisplay(sim)
graph_display.plot_average_pollution()