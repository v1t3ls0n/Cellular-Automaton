from types import MappingProxyType
from config.presets import PRESET_CONFIGS, DEFAULT_PRESET, REQUIRED_KEYS, PARTICLE_MAPPING, KEY_LABELS
import logging

# Config.py
class Config:
    """
    Singleton class to manage the global configuration for the simulation.
    Ensures the configuration is synchronized across all files and immutable after finalization.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._config = DEFAULT_PRESET.copy()
            cls._instance._finalized = False
        return cls._instance

    def get(self):
        """
        Get a copy of the current configuration.

        Returns:
            dict: A copy of the configuration.
        """
        return dict(self._config)

    def update(self, preset_name=None, custom_config=None):
        """
        Update the configuration with a preset or custom configuration.

        Args:
            preset_name (str, optional): The name of the preset configuration to load.
            custom_config (dict, optional): A custom configuration dictionary.

        Raises:
            RuntimeError: If the configuration has been finalized.
            ValueError: If neither preset_name nor custom_config is provided.
        """
        if self._finalized:
            raise RuntimeError("Configuration has been finalized and cannot be updated.")

        if preset_name:
            if preset_name in PRESET_CONFIGS:
                self._config = PRESET_CONFIGS[preset_name].copy()
            else:
                raise ValueError(f"Preset '{preset_name}' does not exist.")
        elif custom_config:
            self._config.update(custom_config)
        else:
            raise ValueError("Either preset_name or custom_config must be provided.")

    def finalize(self):
        """
        Finalize the configuration, making it immutable.
        """
        if self._finalized:
            raise RuntimeError("Configuration is already finalized.")
        self._config = MappingProxyType(self._config)  # Make immutable
        self._finalized = True

    def validate(self):
        """
        Validate that the configuration meets all required keys and types.

        Raises:
            KeyError: If any required key is missing.
            TypeError: If any key has an incorrect type.
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

        check_keys(self._config, REQUIRED_KEYS)

    def log_full_configuration(self):
        """
        Logs the full configuration in a human-readable format using PARTICLE_MAPPING and KEY_LABELS.
        """
        config = self.get()  # Get the current configuration
        logging.info("Full Configuration:")
        
        for key, value in config.items():
            label = KEY_LABELS.get(key, key)  # Use human-readable labels if available
            if isinstance(value, dict):
                logging.info(f"{label}:")
                for sub_key, sub_value in value.items():
                    particle_label = PARTICLE_MAPPING.get(sub_key, sub_key)  # Use particle mapping if applicable
                    logging.info(f"  {particle_label}: {sub_value}")
            elif isinstance(value, list):
                logging.info(f"{label}:")
                for sub_key, sub_value in enumerate(value):
                    particle_label = PARTICLE_MAPPING.get(sub_key, sub_key)  # Use particle mapping if applicable
                    logging.info(f"  {particle_label}: {sub_value}")
            else:
                logging.info(f"{label}: {value}")




# Singleton instance accessor
config_instance = Config()
