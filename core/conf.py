# config.py

config = {
    # 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air  | 7: Rain
    "baseline_temperature": [15, 25, 5, -10, 20, 30, 10, 12],
    "baseline_pollution_level": [1, 10, 0, 0, 2, 50, 0, 1],
    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
        2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
        0: (0.0, 0.0, 1.0, 1.0),  # Ocean (blue)
        3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
        7: (0.4, 0.8, 1.0, 0.1),  # Rain (light cyan)
        1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
        4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
        5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
    },
    "freezing_point": -10,  # Temperature that causes ocean freeze and converts into ice
    "melting_point": 50,  # Temperature threshold for melting ice
    "evaporation_point": 100,  # Temperature threshold for evaporation
    # Pollution threshold, initially set to None and can be updated at runtime,
    "pollution_threshold": None,
    "cloud_saturation_threshold": 1.0,
    "forest_pollution_absorption_rate": 0.2,
    "forest_cooling_effect": 0.2,
    "city_pollution_increase_rate": 0.4,
    "city_warming_effect": 0.4,
    "natural_pollution_decay_rate": 0.1,
    "natural_temperature_decay_rate":  0.1
}
