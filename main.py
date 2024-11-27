import sys
import subprocess
from core.conf import config

# Compile Cython files if requested
if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.precompute(["python", "setup.py", "build_ext",
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
grid_size_input = input(
    "Enter grid size as X,Y,Z (e.g., 10,10,10) (default: 10,10,10): ")

# Handle default and user-provided input
if grid_size_input.strip() == "":
    grid_size = (10, 10, 10)  # Default value
else:
    try:
        # Convert input to a tuple of integers
        grid_size = tuple(map(int, grid_size_input.split(",")))
        if len(grid_size) != 3:
            raise ValueError(
                "You must provide exactly three dimensions (X, Y, Z).")
    except ValueError as e:
        print(f"Invalid input: {e}")
        grid_size = (10, 10, 10)  # Fallback to default

# Print the grid size for confirmation
logging.info(f"Grid Size: {grid_size}")

# Prompt for number of days to track
days = int(
    input("Number Of Days To Track (e.g., 365 = year) (default: 50): ") or 50)
logging.info(f"Number of days to track: {days}")

# Prompt the user for ratios of forests, cities, and deserts
try:
    ratios_input = input(
        "Enter probability for different land cell's type (forest/city/desert - default: 0.3, 0.3, 0.4) : ") or "0.3, 0.3, 0.4"
    if ratios_input.strip() == "":
        # Default ratios
        initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = 0.2, 0.2, 0.2
    else:
        # Convert input to float values
        initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = map(
            float, ratios_input.split(","))
        if round(initial_forests_ratio + initial_cities_ratio + initial_deserts_ratio, 2) != 1.0:
            raise ValueError("The sum of the ratios must equal 1.0.")
except ValueError as e:
    print(f"Invalid input: {e}")
    # Fallback to default ratios
    initial_forests_ratio, initial_cities_ratio, initial_deserts_ratio = 0.2, 0.2, 0.2

# Set the pollution threshold from user input
try:
    config["pollution_threshold"] = float(input("Enter pollution threshold (default: 1.0): ") or 1.0)
    print(f"Pollution threshold set to: {config['pollution_threshold']}")
except ValueError:
    print("Invalid input! Using default value for pollution threshold (1.0).")
    config["pollution_threshold"] = 1.0



# Print the ratios for confirmation
logging.info("Initialized simulation with parameters:")
logging.info(f"Ratios - Forests: {initial_forests_ratio}, Cities: {
             initial_cities_ratio}, Deserts: {initial_deserts_ratio}")
logging.info(f"Pollution Threshold: {config['pollution_threshold']}, Days: {days}, World 3D Grid Dimensions: {grid_size}")

simulation = Simulation(initial_cities_ratio, initial_forests_ratio,
                        initial_deserts_ratio, grid_size, days)

logging.info("Simulation precomputed. Running simulation...")
simulation.precompute()
logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
