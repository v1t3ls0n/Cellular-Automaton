import os

from config.config_state_handler import update_config, get_config, validate_config, finalize_config
from config.conf_presets import PRESET_CONFIGS, DEFAULT_PRESET, PARTICLE_MAPPING, KEY_LABELS
from display.MatplotlibDisplay import MatplotlibDisplay
from core.Simulation import Simulation

def choose_preset():
    """
    Allow the user to choose a configuration preset from a list.
    """
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
                return chosen_preset
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        limit_bad_input -= 1

    print("Too many invalid attempts. Using default preset.")
    return DEFAULT_PRESET


def parse_input_value(input_value, default_value):
    """
    Parse the input value based on the type of the default value.
    """
    if not input_value:
        return default_value

    if isinstance(default_value, bool):
        return input_value.lower() in {"true", "yes", "1"} if isinstance(input_value, str) else bool(input_value)

    try:
        if isinstance(default_value, int):
            return int(input_value)
        if isinstance(default_value, float):
            return float(input_value)
    except ValueError:
        pass

    return input_value


def parse_user_input():
    """
    Prompt user for configuration parameters or use presets.
    """
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
            if isinstance(value, dict):
                user_config[key] = {}
                print(f"\n{label}:")
                for sub_key, sub_value in value.items():
                    particle_label = PARTICLE_MAPPING.get(sub_key, sub_key)
                    input_value = input(f"Enter value for {particle_label} (default: {sub_value}): ").strip()
                    user_config[key][sub_key] = parse_input_value(input_value, sub_value)
            else:
                input_value = input(f"Enter value for {label} (default: {value}): ").strip()
                user_config[key] = parse_input_value(input_value, value)

        update_config(custom_config=user_config)
    elif choice == "1":
        print("Using Default Configuration Preset")
        update_config(custom_config=DEFAULT_PRESET)
    else:
        print("Invalid choice. Using default configuration.")
        update_config(custom_config=DEFAULT_PRESET)


# Main Execution
if __name__ == "__main__":
    try:
        logging.basicConfig(filename="simulation.log", level=logging.DEBUG)
        logging.info("Starting the Cellular Automaton Simulation...")

        parse_user_input()
        config = get_config()
        validate_config(config)
        finalize_config()

        # Extract essential parameters for simulation
        grid_size = config.get("grid_size", (10, 10, 10))
        days = config.get("days", 100)
        initial_ratios = config.get("initial_ratios", {})

        if round(sum(initial_ratios.values()), 2) != 1.0:
            print("Initial ratios must sum to 1. Adjusting to default ratios.")
            initial_ratios = DEFAULT_PRESET["initial_ratios"]

        # Initialize and run simulation
        simulation = Simulation(grid_size=grid_size, initial_ratios=initial_ratios, days=days)
        print("Starting simulation...")
        simulation.precompute()
        print("Simulation complete. Displaying results...")

        display = MatplotlibDisplay(simulation)
        display.render_graphic_user_interface()

        if get_config() != config:
            raise ValueError("Configuration was updated during simulation.")
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
        exit(1)
