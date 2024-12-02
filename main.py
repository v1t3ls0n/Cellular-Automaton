import os
import logging
from core.conf import update_config, get_config,validate_config
from utils.constants import PRESET_CONFIGS, PARTICLE_MAPPING, KEY_LABELS
from display.MatplotlibDisplay import MatplotlibDisplay
from core.Simulation import Simulation

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    filename="simulation.log",
    filemode="w",  # Overwrite the file each time
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)



def choose_preset():
    """
    Allow the user to choose a configuration preset from a list.
    """
    print("Available Configuration Presets:")
    for i, preset_name in enumerate(PRESET_CONFIGS.keys(), 1):
        print(f"{i}. {preset_name}")

    while True:
        try:
            choice = int(input("Enter the number of your chosen preset: "))
            if 1 <= choice <= len(PRESET_CONFIGS):
                chosen_preset = list(PRESET_CONFIGS.keys())[choice - 1]
                print(f"Selected preset: {chosen_preset}")
                return chosen_preset
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def parse_grid_size(input_value):
    """
    Parse the grid size from a string or list.
    """
    if isinstance(input_value, str):
        return tuple(int(value) for value in input_value.replace(",", " ").split())
    elif isinstance(input_value, (list, tuple)):
        return tuple(int(value) for value in input_value)
    else:
        raise ValueError("Invalid grid size format. Provide a list, tuple, or string.")

def parse_boolean(input_value):
    """
    Parse boolean input from strings like "true" or "false".
    """
    if isinstance(input_value, str):
        if input_value.lower() in {"true", "yes", "1"}:
            return True
        elif input_value.lower() in {"false", "no", "0"}:
            return False
    return input_value

def parse_input_value(input_value, default_value):
    """
    Parse the input value based on the type of the default value.
    """
    if not input_value:
        return default_value

    boolean_value = parse_boolean(input_value)
    if isinstance(boolean_value, bool):
        return boolean_value

    try:
        if isinstance(default_value, float):
            return float(input_value)
        if isinstance(default_value, int):
            return int(input_value)
    except ValueError:
        pass

    return input_value

def get_user_configuration():
    """
    Prompt user for all configuration parameters or use presets.
    """
    print("\n--- Simulation Configuration ---")
    print("1. Use Default Configuration Presets")
    print("2. Set Custom Parameters")

    choice = input("Choose an option (1 or 2): ").strip()
    if choice != "2":

        if choice != "1":
            print(f"Invalid choice. Using default configuration.\n")

        preset_name = choose_preset()
        update_config(preset_name=preset_name)
    else:
        user_config = {}
        print("Setting custom configuration...")
        for key, value in config.items():
            if key == "base_colors":
                continue
            label = KEY_LABELS.get(key, key)
            if isinstance(value, dict):
                user_config[key] = {}
                print(f"\n{label}:")
                for sub_key, sub_value in value.items():
                    particle_label = PARTICLE_MAPPING.get(sub_key, sub_key)
                    input_value = input(f"Enter value for {particle_label} (default: {sub_value}): ").strip()
                    user_config[key][sub_key] = parse_input_value(input_value, sub_value)
            elif isinstance(value, list):
                user_config[key] = []
                print(f"\n{label} (list values):")
                for i, v in enumerate(value):
                    particle_label = PARTICLE_MAPPING.get(i, i)
                    input_value = input(f"Enter value for {particle_label} (default: {v}): ").strip()
                    user_config[key].append(parse_input_value(input_value, v))
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                user_config[key] = parse_input_value(input_value, value)
        
        update_config(custom_config=user_config)


# Main execution
if __name__ == "__main__":
    get_user_configuration()
    config = get_config()
    try:
        validate_config(config)
        print("Configuration is valid.")
            # Extract essential parameters for simulation
        grid_size = parse_grid_size(config["grid_size"])
        days = config["days"]
        initial_ratios = config["initial_ratios"]

        if round(sum(initial_ratios.values()), 2) != 1.0:
            print("Initial ratios must sum to 1. Adjusting to default ratios.")
            initial_ratios = config["initial_ratios"]

        # Initialize and run simulation
        simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
        logging.info("Starting simulation...")
        simulation.precompute()
        logging.info("Simulation complete. Displaying results...")
        display = MatplotlibDisplay(simulation)
        display.plot_3d()

    except (KeyError, TypeError) as e:
        print(f"Configuration error: {e}")
        exit(1)

