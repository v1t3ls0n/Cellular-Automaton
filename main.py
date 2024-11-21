import sys
import subprocess

# Compile Cython files if requested
if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.run(["python", "setup.py", "build_ext", "--inplace"], cwd="core", check=True)
    print("Compilation complete.")

# Import the updated simulation and display classes
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging

# Configure logging
logging.basicConfig(
    filename="simulation.log", 
    filemode="w", 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)

logging.info("Simulation started.")

# Initialize and run the simulation
simulation = Simulation(
    grid_size=(10, 10, 10),
    days=365,
    initial_pollution=10.0,
    initial_temperature=15.0,
    initial_water_mass=1.0,
    initial_cities=50,
    initial_forests=50
)

logging.info("Initialized simulation with parameters: %s", simulation.__dict__)
simulation.precompute()

logging.info("Simulation precomputed. Running simulation...")
simulation.run()

logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
