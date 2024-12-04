import logging
from collections import defaultdict
from types import MappingProxyType
from config.conf_presets import PRESET_CONFIGS, DEFAULT_PRESET, REQUIRED_KEYS

# Global configuration dictionary
CONFIG = DEFAULT_PRESET
CONFIG_FINALIZED = False


def finalize_config():
    """
    Finalizes the global configuration, making it immutable.
    """
    global CONFIG, CONFIG_FINALIZED
    if CONFIG_FINALIZED:
        raise RuntimeError("Configuration is already finalized.")
    CONFIG = MappingProxyType(CONFIG)  # Make CONFIG immutable
    CONFIG_FINALIZED = True
    logging.info("Configuration has been finalized and is now immutable.")


def get_config_preset(preset_name=None):
    """
    Retrieve a configuration preset.

    Args:
        preset_name (str, optional): Name of the preset configuration to retrieve.

    Returns:
        dict: A copy of the preset configuration.
    """
    if preset_name:
        if preset_name in PRESET_CONFIGS:
            return PRESET_CONFIGS[preset_name].copy()
        else:
            raise ValueError('Preset name does not exist.')
    else:
        logging.debug("preset_name is None. Returning default config preset.")
        return DEFAULT_PRESET.copy()


def get_config():
    """
    Retrieves a copy of the current global configuration.

    Returns:
        dict: A copy of the global configuration.
    """
    return dict(CONFIG)  # Ensure the returned configuration is a copy


def update_config(preset_name=None, custom_config=None):
    """
    Updates the global CONFIG with a preset or custom configuration.

    Args:
        preset_name (str, optional): The name of the preset configuration to load.
        custom_config (dict, optional): A custom configuration dictionary.

    Raises:
        ValueError: If neither preset_name nor custom_config is provided.
        RuntimeError: If the configuration has been finalized.
    """
    global CONFIG
    if CONFIG_FINALIZED:
        raise RuntimeError("Configuration has been finalized and cannot be updated.")
    if preset_name:
        if preset_name in PRESET_CONFIGS:
            CONFIG = PRESET_CONFIGS[preset_name]
            logging.info(f"Loaded preset configuration: {preset_name}")
        else:
            raise ValueError(f"Preset {preset_name} does not exist.")
    elif custom_config:
        CONFIG = custom_config
        logging.info("Loaded custom configuration.")
    else:
        raise ValueError("Either preset_name or custom_config must be provided.")


def validate_config(config):
    """
    Validates that all required keys and nested keys exist in the configuration.

    Args:
        config (dict): The configuration dictionary to validate.

    Raises:
        KeyError: If any required key or sub-key is missing.
        TypeError: If any key's value has an incorrect type.
    """
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

    check_keys(config, REQUIRED_KEYS)
