# config.py

config = {
    "baseline_temperature": [15, 25, 5, -10, 20, 30, 10, 12], # 0: Sea | 1: Land (desert) | 2: Cloud | 3: Ice | 4: Forest | 5: City | 6: Air  | 7: Rain
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
    "melting_point": 50, # Temperature threshold for melting ice
    "evaporation_point": 100, # Temperature threshold for evaporation
    "pollution_threshold": None,  # Pollution threshold, initially set to None and can be updated at runtime
}
