import logging
from sys import exit
from config.Config import config_instance
from config.presets import PRESET_CONFIGS, DEFAULT_PRESET, PARTICLE_MAPPING, KEY_LABELS
from display.MatplotlibDisplay import MatplotlibDisplay
from core.Simulation import Simulation

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File handler for logging DEBUG and above
file_handler = logging.FileHandler(
    "simulation.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Console handler for logging INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def parse_grid_size(input_value):
    """
    Parse the grid size from a string into a tuple of integers.
    Supports both comma-separated and space-separated strings.
    """
    try:
        # Replace spaces with commas and split by commas
        return tuple(int(value.strip()) for value in input_value.replace(" ", ",").split(","))
    except ValueError:
        raise ValueError(
            "Invalid grid size format. Please provide integers separated by commas or spaces.")

def collect_user_input():
    """
    Collect user input for all configuration parameters, including grid size, days, and others.
    """
    logging.info("Prompting user for grid size and simulation days.")

    # Access the shared config instance
    config = config_instance.get()

    # Get user input for grid size
    default_grid_size = config["grid_size"]
    grid_size_input = input(f"Enter grid size as comma-separated integers (default: {default_grid_size}): ").strip()
    grid_size = parse_grid_size(grid_size_input) if grid_size_input else default_grid_size

    # Get user input for number of days
    default_days = config["days"]
    days_input = input(f"Enter number of days for the simulation (default: {default_days}): ").strip()
    days = int(days_input) if days_input.isdigit() and int(days_input) > 0 else default_days

    # Prompt for preset or custom configuration
    print("\n--- Simulation Configuration ---")
    print("1. Use Default Configuration Preset")
    print("2. Choose Configuration Preset")
    print("3. Customize Additional Parameters")

    choice = input("Choose an option (1, 2, 3): ").strip()

    if choice == "2":
        preset_name = choose_preset()
        logging.info(f"User selected preset: {preset_name}.")
        config_instance.update(preset_name=preset_name)  # Apply the preset
    elif choice == "3":
        logging.info("Setting custom configuration...")
        updated_config = config.copy()
        for key, value in config.items():
            if key in {"grid_size", "days"}:
                continue  # Skip as these are already handled

            label = KEY_LABELS.get(key, key)
            if isinstance(value, dict):
                updated_config[key] = {}
                print(f"\n{label}:")
                for sub_key, sub_value in value.items():
                    if sub_key in {0,1,2,3,4,5,6,7,8}:
                        input_value = input(f"Enter value for {PARTICLE_MAPPING[sub_key]} (default: {sub_value}): ").strip()
                        updated_config[key][sub_key] = parse_input_value(input_value, sub_value)
                    else:
                        input_value = input(f"Enter value for {sub_key} (default: {sub_value}): ").strip()
                        updated_config[key][sub_key] = parse_input_value(input_value, sub_value)    
                print()
            elif isinstance(value, list):
                print(f"\n{label}:")
                for sub_key, sub_value in enumerate(value):
                    input_value = input(f"Enter value for {PARTICLE_MAPPING[sub_key]} (default: {sub_value}): ").strip()
                    updated_config[key][sub_key] = parse_input_value(input_value, sub_value)
                print()
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                updated_config[key] = parse_input_value(input_value, value)
        config_instance.update(custom_config=updated_config)
    elif choice == "1":
        logging.info("User chose default configuration preset.")
    else:
        logging.info("Invalid choice from user. Using default configuration preset.")

    # Override grid size and days with user input
    config_instance.update(custom_config={"grid_size": grid_size, "days": days})

    return config_instance.get()

def parse_input_value(input_value, default_value):
    """
    Parse the input value based on the type of the default value.
    All inputs are initially strings; this function converts them to the correct type.
    """
    if not input_value:  # If input is empty, return the default value
        return default_value

    try:
        # Convert based on the type of the default value
        if isinstance(default_value, bool):
            return input_value.lower() in {"true", "yes", "1"}
        if isinstance(default_value, int):
            return int(input_value)  # Convert to integer
        if isinstance(default_value, float):
            return float(input_value)  # Convert to float
    except ValueError:
        logging.info(f"Could not parse input value '{input_value}' for type {type(default_value).__name__}. Using default: {default_value}")

    return default_value

def choose_preset():
    """
    Allow the user to choose a configuration preset from a list.
    """
    logging.info("Displaying configuration presets for user.")
    print("\nAvailable Configuration Presets:")
    for i, preset_name in enumerate(PRESET_CONFIGS.keys(), 1):
        print(f"{i}. {preset_name}")

    while True:
        try:
            choice = int(input("Enter the number of your chosen preset: "))
            if 1 <= choice <= len(PRESET_CONFIGS):
                return list(PRESET_CONFIGS.keys())[choice - 1]
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    try:
        logging.info("\nCellular Automaton is Running\n")

        # Collect user inputs and update configuration
        config = collect_user_input()
        config_instance.finalize()  # Finalize configuration to make it immutable
        config_instance.log_full_configuration()

        # Extract essential parameters for simulation
        grid_size = config["grid_size"]
        days = config["days"]
        initial_ratios = config.get("initial_ratios", {})

        if round(sum(initial_ratios.values()), 2) != 1.0:
            logging.info("Initial ratios do not sum to 1. Adjusting to default ratios.")
            initial_ratios = DEFAULT_PRESET["initial_ratios"]

        # Initialize and run simulation
        simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
        logging.info("Starting simulation...")
        simulation.precompute()
        logging.info("Simulation complete. Displaying results.")

        display = MatplotlibDisplay(simulation)
        display.render_graphic_user_interface()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        input("Press Enter to exit...")
        exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        input("Press Enter to exit...")
        exit(1)