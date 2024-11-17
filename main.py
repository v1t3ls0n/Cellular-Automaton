from core import Simulation
from display import Display, GraphDisplay

sim = Simulation(grid_size=10, days=365)
display = Display(sim)
graph_display = GraphDisplay(sim)

sim.run()
display.run()
graph_display.plot_average_pollution()