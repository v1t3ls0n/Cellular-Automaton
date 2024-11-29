import sys
import subprocess
from core.conf import config
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging

# Set up logging
logging.basicConfig(
    filename="simulation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Simulation started.")

# Grid size
default_grid_size = config.get("default_grid_size", (10, 10, 10))
grid_size_input = input(f"Enter grid size as X,Y,Z (default: {default_grid_size}): ").strip()
grid_size = tuple(map(int, grid_size_input.split(","))) if grid_size_input else default_grid_size
logging.info(f"Grid Size: {grid_size}")

# Number of days
default_days = config.get("default_days", 50)
days = int(input(f"Number of days to track (default: {default_days}): ").strip() or default_days)
logging.info(f"Days to track: {days}")

# Initial ratios
default_ratios = config.get("initial_ratios", {"forest": 0.3, "city": 0.3, "desert": 0.4})
ratios_input = input(
    f"Enter ratios for forest, city, desert (default: {list(default_ratios.values())}): "
).strip()
if ratios_input:
    forest_ratio, city_ratio, desert_ratio = map(float, ratios_input.split(","))
else:
    forest_ratio, city_ratio, desert_ratio = default_ratios.values()
initial_ratios = {"forest": forest_ratio, "city": city_ratio, "desert": desert_ratio}
logging.info(f"Initial ratios: {initial_ratios}")

# Pollution threshold
default_pollution_threshold = config.get("pollution_damage_threshold", 1.0)
pollution_threshold = float(input(f"Enter pollution threshold (default: {default_pollution_threshold}): ").strip() or default_pollution_threshold)
config["pollution_damage_threshold"] = pollution_threshold
logging.info(f"Pollution threshold: {pollution_threshold}")

# Initialize and run simulation
simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
logging.info("Starting simulation...")
simulation.precompute()
logging.info("Simulation complete. Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
