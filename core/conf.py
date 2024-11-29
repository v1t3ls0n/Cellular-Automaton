# config.py

# Configuration settings for the simulation

config = {
    # 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air | 7: Rain | 8: Vacuum
    "baseline_temperature": [
        15,  # Sea: Warm
        30,  # Desert: Hot
        5,   # Cloud: Cool
        -15, # Ice: Freezing
        20,  # Forest: Moderate
        35,  # City: Hot due to urban heat
        10,  # Air: Cool
        12,  # Rain: Mild
        -20 # Vacuum: Near absolute zero
    ],

    "cell_type_weights": {
        0: 1.0,  # Ocean
        1: 1.2,  # Desert
        2: 0.7,  # Cloud
        3: 0.8,  # Ice
        4: 1.5,  # Forest
        5: 2.0,  # City
        6: 0.5,  # Air
        7: 1.0,  # Rain
        8: 0.0,  # Vacuum has no weight
    },

    "baseline_pollution_level": [
        3,   # 0: Sea - Some pollution from industrial waste and microplastics
        10,  # 1: Desert - Dust and localized human activity
        1,   # 2: Cloud - Almost no pollution
        0,   # 3: Ice - Pristine areas with negligible pollution
        2,   # 4: Forest - Absorbs pollution; very low
        70,  # 5: City - High pollution due to vehicles, factories, etc.
        5,   # 6: Air - Variable based on proximity to cities
        0,   # 7: Rain - Cleanses the atmosphere
        0,   # 8: Vacuum - No pollution in empty space
    ],

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.1),  # Air (transparent white)
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud (light gray)
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean (deep blue)
        3: (0.6, 0.8, 1.0, 1.0),  # Ice (light cyan)
        7: (0.3, 0.4, 0.6, 1.0),  # Rain (grayish-blue)
        1: (1.0, 0.8, 0.5, 1.0),  # Desert (sandy gold)
        4: (0.0, 0.6, 0.0, 1.0),  # Forest (lush green)
        5: (0.4, 0.0, 0.4, 1.0),  # City (dark purple)
        8: (0.0, 0.0, 0.0, 0.0),  # Vacuum (fully transparent/black)
    },

    "temperature_extinction_point": 60,
    "freezing_point": -15,  # Lowered to account for extreme cold
    "melting_point": 10,
    "evaporation_point": 25,
    "water_transfer_threshold": 0.05,  # Adjusted for smoother transfer dynamics

    # Pollution-related thresholds
    "pollution_damage_threshold": 5.0,  # Slightly higher threshold for visible damage
    "pollution_level_tipping_point": 50, # Increased sensitivity for ecosystem changes
    "natural_pollution_decay_rate": 0.02, # Pollution decreases more slowly over time

    # Temperature decay
    "natural_temperature_decay_rate": 0.4, # Retains realistic cooling/heating dynamics

    # Cloud-specific settings
    "cloud_saturation_threshold": 1.2,

    # Rates for environmental changes
    "melting_rate": 0.15,  # Ice melts slower
    "evaporation_rate": 0.05,  # Reduced evaporation rate for balance

    # Forest-specific settings
    "forest_pollution_absorption_rate": 0.3, # Forests absorb more pollution
    "forest_cooling_effect": 0.3, # Slightly more cooling effect from forests

    # City-specific settings
    "city_pollution_increase_rate": 0.6, # Cities emit pollution at a steady rate
    "city_warming_effect": 0.4, # Slightly reduced warming effect for balance
    "city_temperature_upper_limit": 50, # Cities remain hot but capped lower
    "city_pollution_upper_limit": 100, # Cities can accumulate significant pollution

    # Ratios for land cell types
    "initial_ratios": {
        "forest": 0.3,  # Increased forest proportion
        "city": 0.3,    # Slightly fewer cities
        "desert": 0.2,  # Balance deserts and forests
        "vacuum": 0.2,  # Significant amount of vacuum for realism
    },

    # Default simulation parameters
    "default_grid_size": (20, 20, 20), # Increased grid size for more detailed simulation
    "default_days": 100, # Longer default simulation duration

    # Visualization settings
    "tint": True, # Use tint for better visual representation
}


# Cell type mapping with initial values for easy reference
config["cell_type_mapping"] = {
    0: {  # Sea
        "name": "Sea",
        "temperature": config["baseline_temperature"][0],
        "pollution": config["baseline_pollution_level"][0],
        "weight": config["cell_type_weights"][0],
        "color": config["base_colors"][0],
    },
    1: {  # Desert
        "name": "Desert",
        "temperature": config["baseline_temperature"][1],
        "pollution": config["baseline_pollution_level"][1],
        "weight": config["cell_type_weights"][1],
        "color": config["base_colors"][1],
    },
    2: {  # Cloud
        "name": "Cloud",
        "temperature": config["baseline_temperature"][2],
        "pollution": config["baseline_pollution_level"][2],
        "weight": config["cell_type_weights"][2],
        "color": config["base_colors"][2],
    },
    3: {  # Ice
        "name": "Ice",
        "temperature": config["baseline_temperature"][3],
        "pollution": config["baseline_pollution_level"][3],
        "weight": config["cell_type_weights"][3],
        "color": config["base_colors"][3],
    },
    4: {  # Forest
        "name": "Forest",
        "temperature": config["baseline_temperature"][4],
        "pollution": config["baseline_pollution_level"][4],
        "weight": config["cell_type_weights"][4],
        "color": config["base_colors"][4],
    },
    5: {  # City
        "name": "City",
        "temperature": config["baseline_temperature"][5],
        "pollution": config["baseline_pollution_level"][5],
        "weight": config["cell_type_weights"][5],
        "color": config["base_colors"][5],
    },
    6: {  # Air
        "name": "Air",
        "temperature": config["baseline_temperature"][6],
        "pollution": config["baseline_pollution_level"][6],
        "weight": config["cell_type_weights"][6],
        "color": config["base_colors"][6],
    },
    7: {  # Rain
        "name": "Rain",
        "temperature": config["baseline_temperature"][7],
        "pollution": config["baseline_pollution_level"][7],
        "weight": config["cell_type_weights"][7],
        "color": config["base_colors"][7],
    },
    8: {  # Vacuum
        "name": "Vacuum",
        "temperature": config["baseline_temperature"][8],
        "pollution": config["baseline_pollution_level"][8],
        "weight": config["cell_type_weights"][8],
        "color": config["base_colors"][8],
    },
}
