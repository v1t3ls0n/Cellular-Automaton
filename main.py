import logging
from sys import exit
from config.config_state_handler import update_config, get_config, validate_config, finalize_config
from config.conf_presets import PRESET_CONFIGS, DEFAULT_PRESET, PARTICLE_MAPPING, KEY_LABELS
from display.MatplotlibDisplay import MatplotlibDisplay
from core.Simulation import Simulation

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler for logging DEBUG and above
file_handler = logging.FileHandler("simulation.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Console handler for logging INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def parse_grid_size(input_value, default_value):
    """
    Parse the grid size from a string into a tuple of integers.
    Fallbacks to default value if parsing fails.
    """
    if isinstance(input_value, str):
        try:
            # Replace spaces with commas and split by commas
            return tuple(int(value.strip()) for value in input_value.replace(" ", ",").split(","))
        except ValueError:
            logging.warning(f"Invalid grid size input: {input_value}. Falling back to default value: {default_value}.")
            return default_value
    elif isinstance(input_value, (list, tuple)):
        return tuple(int(value) for value in input_value)
    else:
        logging.warning(f"Invalid grid size input type. Falling back to default value: {default_value}.")
        return default_value


def collect_user_input():
    """
    Collect user input for all configuration parameters, including grid size, days, and others.
    Configuration is updated only once at the end.
    """
    # logging.info("Prompting user for grid size and simulation days.")

    # Collect initial configuration
    user_config = {}

    # Get grid size
    default_grid_size = DEFAULT_PRESET.get("grid_size", (10, 10, 10))
    grid_size_input = input(f"Enter grid size as comma-separated integers (default: {default_grid_size}): ").strip()
    user_config["grid_size"] = parse_grid_size(grid_size_input, default_grid_size)

    # Get number of days
    default_days = DEFAULT_PRESET.get("days", 100)
    try:
        days_input = input(f"Enter number of days for the simulation (default: {default_days}): ").strip()
        user_config["days"] = int(days_input) if days_input else default_days
        if user_config["days"] <= 0:
            logging.warning(f"Invalid number of days: {days_input}. Falling back to default value: {default_days}.")
            user_config["days"] = default_days
    except ValueError:
        logging.warning(f"Invalid input for number of days: {days_input}. Falling back to default value: {default_days}.")
        user_config["days"] = default_days

    # Prompt for additional configuration options
    logging.info("Prompting user for additional configuration options.")
    print("\n--- Simulation Configuration ---")
    print("1. Use Default Configuration Preset")
    print("2. Choose Configuration Preset")
    print("3. Customize Additional Parameters")

    choice = input("Choose an option (1, 2, 3): ").strip()
    if choice == "2":
        preset_name = choose_preset()
        logging.info(f"User selected preset: {preset_name}.")
        user_config.update(PRESET_CONFIGS[preset_name])
    elif choice == "3":
        print("Setting custom configuration...")
        for key, value in DEFAULT_PRESET.items():
            label = KEY_LABELS.get(key, key)

            if key in {"grid_size", "days"}:
                # Skip grid size and days as they are already collected
                continue
            elif isinstance(value, dict):
                user_config[key] = {}
                print(f"\n{label}:")
                for sub_key, sub_value in value.items():
                    input_value = input(f"Enter value for {sub_key} (default: {sub_value}): ").strip()
                    user_config[key][sub_key] = parse_input_value(input_value, sub_value)
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                user_config[key] = parse_input_value(input_value, value)
    elif choice == "1":
        logging.info("User chose default configuration preset.")
        user_config.update(DEFAULT_PRESET)
    else:
        logging.warning("Invalid choice from user. Using default configuration preset.")
        print("Invalid choice. Using default configuration.")
        user_config.update(DEFAULT_PRESET)

    return user_config


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
        logging.warning(f"Could not parse input value '{input_value}' for type {type(default_value).__name__}. Using default: {default_value}")

    return default_value


def choose_preset():
    """
    Allow the user to choose a configuration preset from a list.
    """
    logging.info("Displaying configuration presets for user.")
    print("Available Configuration Presets:")
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
            logging.warning("Invalid input. User did not enter a number.")
            print("Invalid input. Please enter a number.")


# Main Execution
if __name__ == "__main__":
    try:
        logging.info("Starting the Cellular Automaton Simulation.")

        # Collect all user inputs
        final_config = collect_user_input()

        # Update the configuration once with all collected inputs
        update_config(custom_config=final_config)

        # Validate and finalize configuration
        config = get_config()
        validate_config(config)
        finalize_config()

        # Extract essential parameters for simulation
        grid_size = config["grid_size"]
        days = config["days"]
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
