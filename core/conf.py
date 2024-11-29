# config.py

# Configuration settings for the simulation

config = {

    # Visualization settings
    "tint": False, # Use tint for better visual representation

 
    # Default simulation parameters
    "default_grid_size": (10, 10, 10), # Increased grid size for more detailed simulation
    "default_days": 50, # Longer default simulation duration
   
 
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

    "baseline_pollution_level": [
        3,   # 0: Sea - Some pollution from industrial waste and microplastics
        10,  # 1: Desert - Dust and localized human activity
        1,   # 2: Cloud - Almost no pollution
        0,   # 3: Ice - Pristine areas with negligible pollution
        2,   # 4: Forest - Absorbs pollution; very low
        20,  # 5: City - High pollution due to vehicles, factories, etc.
        5,   # 6: Air - Variable based on proximity to cities
        0,   # 7: Rain - Cleanses the atmosphere
        0,   # 8: Vacuum - No pollution in empty space
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



    "temperature_extinction_point": 80,
    "freezing_point": -15,  # Lowered to account for extreme cold
    "melting_point": 20,
    "evaporation_point": 35,
        
    "water_transfer_threshold": 0.05,  # Adjusted for smoother transfer dynamics

    # Pollution-related thresholds
    "pollution_damage_threshold": 10.0,  # Slightly higher threshold for visible damage
    "pollution_level_tipping_point": 50, # Increased sensitivity for ecosystem changes
    "natural_pollution_decay_rate": 0.1, # Pollution decreases more slowly over time

    # Temperature decay
    "natural_temperature_decay_rate": 0.1, # Retains realistic cooling/heating dynamics

    # Cloud-specific settings
    "cloud_saturation_threshold": 3.0,

    # Rates for environmental changes
    "melting_rate": 0.15,  # Ice melts slower
    "evaporation_rate": 0.05,  # Reduced evaporation rate for balance

    # Forest-specific settings
    "forest_pollution_absorption_rate": 0.2, # Forests absorb more pollution
    "forest_cooling_effect": 0.2, # Slightly more cooling effect from forests

    # City-specific settings
    "city_pollution_increase_rate": 0.1, # Cities emit pollution at a steady rate
    "city_warming_effect": 0.1, # Slightly reduced warming effect for balance
    "city_temperature_upper_limit": 100, # Cities remain hot but capped lower
    "city_pollution_upper_limit": 100, # Cities can accumulate significant pollution

    # Ratios for land cell types
    "initial_ratios": {
        "forest": 0.4,  # Increased forest proportion
        "city": 0.4,    # Slightly fewer cities
        "desert": 0.1,  # Balance deserts and forests
        "vacuum": 0.1,  # Significant amount of vacuum for realism
    },
    
    "ambient_temperature": 20,  # Base temperature in degrees Celsius
    "cycle_amplitude": 5,       # Day-night temperature swing

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.1),  # Air (transparent white)
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud (light gray)
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean (deep blue)
        3: (0.6, 0.8, 1.0, 1.0),  # Ice (light cyan)
        7: (0.5, 0.5, 1.0, 1.0), # Rain (grayish-blue)
        1: (1.0, 0.8, 0.5, 1.0),  # Desert (sandy gold)
        4: (0.0, 0.6, 0.0, 1.0),  # Forest (lush green)
        5: (0.4, 0.0, 0.4, 1.0),  # City (dark purple)
        8: (0.0, 0.0, 0.0, 0.0),  # Vacuum (fully transparent/black)
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