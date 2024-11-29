import sys
import subprocess
from core.conf import config, particle_mapping, key_labels
# from core.Simulation import Simulation
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging


# Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(message)s",  # Remove the default logging level prefix
# )


logging.basicConfig(
    filename="simulation.log",
    level=logging.DEBUG,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    # datefmt="%Y-%m-%d %H:%M:%S",
)





logging.info("Simulation started.")

# Compile Cython files if requested
if "--compile" in sys.argv:
    print("Compiling Cython files...")
    subprocess.run(["python", "setup.py", "build_ext", "--inplace"], cwd="core", check=True)
    print("Compilation complete.")


# Function to get user input for all configuration parameters
def get_user_configuration():
    """Prompt user for all configuration parameters or use defaults."""
    user_config = {}

    print("\n--- Simulation Configuration ---")
    print("1. Use Default Parameters")
    print("2. Set Custom Parameters")
    
    choice = input("Choose an option (1 or 2): ").strip()
    if choice == "1":
        # Use default configuration
        print("Using default configuration.")
        user_config = config.copy()
    elif choice == "2":
        # Custom configuration
        print("Setting custom configuration...")
        for key, value in config.items():
            if key == "base_colors":
                continue
            label = key_labels.get(key, key)  # Get descriptive label if available
            if isinstance(value, dict):
                print(f"\n{label}:")
                user_config[key] = {}
                for sub_key, sub_value in value.items():
                    particle_label = particle_mapping.get(sub_key, sub_key)
                    input_value = input(f"Enter value for {particle_label} (default: {sub_value}): ").strip()
                    user_config[key][sub_key] = float(input_value) if input_value else sub_value
            elif isinstance(value, list):
                print(f"\n{label} (list values):")
                user_config[key] = []
                for i, v in enumerate(value):
                    particle_label = particle_mapping.get(i, i)
                    input_value = input(f"Enter value for {particle_label} (default: {v}): ").strip()
                    user_config[key].append(float(input_value) if input_value else v)
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                if isinstance(value, int):
                    user_config[key] = int(input_value) if input_value else value
                elif isinstance(value, float):
                    user_config[key] = float(input_value) if input_value else value
                else:
                    user_config[key] = input_value if input_value else value
    else:
        print("Invalid choice. Using default configuration.")
        user_config = config.copy()

    return user_config


# Main execution
if __name__ == "__main__":
    # Prompt user for configuration
    user_config = get_user_configuration()

    # Extract essential parameters for simulation
    grid_size = tuple(user_config.get("default_grid_size", (10, 10, 10)))
    days = user_config.get("default_days", 10)
    initial_ratios = user_config.get("initial_ratios", {"forest": 0.3, "city": 0.3, "desert": 0.3, "vacuum": 0.1})

    # Validate initial ratios
    if round(sum(initial_ratios.values()), 2) != 1.0:
        print("Initial ratios must sum to 1. Adjusting to default ratios.")
        initial_ratios = config["initial_ratios"]

    # Set updated configuration
    config.update(user_config)

    # Initialize and run simulation
    simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
    logging.info("Starting simulation...")
    simulation.precompute()
    logging.info("Simulation complete. Displaying results...")
    display = MatplotlibDisplay(simulation)
    display.plot_3d()