# conf.py
import logging
from collections import defaultdict
from utils.constants import PRESET_CONFIGS
# Global configuration dictionary
CONFIG = defaultdict()



# Configuration settings for the simulation
# This file contains all the parameters and settings used to define the behavior and appearance
# of the cellular automata simulation.
def get_config():
    global CONFIG
    return CONFIG.copy()

def update_config(preset_name=None, custom_config=None):
    '''
    Update the global CONFIG with a preset or custom configuration.

    Args:
        preset_name (str, optional): The name of the preset configuration to load.
        custom_config (dict, optional): A custom configuration dictionary.

    Raises:
        ValueError: If neither preset_name nor custom_config is provided.
    '''
    global CONFIG
    if preset_name:
        if preset_name in PRESET_CONFIGS:            
            CONFIG = PRESET_CONFIGS[preset_name]
            logging.info(f'Loaded preset configuration: {preset_name}')
        else:
            raise ValueError(f'Preset {preset_name} does not exist.')
    elif custom_config:
        CONFIG = custom_config
        logging.info('Loaded custom configuration.')
    else:
        raise ValueError('Either preset_name or custom_config must be provided.')
    return CONFIG.copy()
    
def validate_config(config):
    """
    Validate that all required keys and nested keys exist in the configuration.

    Args:
        config (dict): The configuration dictionary to validate.

    Raises:
        KeyError: If any required key or sub-key is missing.
    """
    required_keys = {
        "days": int,
        "grid_size": tuple,
        "initial_ratios": {
            "forest": float,
            "city": float,
            "desert": float,
            "vacuum": float,
        },
        "baseline_temperature": list,
        "baseline_pollution_level": list,
        "cell_type_weights": dict,
        "forest_pollution_absorption_rate": float,
        "forest_cooling_effect": float,
        "forest_pollution_extinction_point": float,
        "forest_temperature_extinction_point":float,
        "city_pollution_generation_rate": float,
        "city_warming_effect": float,
        "city_temperature_extinction_point": float,
        "city_pollution_extinction_point": float,
        "freezing_point": float,
        "melting_point": float,
        "evaporation_point": float,
        "water_transfer_threshold": float,
        "water_transfer_rate": float,
        "ocean_conversion_threshold": float,
        "pollution_damage_threshold": float,
        "pollution_level_tipping_point": float,
        "natural_pollution_decay_rate": float,
        "natural_temperature_decay_rate": float,
        "cloud_saturation_threshold": float,
        "melting_rate": float,
        "evaporation_rate": float,
        "base_colors": {
            0: tuple,  # Ocean
            1: tuple,  # Desert
            2: tuple,  # Cloud
            3: tuple,  # Ice
            4: tuple,  # Forest
            5: tuple,  # City
            6: tuple,  # Air
            7: tuple,  # Rain
            8: tuple,  # Vacuum
        },
    }

    def check_keys(sub_config, required_sub_keys, path=""):

        for key, expected_type in required_sub_keys.items():
            full_key = f"{path}.{key}" if path else key
            if key not in sub_config:
                raise KeyError(f"Missing required configuration key: {full_key}")
            if isinstance(expected_type, dict):
                if not isinstance(sub_config[key], dict):
                    raise TypeError(
                        f"Key {full_key} must be a dictionary, but got {type(sub_config[key])}."
                    )
                check_keys(sub_config[key], expected_type, full_key)
            else:
                if not isinstance(sub_config[key], expected_type):
                    if isinstance(expected_type, tuple) and isinstance(sub_config[key], expected_type):
                        continue  # Allow multiple types
                    raise TypeError(
                        f"Key {full_key} must be of type {expected_type}, "
                        f"but got {type(sub_config[key]).__name__}."
                    )

    check_keys(config, required_keys)



