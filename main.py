from Simulation import Simulation
from Display import Display
from GraphDisplay import GraphDisplay

# יצירת סימולציה
sim = Simulation(grid_size=10, days=365)

# הרצת הסימולציה
sim.run()

# הצגת התוצאות
display = Display(sim)
display.run()
