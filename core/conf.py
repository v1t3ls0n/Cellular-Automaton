# config.py

# Configuration settings for the simulation

config = {
    # 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air | 7: Rain | 8: Vacuum
    "baseline_temperature": [15, 25, 5, -10, 20, 30, 10, 12, 0],  # Vacuum temperature set to 0

    "cell_type_weights": {
        0: 1.0,  # Ocean
        1: 1.2,  # Desert
        2: 0.8,  # Cloud
        3: 0.9,  # Ice
        4: 1.5,  # Forest
        5: 2.0,  # City
        6: 0.5,  # Air
        7: 1.1,  # Rain
        8: 0.0,  # Vacuum has no weight
    },

    "baseline_pollution_level": [
        5,   # 0: Sea - Some pollution due to industrial waste and ocean pollution.
        15,  # 1: Land (desert) - Minimal pollution but may contain dust particles or localized pollution.
        2,   # 2: Cloud - Very low pollution, mainly water vapor.
        1,   # 3: Ice - Negligible pollution in frozen areas.
        3,   # 4: Forest - Forests absorb pollution, so they typically have low levels.
        50,  # 5: City - High pollution due to industrial activities, vehicles, etc.
        10,  # 6: Air - Moderate pollution depending on proximity to cities and other sources.
        0,   # 7: Rain - Negligible pollution as rain often helps clean the air.
        0,   # 8: Vacuum - No pollution in empty space.
    ],
    
    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.5),  # Air (transparent white)
        2: (0.5, 0.5, 0.5, 1.0),  # Cloud (gray)
        0: (0.0, 0.0, 1.0, 1.0),  # Ocean (blue)
        3: (0.4, 0.8, 1.0, 1.0),  # Ice (cyan)
        7: (0.2, 0.3, 0.5, 1.0),  # Rain (light cyan)
        1: (1.0, 1.0, 0.0, 1.0),  # Land (gold)
        4: (0.0, 0.5, 0.0, 1.0),  # Forest (green)
        5: (0.5, 0.0, 0.5, 1.0),  # City (purple)
        8: (0.0, 0.0, 0.0, 0.0),  # Vacuum (transparent/black for empty space)
    },

    "extinction_point": 80,
    "freezing_point": -10,
    "melting_point": 45,
    "evaporation_point": 30,
    "water_transfer_threshold": 0.1,

    # Pollution-related thresholds
    "pollution_damage_threshold": 1.0,  # Default pollution threshold
    "pollution_level_tipping_point": 60,
    "natural_pollution_decay_rate": 0.4,

    # Temperature decay
    "natural_temperature_decay_rate": 0.01,

    # Cloud-specific settings
    "cloud_saturation_threshold": 1.5,

    # Rates for environmental changes
    "melting_rate": 0.2,
    "evaporation_rate": 0.1,

    # Forest-specific settings
    "forest_pollution_absorption_rate": 0.2,
    "forest_cooling_effect": 0.2,

    # City-specific settings
    "city_pollution_increase_rate": 0.5,
    "city_warming_effect": 0.5,
    "city_temperature_upper_limit": 60,
    "city_pollution_upper_limit": 100,

    # Ratios for land cell types
    "initial_ratios": {
        "forest": 0.2,  
        "city": 0.4,
        "desert": 0.2,
        "vacuum": 0.2,  #
    },

    # Default simulation parameters
    "default_grid_size": (10, 10, 10),
    "default_days": 50,

    # Visualization settings
    "tint": False,
}
