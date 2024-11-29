import sys
import subprocess
from core.conf import config
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging

# Set up logging
logging.basicConfig(
    # filename="simulation.log",
    # level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    # datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Simulation started.")

# Compile Cython files if requested
if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.run(["python", "setup.py", "build_ext", "--inplace"], cwd="core", check=True)
    print("Compilation complete.")

# Prompt for grid size
default_grid_size = config.get("default_grid_size", (10, 10, 10))
grid_size_input = input(f"Enter grid size as X,Y,Z (default: {default_grid_size}): ").strip()
try:
    grid_size = (
        tuple(map(int, grid_size_input.split(",")))
        if grid_size_input
        else default_grid_size
    )
    if len(grid_size) != 3:
        raise ValueError("You must provide exactly three dimensions (X, Y, Z).")
except ValueError as e:
    print(f"Invalid input for grid size: {e}. Using default: {default_grid_size}")
    grid_size = default_grid_size
logging.info(f"Grid size: {grid_size}")

# Prompt for number of days
default_days = config.get("default_days", 50)
try:
    days = int(input(f"Enter number of days to track (default: {default_days}): ").strip() or default_days)
except ValueError:
    print(f"Invalid input for days. Using default: {default_days}")
    days = default_days
logging.info(f"Number of days to track: {days}")

# Prompt for initial ratios
default_ratios = config.get("initial_ratios", {"forest": 0.3, "city": 0.3, "desert": 0.3, "vacuum": 0.1})
try:
    ratios_input = input(
        f"Enter ratios for forest, city, desert, vacuum (default: {list(default_ratios.values())}): "
    ).strip()
    if ratios_input:
        forest_ratio, city_ratio, desert_ratio, vacuum_ratio = map(float, ratios_input.split(","))
        if round(forest_ratio + city_ratio + desert_ratio + vacuum_ratio, 2) != 1.0:
            raise ValueError("The ratios must sum to 1.0.")
    else:
        forest_ratio, city_ratio, desert_ratio, vacuum_ratio = default_ratios.values()
    initial_ratios = {
        "forest": forest_ratio,
        "city": city_ratio,
        "desert": desert_ratio,
        "vacuum": vacuum_ratio,
    }
except ValueError as e:
    print(f"Invalid input for ratios: {e}. Using default: {default_ratios}")
    initial_ratios = default_ratios
logging.info(f"Initial ratios: {initial_ratios}")

# Prompt for pollution threshold
default_pollution_threshold = config.get("pollution_damage_threshold", 1.0)
try:
    pollution_threshold = float(
        input(f"Enter pollution threshold (default: {default_pollution_threshold}): ").strip()
        or default_pollution_threshold
    )
except ValueError:
    print(f"Invalid input for pollution threshold. Using default: {default_pollution_threshold}")
    pollution_threshold = default_pollution_threshold
config["pollution_damage_threshold"] = pollution_threshold
logging.info(f"Pollution threshold: {pollution_threshold}")

# Initialize and run simulation
simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
logging.info("Starting simulation...")
simulation.precompute()
logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
