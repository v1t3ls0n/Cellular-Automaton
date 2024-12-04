import logging
from config.config_state_handler import update_config, get_config, validate_config, finalize_config
from config.conf_presets import PRESET_CONFIGS, DEFAULT_PRESET, PARTICLE_MAPPING, KEY_LABELS
from display.MatplotlibDisplay import MatplotlibDisplay
from core.Simulation import Simulation

# Configure logging
# Configure the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the lowest level you want to log (DEBUG in this case)

# Create a file handler for logging all messages (DEBUG and above)
file_handler = logging.FileHandler("simulation.log")
file_handler.setLevel(logging.INFO)  # Logs everything to the file

# Create a console handler for logging only INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Logs only INFO and above to the console

# Create a formatter for both handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Attach the formatter to the handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example usage
logger.debug("This is a DEBUG message (file only)")
logger.info("This is an INFO message (console and file)")
logger.warning("This is a WARNING message (console and file)")
logger.error("This is an ERROR message (console and file)")
logger.critical("This is a CRITICAL message (console and file)")

def parse_grid_size(input_value):
    """
    Parse the grid size from a string or list into a tuple.
    """
    if isinstance(input_value, str):
        try:
            return tuple(int(value.strip()) for value in input_value.split(","))
        except ValueError:
            raise ValueError("Invalid grid size format. Please provide integers separated by commas.")
    elif isinstance(input_value, (list, tuple)):
        return tuple(int(value) for value in input_value)
    else:
        raise ValueError("Invalid grid size format. Provide a list, tuple, or string.")

def choose_preset():
    """
    Allow the user to choose a configuration preset from a list.
    """
    logging.info("Displaying configuration presets for user.")
    print("Available Configuration Presets:")
    for i, preset_name in enumerate(PRESET_CONFIGS.keys(), 1):
        print(f"{i}. {preset_name}")

    limit_bad_input = 10
    while limit_bad_input > 0:
        try:
            choice = int(input("Enter the number of your chosen preset: "))
            if 1 <= choice <= len(PRESET_CONFIGS):
                chosen_preset = list(PRESET_CONFIGS.keys())[choice - 1]
                print(f"Selected preset: {chosen_preset}")
                logging.info(f"User selected preset: {chosen_preset}")
                return chosen_preset
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            logging.warning("Invalid input. User did not enter a number.")
            print("Invalid input. Please enter a number.")
        limit_bad_input -= 1

    logging.warning("User exceeded invalid input attempts. Default preset selected.")
    print("Too many invalid attempts. Using default preset.")
    return DEFAULT_PRESET

def parse_input_value(input_value, default_value):
    """
    Parse the input value based on the type of the default value.
    """
    if not input_value:
        return default_value

    try:
        if isinstance(default_value, bool):
            return input_value.lower() in {"true", "yes", "1"} if isinstance(input_value, str) else bool(input_value)
        if isinstance(default_value, int):
            return int(input_value)
        if isinstance(default_value, float):
            return float(input_value)
    except ValueError:
        logging.warning(f"Could not parse input value: {input_value}")

    return input_value

def parse_user_input():
    """
    Prompt user for configuration parameters or use presets.
    """
    logging.info("Prompting user for configuration options.")
    print("\n--- Simulation Configuration ---")
    print("1. Go with Default Configuration Preset")
    print("2. Choose Configuration Presets")
    print("3. Customize Parameters")

    choice = input("Choose an option (1, 2, 3): ").strip()
    if choice == "2":
        update_config(preset_name=choose_preset())
    elif choice == "3":
        user_config = {}
        print("Setting custom configuration...")
        for key, value in DEFAULT_PRESET.items():
            label = KEY_LABELS.get(key, key)

            if key == "grid_size":
                # Special parsing for grid_size to convert it into a tuple
                input_value = input(f"Enter value for {label} as comma-separated integers (default: {value}): ").strip()
                if input_value:
                    try:
                        user_config[key] = parse_grid_size(input_value)
                    except ValueError as e:
                        logging.warning(f"Invalid grid_size input: {e}")
                        print(f"Invalid input for {label}. Using default: {value}")
                        user_config[key] = value
                else:
                    user_config[key] = value
            elif isinstance(value, dict):
                user_config[key] = {}
                print(f"\n{label}:")
                for sub_key, sub_value in value.items():
                    input_value = input(f"Enter value for {sub_key} (default: {sub_value}): ").strip()
                    user_config[key][sub_key] = parse_input_value(input_value, sub_value)
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                user_config[key] = parse_input_value(input_value, value)

        update_config(custom_config=user_config)
    elif choice == "1":
        logging.info("User chose default configuration preset.")
        update_config(custom_config=DEFAULT_PRESET)
    else:
        logging.warning("Invalid choice from user. Default configuration used.")
        print("Invalid choice. Using default configuration.")
        update_config(custom_config=DEFAULT_PRESET)

def parse_grid_size(input_value):
    """
    Parse the grid size from a string into a tuple of integers.
    """
    if isinstance(input_value, str):
        try:
            return tuple(int(value.strip()) for value in input_value.split(","))
        except ValueError:
            raise ValueError("Invalid grid size format. Please provide integers separated by commas.")
    elif isinstance(input_value, (list, tuple)):
        return tuple(int(value) for value in input_value)
    else:
        raise ValueError("Invalid grid size format. Provide a string, list, or tuple.")

# Main Execution
if __name__ == "__main__":
    try:
        logging.info("Starting the Cellular Automaton Simulation.")

        parse_user_input()
        config = get_config()
        validate_config(config)
        finalize_config()

        # Extract essential parameters for simulation
        grid_size = config.get("grid_size", (10, 10, 10))
        days = config.get("days", 100)
        initial_ratios = config.get("initial_ratios", {})

        if round(sum(initial_ratios.values()), 2) != 1.0:
            logging.warning("Initial ratios do not sum to 1. Adjusting to default ratios.")
            initial_ratios = DEFAULT_PRESET["initial_ratios"]

        # Initialize and run simulation
        simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
        logging.info("Starting simulation...")
        simulation.precompute()
        logging.info("Simulation complete. Displaying results.")

        display = MatplotlibDisplay(simulation)
        display.render_graphic_user_interface()

        if get_config() != config:
            logging.error("Configuration was updated during simulation.")
            raise ValueError("Configuration mismatch detected.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
        exit(1)
