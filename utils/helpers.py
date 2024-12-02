from utils.constants import PARTICLE_MAPPING

def floatify_preset_integers(presets):
    """
    Converts all integer values in the CONFIG_PRESETS to floats, except for the 'days' key.
    Args:
        presets (dict): The configuration presets dictionary.
    """
    def process_value(value, key):
        if isinstance(value, int) and key != "days":
            return float(value)  # Convert int to float
        elif isinstance(value, dict):
            return {k: process_value(v, k) for k, v in value.items()}  # Process nested dictionaries
        elif isinstance(value, list):
            return [process_value(v, None) for v in value]  # Process nested lists
        else:
            return value  # Leave other types unchanged

    for preset_name, preset in presets.items():
        presets[preset_name] = {k: process_value(v, k) for k, v in preset.items()}


def rgba_to_hex(rgba):
    r, g, b, a = rgba  # Extract RGBA components
    return f'#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}'


# Function to format config values for display or logging
def format_config_value(key, value):
    if key == 'baseline_temperature':
        return '  |  '.join(
            [f'{PARTICLE_MAPPING[i]}: {temp}°C' for i,
                temp in enumerate(value)]
        )
    elif key == 'initial_ratios':
        return '  |  '.join([f'{k.capitalize()}: {v}' for k, v in value.items()])
    elif key == 'cell_type_weights':
        return '  |  '.join(
            [f'{PARTICLE_MAPPING[k]}: {v}' for k, v in value.items()]
        )
    elif key == 'baseline_pollution_level':
        return '  |  '.join(
            [f'{PARTICLE_MAPPING[i]}: {level}' for i,
                level in enumerate(value)]
        )
    else:
        return str(value)


