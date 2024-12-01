from core.conf import config, particle_mapping, key_labels
from core.Simulation import Simulation
from display.MatplotlibDisplay import MatplotlibDisplay
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    # filename="simulation.log",
    # filemode="w",  # Overwrite the file each time
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Simulation started.")


# Utility function to parse grid size input
def parse_grid_size(input_value):
    """
    Parse the grid size from a string or list.
    Accepts formats like:
    - "10,10,10"
    - "10 10 10"
    - [10, 10, 10]

    Returns:
        tuple: Parsed grid size as integers (x, y, z)
    """
    if isinstance(input_value, str):
        # Replace commas with spaces, split by spaces, and convert to integers
        return tuple(int(value) for value in input_value.replace(",", " ").split())
    elif isinstance(input_value, (list, tuple)):
        # Convert list or tuple to a tuple of integers
        return tuple(int(value) for value in input_value)
    else:
        raise ValueError("Invalid grid size format. Provide a list, tuple, or string.")


# Utility function to parse boolean strings
def parse_boolean(input_value):
    """
    Parse boolean input from strings like "true" or "false".
    Returns True for "true", False for "false", and passes through other values.

    Args:
        input_value (str): Input string to parse

    Returns:
        bool or original value: Parsed boolean or original input
    """
    if isinstance(input_value, str):
        if input_value.lower() in {"true", "yes", "1", 1, "True"}:
            return True
        elif input_value.lower() in {"false", "no", "0", "False", 0}:
            return False
    return input_value

def parse_input_value(input_value, default_value):
    """
    Parse the input value based on the type of the default value.
    """
    if not input_value:  # If input is empty, return the default value
        return default_value

    # Try to parse as boolean
    boolean_value = parse_boolean(input_value)
    if isinstance(boolean_value, bool):
        return boolean_value

    # Parse as float, then integer if necessary
    try:
        if isinstance(default_value, float):
            return float(input_value)
        if isinstance(default_value, int):
            return int(input_value)
    except ValueError:
        pass  # Fall back to returning the input as a string

    return input_value  # Default to string if no conversion is possible


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
                    user_config[key][sub_key] = parse_input_value(input_value, sub_value)
            elif isinstance(value, list):
                print(f"\n{label} (list values):")
                user_config[key] = []
                for i, v in enumerate(value):
                    particle_label = particle_mapping.get(i, i)
                    input_value = input(f"Enter value for {particle_label} (default: {v}): ").strip()
                    user_config[key].append(parse_input_value(input_value, v))
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                user_config[key] = parse_input_value(input_value, value)
    else:
        print("Invalid choice. Using default configuration.")
        user_config = config.copy()

    return user_config




# Main execution
if __name__ == "__main__":
    # Prompt user for configuration
    user_config = get_user_configuration()

    # Extract essential parameters for simulation
    grid_size_input = user_config.get("default_grid_size", (10, 10, 10))
    grid_size = parse_grid_size(grid_size_input)  # Parse grid size input
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

   