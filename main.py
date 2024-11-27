import sys
import subprocess

# Compile Cython files if requested
if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.run(["python", "setup.py", "build_ext",
                   "--inplace"], cwd="core", check=True)
    print("Compilation complete.")

# Import the updated simulation and display classes
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging

import logging

# Set up logging
# Configure logging
logging.basicConfig(
    filename='simulation.log',    # Name of the log file
    level=logging.INFO,           # Minimum log level to write to the file
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'   # Date and time format
)
logging.info("Simulation started.")

# Prompt the user for grid size
grid_size_input = input("Enter grid size as X,Y,Z (e.g., 10,10,10) (default: 10,10,10): ")

# Handle default and user-provided input
if grid_size_input.strip() == "":
    grid_size = (10, 10, 10)  # Default value
else:
    try:
        # Convert input to a tuple of integers
        grid_size = tuple(map(int, grid_size_input.split(",")))
        if len(grid_size) != 3:
            raise ValueError("You must provide exactly three dimensions (X, Y, Z).")
    except ValueError as e:
        print(f"Invalid input: {e}")
        grid_size = (10, 10, 10)  # Fallback to default

# Print the grid size for confirmation
logging.info(f"Grid Size: {grid_size}")

# Prompt for number of days to track
days = int(input("Number Of Days To Track (e.g., 365 = year) (default: 50): ") or 50)
logging.info(f"Number of days to track: {days}")

# Prompt the user for ratios of forests, cities, and deserts
try:
    ratios_input = input("Enter ratios for forests, cities, and deserts as F,C,D (e.g., 0.3,0.3,0.4) (default: 0.2, 0.2, 0.2): ")
    if ratios_input.strip() == "":
        initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = 0.2, 0.2, 0.2  # Default ratios
    else:
        # Convert input to float values
        initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = map(float, ratios_input.split(","))
        if round(initial_forests_ratio + initial_cities_ratio + initial_deserts_ratio, 2) != 1.0:
            raise ValueError("The sum of the ratios must equal 1.0.")
except ValueError as e:
    print(f"Invalid input: {e}")
    initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = 0.2, 0.2, 0.2  # Fallback to default ratios

# Print the ratios for confirmation
logging.info(f"Ratios - Forests: {initial_forests_ratio}, Cities: {initial_cities_ratio}, Deserts: {initial_deserts_ratio}")

# The rest of the initialization logic follows here...
# For example:

simulation = Simulation(initial_cities_ratio,initial_forests_ratio,initial_deserts_ratio,grid_size,days)


# logging.info("Initialized simulation with parameters: %s", simulation.__dict__)
# simulation.precompute()

# logging.info("Simulation precomputed. Running simulation...")
simulation.run()

# logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
