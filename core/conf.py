# config.py

# 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air  | 7: Rain

config = {
    "baseline_temperature": [15, 25, 5, -10, 20, 30, 10, 12],

    "cell_type_weights": {
        0: 1.0,  # Ocean
        1: 1.2,  # Desert
        2: 0.8,  # Cloud
        3: 0.01,  # Ice
        4: 1.5,  # Forest
        5: 2.0,  # City
        6: 0.5,  # Air
        7: 1.1,  # Rain
    },

    "baseline_pollution_level": [1, 10, 0, 0, 2, 50, 0, 1],

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.01),  # Air (transparent white)
        2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
        0: (0.0, 0.0, 1.0, 1.0),  # Ocean (blue)
        3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
        7: (0.2, 0.3, 0.5, 1.0),  # Rain (light cyan)
        1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
        4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
        5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
    },

    "extinction_point": 80,
    "freezing_point": -10,  # Temperature that causes ocean freeze and converts into ice
    "melting_point": 45,  # Temperature threshold for melting ice
    "evaporation_point": 30,  # Temperature threshold for evaporation
    "water_transfer_threshold": 0.1,


    "pollution_damage_threshold": 10.0,
    "pollution_level_tipping_point": 60,
    "natural_pollution_decay_rate": 0.4,
    "natural_temperature_decay_rate":  0.4,


    "cloud_saturation_threshold": 10.0,

    "melting_rate" : 0.2,
    "evaporation_rate" : 0.1,

    "forest_pollution_absorption_rate": 0.2,
    "forest_cooling_effect": 0.2,


    "city_pollution_increase_rate": 0.01,
    "city_warming_effect": 0.01,
    "city_temperature_upper_limit": 60,
    "city_pollution_upper_limit": 100,

    "tint": False
}
