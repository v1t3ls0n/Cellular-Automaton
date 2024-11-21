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

def get_user_input(prompt, default, value_type=float):
    """Helper function to get user input with a default value."""
    user_input = input(f"{prompt} (default: {default}): ")
    if user_input.strip() == "":
        return default
    try:
        return value_type(user_input)
    except ValueError:
        print("Invalid input. Using default value.")
        return default

# Collect input from user with improved defaults
print("Please enter the initial parameters for the simulation:")
grid_size = get_user_input("Grid size (e.g., 10)", (10,10,10), int)
days = get_user_input("Number of days to simulate (e.g., 365)", 365, int)
initial_cities = get_user_input("Initial number of cities (e.g., 50)", 450, int)
initial_forests = get_user_input("Initial number of forests (e.g., 50)", 450, int)
initial_pollution = get_user_input("Initial pollution level (e.g., 10.0)", 10.0)
initial_temperature = get_user_input("Initial temperature (e.g., 15.0)", 15.0)
initial_water_mass = get_user_input("Initial water level (e.g., 1.0)", 1.0)

# Initialize simulation with user-provided inputs
simulation = Simulation(
    grid_size=grid_size,
    days=days,
    initial_cities=initial_cities,
    initial_forests=initial_forests,
    initial_pollution=initial_pollution,
    initial_temperature=initial_temperature,
    initial_water_mass=initial_water_mass,
)

# Precompute states
print("Precomputing simulation states...")
simulation.precompute()
print("Precomputation complete.")

# Run the simulation
print("Running simulation...")
simulation.run()
print("Simulation complete.")

# Display the results using Matplotlib
print("Displaying results...")
display = MatplotlibDisplay(simulation)
display.plot_3d()
