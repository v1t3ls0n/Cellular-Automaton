import Simulation
import Display
import GraphDisplay
# יצירת סימולציה
sim = Simulation(grid_size=10, days=365)
display = Display(sim)
graph_display = GraphDisplay(sim)

# הרצת הסימולציה
sim.run()
# הצגת התוצאות
display.run()
# יצירת גרף של זיהום אוויר
graph_display.plot_average_pollution()
