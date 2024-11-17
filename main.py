import sys
import subprocess

if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.run(["python", "setup.py", "build_ext", "--inplace"], cwd="core", check=True)
    print("Compilation complete.")

# Import and run the main simulation code
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay

simulation = Simulation(grid_size=10, days=365)
simulation.run()

display = MatplotlibDisplay(simulation)
display.plot_3d()
