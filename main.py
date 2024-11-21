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

days =int(input("Number Of Days To Track (e.g., 365 = year) (default: 5): ") or 20)
initial_pollution = float(input("Initial pollution level (e.g., 10.0) (default: 30.0): ") or 2)
initial_temperature = float(input("Initial temperature (e.g., 15.0) (default: 25.0): ") or 15.0)
initial_water_mass = float(input("Initial water level (e.g., 1.0) (default: 1.0): ") or 1.0)
initial_cities = int(input("Initial number of cities (e.g., 50) (default: 50): ") or 500)
initial_forests = int(input("Initial number of forests (e.g., 50) (default: 50): ") or 800)
grid_size = (10,10,10)

simulation = Simulation(
    grid_size=grid_size,
    days=days,
    initial_pollution=initial_pollution,
    initial_temperature=initial_temperature,
    initial_water_mass=initial_water_mass,
    initial_cities=initial_cities,
    initial_forests=initial_forests
)






# logging.info("Initialized simulation with parameters: %s", simulation.__dict__)
# simulation.precompute()

# logging.info("Simulation precomputed. Running simulation...")
simulation.run()
simulation._calculate_aggregates()  # Compute aggregates for analysis


# logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
