# config.py

# Configuration settings for the simulation
# config.py

# Configuration settings for the simulation

config = {

    # Visualization settings
    "tint": False,  # Use tint for better visual representation

    # Default simulation parameters
    "default_grid_size": (10, 10, 10),  # Increased grid size for more detailed simulation
    "default_days": 50,  # Longer default simulation duration

    # 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air | 7: Rain | 8: Vacuum
    "baseline_temperature": [
        20,  # Sea: Warmer
        35,  # Desert: Very hot
        10,  # Cloud: Slightly warmer
        -10,  # Ice: Slightly less cold
        25,  # Forest: Warmer
        40,  # City: Hot due to urban heat
        15,  # Air: Warmer
        18,  # Rain: Warmer
        -30  # Vacuum: Extremely cold
    ],

    "cell_type_weights": {
        0: 1.0,  # Ocean
        1: 1.5,  # Desert
        2: 0.8,  # Cloud
        3: 0.9,  # Ice
        4: 2.0,  # Forest
        5: 3.0,  # City
        6: 0.7,  # Air
        7: 1.2,  # Rain
        8: 0.0,  # Vacuum has no weight
    },

    "baseline_pollution_level": [
        5,   # 0: Sea - Increased pollution
        15,  # 1: Desert - Higher pollution
        3,   # 2: Cloud - Some pollution
        0,   # 3: Ice - Negligible pollution
        5,   # 4: Forest - Low pollution
        100,  # 5: City - Extreme pollution
        10,   # 6: Air - Moderate pollution
        2,   # 7: Rain - Cleansing effect
        0,   # 8: Vacuum - No pollution
    ],

    "temperature_extinction_point": 70,
    "freezing_point": 0,  # Raised for less ice
    "melting_point": 15,
    "evaporation_point": 20,
    "water_transfer_threshold": 0.1,  # Increased for faster water dynamics
    "rain_transfer_rate": 0.1,  # Transfer rate for rain to other cells (new key)

    # Pollution-related thresholds
    "pollution_damage_threshold": 3.0,  # Lowered for faster damage
    "pollution_level_tipping_point": 30,  # More sensitive ecosystem changes
    "natural_pollution_decay_rate": 0.01,  # Slower pollution decay

    # Temperature decay
    "natural_temperature_decay_rate": 0.02,  # Faster cooling/heating dynamics

    # Cloud-specific settings
    "cloud_saturation_threshold": 1,  # Clouds form rain faster

    # Rates for environmental changes
    "melting_rate": 0.3,  # Ice melts faster
    "evaporation_rate": 0.1,  # Increased evaporation rate

    # Forest-specific settings
    "forest_pollution_absorption_rate": 0.05,  # More aggressive pollution absorption
    "forest_cooling_effect": 0.05,  # More pronounced cooling effect

    # City-specific settings
    "city_pollution_increase_rate": 0.3,  # Cities emit pollution rapidly
    "city_warming_effect": 0.2,  # Increased warming effect
    "city_temperature_upper_limit": 70,  # Cities remain very hot
    "city_pollution_upper_limit": 200,  # Cities can accumulate extreme pollution

    # Ratios for land cell types
    "initial_ratios": {
        "forest": 0.4,  # Increased forest proportion
        "city": 0.2,  # Fewer cities
        "desert": 0.3,  # Increased deserts
        "vacuum": 0.1,  # Reduced vacuum
    },

    "ambient_temperature": 25,  # Warmer base temperature
    "cycle_amplitude": 10,  # Larger day-night temperature swing

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.1),  # Air (slightly opaque white)
        2: (0.8, 0.8, 0.8, 1.0),  # Cloud (light gray)
        0: (0.0, 0.4, 1.0, 1.0),  # Ocean (deeper blue)
        3: (0.7, 0.9, 1.0, 1.0),  # Ice (brighter cyan)
        7: (0.3, 0.5, 0.8, 1.0),  # Rain (brighter grayish-blue)
        1: (1.0, 0.7, 0.4, 1.0),  # Desert (warmer sandy gold)
        4: (0.0, 0.8, 0.0, 1.0),  # Forest (vibrant green)
        5: (0.5, 0.0, 0.5, 1.0),  # City (brighter purple)
        8: (0.0, 0.0, 0.0, 0.0),  # Vacuum (fully transparent)
    },
}



key_labels = {
    "baseline_temperature": "Baseline Temperature (°C)",
    "cell_type_weights": "Cell Type Weights",
    "baseline_pollution_level": "Baseline Pollution Levels",
    "temperature_extinction_point": "Temperature Extinction Point (°C)",
    "freezing_point": "Freezing Point (°C)",
    "melting_point": "Melting Point (°C)",
    "evaporation_point": "Evaporation Point (°C)",
    "water_transfer_threshold": "Water Transfer Threshold",
    "pollution_damage_threshold": "Pollution Damage Threshold",
    "pollution_level_tipping_point": "Pollution Tipping Point",
    "natural_pollution_decay_rate": "Natural Pollution Decay Rate",
    "natural_temperature_decay_rate": "Natural Temperature Decay Rate",
    "cloud_saturation_threshold": "Cloud Saturation Threshold",
    "melting_rate": "Melting Rate",
    "evaporation_rate": "Evaporation Rate",
    "forest_pollution_absorption_rate": "Forest Pollution Absorption Rate",
    "forest_cooling_effect": "Forest Cooling Effect",
    "city_pollution_increase_rate": "City Pollution Increase Rate",
    "city_warming_effect": "City Warming Effect",
    "city_temperature_upper_limit": "City Temperature Upper Limit (°C)",
    "city_pollution_upper_limit": "City Pollution Upper Limit",
    "initial_ratios": "Initial Ratios (Proportions)",
    "default_grid_size": "Default Grid Size (X, Y, Z)",
    "default_days": "Default Simulation Duration (Days)",
    "tint": "Visualization Tint",
}



def format_config_value(key, value):
    
    if key == "baseline_temperature":
        return "  |  ".join(
            [f"{particle_mapping[i]}: {temp}°C" for i, temp in enumerate(value)]
        )
    
    if key == "initial_ratios":
        return "  |  ".join([f"{k.capitalize()}: {v}" for k, v in value.items()])
    elif key == "cell_type_weights":
        return "  |  ".join(
            [f"{particle_mapping[k]}: {v}" for k, v in value.items()]
        )
    elif key == "baseline_pollution_level":
        return "  |  ".join(
            [f"{particle_mapping[i]}: {level}" for i, level in enumerate(value)]
        )
    else:
        return str(value)
    
    
particle_mapping = {
    0: "Ocean",
    1: "Desert",
    2: "Cloud",
    3: "Ice",
    4: "Forest",
    5: "City",
    6: "Air",
    7: "Rain",
    8: "Vacuum",
}