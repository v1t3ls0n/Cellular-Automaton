# List of required keys
required_keys = [
    'days',
    'grid_size',
    'initial_ratios',
    'baseline_temperature',
    'baseline_pollution_level',
    'cell_type_weights',
    'forest_pollution_absorption_rate',
    'forest_cooling_effect',
    'forest_pollution_extinction_point',
    'forest_temperature_extinction_point',
    'city_pollution_generation_rate',
    'city_warming_effect',
    'city_temperature_extinction_point',
    'city_pollution_extinction_point',
    'freezing_point',
    'melting_point',
    'evaporation_point',
    "water_transfer_threshold",
    'water_transfer_rate',
    'ocean_conversion_threshold',
    'pollution_damage_threshold',
    'pollution_level_tipping_point',
    'natural_pollution_decay_rate',
    'natural_temperature_decay_rate',
    'cloud_saturation_threshold',
    'melting_rate',
    'evaporation_rate'
]

# Example preset configuration
preset_configs = {
    'Mass Extinction and Forest Regrowth (Scenario 1)': {
        'days': 50,
        'grid_size': (10, 10, 10),
        'initial_ratios': {
            'forest': 0.2,
            'city': 0.6,
            'desert': 0.1,
            'vacuum': 0.1,
        },
        'baseline_temperature': [15, 30, 5, -15, 20, 35, 10, 12, -20],
        'baseline_pollution_level': [3, 10, 1, 0, 2, 20, 50, 0, 0],
        'cell_type_weights': {0: 1.0, 1: 1.2, 2: 0.7, 3: 0.8, 4: 1.5, 5: 2.0, 6: 0.5, 7: 1.0, 8: 0.0},
        'forest_pollution_absorption_rate': 0.5,
        'forest_cooling_effect': 0.5,
        'forest_pollution_extinction_point': 100,
        'forest_temperature_extinction_point': 80,
        'city_pollution_generation_rate': 0.5,
        'city_warming_effect': 0.5,
        'city_temperature_extinction_point': 100,
        'city_pollution_extinction_point': 100,
        'freezing_point': -15,
        'melting_point': 20,
        'evaporation_point': 35,
        "water_transfer_threshold": 0.05,
        'water_transfer_rate': 0.1,
        'ocean_conversion_threshold': 1.0,
        'pollution_damage_threshold': 30.0,
        'pollution_level_tipping_point': 50,
        'natural_pollution_decay_rate': 0.3,
        'natural_temperature_decay_rate': 0.3,
        'cloud_saturation_threshold': 3.0,
        'melting_rate': 0.15,
        'evaporation_rate': 0.05
    }
}

# Check if all keys are present and correct in the preset
missing_keys = [key for key in required_keys if key not in preset_configs['Mass Extinction and Forest Regrowth (Scenario 1)']]

print(missing_keys)