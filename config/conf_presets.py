# conf_presets.py
# Mapping of particle types to descriptive names
PARTICLE_MAPPING = {
    0: 'Ocean',
    1: 'Desert',
    2: 'Cloud',
    3: 'Ice',
    4: 'Forest',
    5: 'City',
    6: 'Air',
    7: 'Rain',
    8: 'Vacuum',
}

# Labels for configuration keys to provide context in the UI or logs
KEY_LABELS = {
    # General Simulation Parameters
    "days": "Default Simulation Duration (Days)",
    "grid_size": "Default Grid Size (X, Y, Z)",
    "initial_ratios": "Initial Ratios (Proportions)",

    # Baseline Environmental Properties
    "baseline_temperature": "Baseline Temperature (°C)",
    "baseline_pollution_level": "Baseline Pollution Levels",

    # Pollution Transfer Weights
    "cell_type_pollution_transfer_weights": "Pollution Transfer Weights by Cell Type",

    # Temperature Transfer Weights
    "cell_type_temperature_transfer_weights": "Temperature Transfer Weights by Cell Type",

    # Water Transfer Weights
    "cell_type_water_transfer_weights": "Water Transfer Weights by Cell Type",

    # Forest Properties
    "forest_pollution_absorption_rate": "Forest Pollution Absorption Rate",
    "forest_cooling_effect": "Forest Cooling Effect",
    "forest_pollution_extinction_point": "Forest Pollution Extinction Point",
    "forest_temperature_extinction_point": "Forest Temperature Extinction Point",

    # City Properties
    "city_pollution_generation_rate": "City Pollution Generation Rate",
    "city_warming_effect": "City Warming Effect",
    "city_temperature_extinction_point": "City Temperature Extinction Point (°C)",
    "city_pollution_extinction_point": "City Pollution Extinction Point",

    # Physical Properties
    "freezing_point": "Freezing Point (°C)",
    "melting_point": "Melting Point (°C)",
    "evaporation_point": "Evaporation Point (°C)",

    # Water Transfer
    "water_transfer_threshold": "Water Transfer Threshold",
    "water_transfer_rate": "Water Transfer Rate",
    "ocean_conversion_threshold": "Ocean Conversion Threshold",

    # Pollution Dynamics
    "pollution_damage_threshold": "Pollution Damage Threshold",
    "pollution_level_tipping_point": "Pollution Tipping Point",
    "natural_pollution_decay_rate": "Natural Pollution Decay Rate",

    # Temperature Dynamics
    "natural_temperature_decay_rate": "Natural Temperature Decay Rate",

    # Cloud Properties
    "cloud_saturation_threshold": "Cloud Saturation Threshold",

    # Environmental Change Rates
    "melting_rate": "Melting Rate",
    "evaporation_rate": "Evaporation Rate",

    # Conversion Weights
    "cell_type_collision_weights": "Cell Type Collision Weights",

    # Base Colors
    "base_colors": "Base Colors for Cell Types",
}



PRESET_CONFIGS = {
    "Low Air Pollution (5.0) - Stable" : {

    # General Simulation Parameters
    "days": 365,  # Total number of simulation days.
    "grid_size": (10, 10, 10),  # Dimensions of the simulation grid (X, Y, Z).
    "initial_ratios": {
        "forest": 0.3,  # 30% of the grid is forest.
        "city": 0.3,  # 30% of the grid is urban areas.
        "desert": 0.2,  # 20% of the grid is desert.
        "vacuum": 0.2,  # 20% of the grid is uninhabitable.
    },

    # Baseline Environmental Properties
    "baseline_temperature": [
        15.0,   # Ocean: Moderate temperature due to high heat capacity.
        35.0,   # Desert: Hot due to direct sunlight and arid conditions.
        5.0,    # Cloud: Cool at high altitudes.
        -20.0,  # Ice: Below freezing point.
        25.0,   # Forest: Moderate, buffered by vegetation.
        30.0,   # City: Warmer due to urban heat islands.
        10.0,   # Air: Cool and variable depending on altitude.
        12.0,   # Rain: Mild temperature, absorbs heat.
        -50.0,  # Vacuum: Close to absolute zero.
    ],

    "baseline_pollution_level": [
        3.0,   # Ocean: Pollution from industrial and plastic waste.
        2.0,   # Desert: Sparse pollution due to limited human activity.
        1.0,   # Cloud: Almost no pollution, cleanses atmosphere.
        0.0,   # Ice: Pristine and isolated.
        5.0,   # Forest: Low pollution absorbed by vegetation.
        40.0,  # City: High due to factories and vehicles.
        5.0,   # Air: Moderate, depends on proximity to cities.
        2.0,   # Rain: Low, acts as a natural cleanser.
        0.0,   # Vacuum: No pollution, uninhabitable space.
    ],

    # Pollution Transfer Weights
    "cell_type_pollution_transfer_weights": {
        0: 0.3,  # Ocean: Moderate exchange due to water currents.
        1: 0.1,  # Desert: Minimal exchange due to sparse vegetation.
        2: 0.8,  # Cloud: High due to atmospheric circulation.
        3: 0.1,  # Ice: Low, isolated conditions.
        4: 0.6,  # Forest: Moderate, acts as a pollution sink.
        5: 0.9,  # City: High, concentrated emissions.
        6: 0.7,  # Air: High, pollution disperses easily.
        7: 0.5,  # Rain: Moderate, washes pollution from the air.
        8: 0.0,  # Vacuum: No transfer, uninhabitable space.
    },

    # Temperature Transfer Weights
    "cell_type_temperature_transfer_weights": {
        0: 0.3,  # Ocean: Moderate due to water's heat capacity.
        1: 0.2,  # Desert: Low due to poor heat conductivity.
        2: 0.8,  # Cloud: High due to rapid atmospheric mixing.
        3: 0.1,  # Ice: Very low due to insulation.
        4: 0.5,  # Forest: Moderate due to vegetation as a buffer.
        5: 0.7,  # City: High, urban areas retain and radiate heat.
        6: 1.0,  # Air: Very high due to convection currents.
        7: 0.6,  # Rain: Moderate, transfers heat efficiently.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Water Transfer Weights
    "cell_type_water_transfer_weights": {
        0: 0.8,  # Ocean: High transfer due to large water bodies.
        1: 0.1,  # Desert: Low due to poor water retention.
        2: 0.9,  # Cloud: Very high due to atmospheric water vapor.
        3: 0.3,  # Ice: Low, solid state hinders transfer.
        4: 0.6,  # Forest: Moderate due to vegetation transpiration.
        5: 0.4,  # City: Low, impermeable surfaces limit transfer.
        6: 1.0,  # Air: Very high due to vapor movement.
        7: 0.9,  # Rain: Very high, direct water transfer.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Forest Properties
    # Rate of pollution absorption by forests.
    "forest_pollution_absorption_rate": 0.1,
    "forest_cooling_effect": 0.1,  # Cooling effect of vegetation.
    # Pollution level beyond which forests die.
    "forest_pollution_extinction_point": 100.0,
    # Temperature beyond which forests die.
    "forest_temperature_extinction_point": 100.0,

    # City Properties
    # Rate of pollution generation in urban areas.
    "city_pollution_generation_rate": 0.1,
    "city_warming_effect": 0.1,  # Heat retention in cities.
    # Max temperature before urban collapse.
    "city_temperature_extinction_point": 70.0,
    # Pollution level before urban collapse.
    "city_pollution_extinction_point": 100.0,

    # Physical Properties
    "freezing_point": -15.0,  # Freezing temperature for water (°C).
    "melting_point": 20.0,  # Melting temperature for ice (°C).
    "evaporation_point": 35.0,  # Evaporation temperature for water (°C).

    # Water Transfer
    # Minimum water mass difference for transfer.
    "water_transfer_threshold": 0.05,
    "water_transfer_rate": 0.1,  # Rate of water transfer between cells.
    # Water mass needed to convert a cell to ocean.
    "ocean_conversion_threshold": 1.0,

    # Pollution Dynamics
    # Pollution level causing damage to ecosystems.
    "pollution_damage_threshold": 10.0,
    # Pollution level beyond which damage accelerates.
    "pollution_level_tipping_point": 50.0,
    # Rate at which pollution decays naturally.
    "natural_pollution_decay_rate": 0.01,

    # Temperature Dynamics
    # Rate at which temperature equalizes to baseline.
    "natural_temperature_decay_rate": 0.01,

    # Cloud Properties
    # Minimum water mass for clouds to precipitate.
    "cloud_saturation_threshold": 2.0,

    # Environmental Change Rates
    "melting_rate": 0.15,  # Rate at which ice melts.
    "evaporation_rate": 0.05,  # Rate at which water evaporates.


    "cell_type_collision_weights": {
        # Ocean: High conversion likelihood due to fluid dynamics but less energy dissipation.
        0: 1.2,
        # Desert: Moderate conversion due to sand and dust, which partially absorbs impacts.
        1: 0.7,
        # Cloud: Very low conversion as clouds are gaseous and diffuse energy quickly.
        2: 0.7,
        # Ice: High conversion as ice can transfer energy efficiently while fracturing.
        3: 0.9,
        # Forest: High due to vegetation density, which buffers and redirects energy.
        4: 1.4,
        # City: Very high as dense urban structures lead to strong interactions and energy dissipation.
        5: 1.8,
        # Air: Moderate as energy dissipates through air currents but may redirect particles.
        6: 0.6,
        # Rain: Moderate as water droplets can transfer some energy but dissipate quickly.
        7: 0.8,
        8: 0.0,  # Vacuum: No conversion as collisions can't occur in a vacuum.
    },

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.2),  # Air: Light white with some transparency
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud: Neutral gray, opaque
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean: Deep blue, opaque
        3: (0.6, 0.8, 1.0, 1.0),  # Ice: Pale blue, opaque
        7: (0.5, 0.5, 1.0, 1.0),  # Rain: Medium blue, opaque
        1: (1.0, 0.7, 0.3, 1.0),  # Desert: warm sandy tone
        4: (0.0, 0.6, 0.0, 1.0),  # Forest: Vibrant green, opaque
        5: (0.4, 0.0, 0.4, 1.0),  # City: Purple tone, opaque
        8: (1.0, 1.0, 1.0, 0.0),  # Vacuum: Fully transparent
    }


},
    "Normal Air Pollution (80.0) - Stable" : {

    # General Simulation Parameters
    "days": 365,  # Total number of simulation days.
    "grid_size": (10, 10, 10),  # Dimensions of the simulation grid (X, Y, Z).
    "initial_ratios": {
        "forest": 0.3,  # 30% of the grid is forest.
        "city": 0.3,  # 30% of the grid is urban areas.
        "desert": 0.2,  # 20% of the grid is desert.
        "vacuum": 0.2,  # 20% of the grid is uninhabitable.
    },

    # Baseline Environmental Properties
    "baseline_temperature": [
        15.0,   # Ocean: Moderate temperature due to high heat capacity.
        35.0,   # Desert: Hot due to direct sunlight and arid conditions.
        5.0,    # Cloud: Cool at high altitudes.
        -20.0,  # Ice: Below freezing point.
        25.0,   # Forest: Moderate, buffered by vegetation.
        30.0,   # City: Warmer due to urban heat islands.
        10.0,   # Air: Cool and variable depending on altitude.
        12.0,   # Rain: Mild temperature, absorbs heat.
        -50.0,  # Vacuum: Close to absolute zero.
    ],

    "baseline_pollution_level": [
        3.0,   # Ocean: Pollution from industrial and plastic waste.
        2.0,   # Desert: Sparse pollution due to limited human activity.
        1.0,   # Cloud: Almost no pollution, cleanses atmosphere.
        0.0,   # Ice: Pristine and isolated.
        5.0,   # Forest: Low pollution absorbed by vegetation.
        40.0,  # City: High due to factories and vehicles.
        80.0,   # Air: Moderate, depends on proximity to cities.
        2.0,   # Rain: Low, acts as a natural cleanser.
        0.0,   # Vacuum: No pollution, uninhabitable space.
    ],

    # Pollution Transfer Weights
    "cell_type_pollution_transfer_weights": {
        0: 0.3,  # Ocean: Moderate exchange due to water currents.
        1: 0.1,  # Desert: Minimal exchange due to sparse vegetation.
        2: 0.8,  # Cloud: High due to atmospheric circulation.
        3: 0.1,  # Ice: Low, isolated conditions.
        4: 0.6,  # Forest: Moderate, acts as a pollution sink.
        5: 0.9,  # City: High, concentrated emissions.
        6: 0.7,  # Air: High, pollution disperses easily.
        7: 0.5,  # Rain: Moderate, washes pollution from the air.
        8: 0.0,  # Vacuum: No transfer, uninhabitable space.
    },

    # Temperature Transfer Weights
    "cell_type_temperature_transfer_weights": {
        0: 0.3,  # Ocean: Moderate due to water's heat capacity.
        1: 0.2,  # Desert: Low due to poor heat conductivity.
        2: 0.8,  # Cloud: High due to rapid atmospheric mixing.
        3: 0.1,  # Ice: Very low due to insulation.
        4: 0.5,  # Forest: Moderate due to vegetation as a buffer.
        5: 0.7,  # City: High, urban areas retain and radiate heat.
        6: 1.0,  # Air: Very high due to convection currents.
        7: 0.6,  # Rain: Moderate, transfers heat efficiently.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Water Transfer Weights
    "cell_type_water_transfer_weights": {
        0: 0.8,  # Ocean: High transfer due to large water bodies.
        1: 0.1,  # Desert: Low due to poor water retention.
        2: 0.9,  # Cloud: Very high due to atmospheric water vapor.
        3: 0.3,  # Ice: Low, solid state hinders transfer.
        4: 0.6,  # Forest: Moderate due to vegetation transpiration.
        5: 0.4,  # City: Low, impermeable surfaces limit transfer.
        6: 1.0,  # Air: Very high due to vapor movement.
        7: 0.9,  # Rain: Very high, direct water transfer.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Forest Properties
    # Rate of pollution absorption by forests.
    "forest_pollution_absorption_rate": 0.1,
    "forest_cooling_effect": 0.1,  # Cooling effect of vegetation.
    # Pollution level beyond which forests die.
    "forest_pollution_extinction_point": 100.0,
    # Temperature beyond which forests die.
    "forest_temperature_extinction_point": 100.0,

    # City Properties
    # Rate of pollution generation in urban areas.
    "city_pollution_generation_rate": 0.1,
    "city_warming_effect": 0.1,  # Heat retention in cities.
    # Max temperature before urban collapse.
    "city_temperature_extinction_point": 70.0,
    # Pollution level before urban collapse.
    "city_pollution_extinction_point": 100.0,

    # Physical Properties
    "freezing_point": -15.0,  # Freezing temperature for water (°C).
    "melting_point": 20.0,  # Melting temperature for ice (°C).
    "evaporation_point": 35.0,  # Evaporation temperature for water (°C).

    # Water Transfer
    # Minimum water mass difference for transfer.
    "water_transfer_threshold": 0.05,
    "water_transfer_rate": 0.1,  # Rate of water transfer between cells.
    # Water mass needed to convert a cell to ocean.
    "ocean_conversion_threshold": 1.0,

    # Pollution Dynamics
    # Pollution level causing damage to ecosystems.
    "pollution_damage_threshold": 10.0,
    # Pollution level beyond which damage accelerates.
    "pollution_level_tipping_point": 50.0,
    # Rate at which pollution decays naturally.
    "natural_pollution_decay_rate": 0.01,

    # Temperature Dynamics
    # Rate at which temperature equalizes to baseline.
    "natural_temperature_decay_rate": 0.01,

    # Cloud Properties
    # Minimum water mass for clouds to precipitate.
    "cloud_saturation_threshold": 2.0,

    # Environmental Change Rates
    "melting_rate": 0.15,  # Rate at which ice melts.
    "evaporation_rate": 0.05,  # Rate at which water evaporates.


    "cell_type_collision_weights": {
        # Ocean: High conversion likelihood due to fluid dynamics but less energy dissipation.
        0: 1.2,
        # Desert: Moderate conversion due to sand and dust, which partially absorbs impacts.
        1: 0.7,
        # Cloud: Very low conversion as clouds are gaseous and diffuse energy quickly.
        2: 0.7,
        # Ice: High conversion as ice can transfer energy efficiently while fracturing.
        3: 0.9,
        # Forest: High due to vegetation density, which buffers and redirects energy.
        4: 1.4,
        # City: Very high as dense urban structures lead to strong interactions and energy dissipation.
        5: 1.8,
        # Air: Moderate as energy dissipates through air currents but may redirect particles.
        6: 0.6,
        # Rain: Moderate as water droplets can transfer some energy but dissipate quickly.
        7: 0.8,
        8: 0.0,  # Vacuum: No conversion as collisions can't occur in a vacuum.
    },

     "base_colors":{
        6: (1.0, 1.0, 1.0, 0.2),  # Air: Light white with some transparency
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud: Neutral gray, opaque
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean: Deep blue, opaque
        3: (0.6, 0.8, 1.0, 1.0),  # Ice: Pale blue, opaque
        7: (0.5, 0.5, 1.0, 1.0),  # Rain: Medium blue, opaque
        1: (1.0, 0.7, 0.3, 1.0),  # Desert: warm sandy tone
        4: (0.0, 0.6, 0.0, 1.0),  # Forest: Vibrant green, opaque
        5: (0.4, 0.0, 0.4, 1.0),  # City: Purple tone, opaque
        8: (1.0, 1.0, 1.0, 0.0),  # Vacuum: Fully transparent
    }


},
   "High Air Pollution (200.0) - Mass Extinction Of Cities" : {

    # General Simulation Parameters
    "days": 365,  # Total number of simulation days.
    "grid_size": (10, 10, 10),  # Dimensions of the simulation grid (X, Y, Z).
    "initial_ratios": {
        "forest": 0.3,  # 30% of the grid is forest.
        "city": 0.3,  # 30% of the grid is urban areas.
        "desert": 0.2,  # 20% of the grid is desert.
        "vacuum": 0.2,  # 20% of the grid is uninhabitable.
    },

    # Baseline Environmental Properties
    "baseline_temperature": [
        15.0,   # Ocean: Moderate temperature due to high heat capacity.
        35.0,   # Desert: Hot due to direct sunlight and arid conditions.
        5.0,    # Cloud: Cool at high altitudes.
        -20.0,  # Ice: Below freezing point.
        25.0,   # Forest: Moderate, buffered by vegetation.
        30.0,   # City: Warmer due to urban heat islands.
        10.0,   # Air: Cool and variable depending on altitude.
        12.0,   # Rain: Mild temperature, absorbs heat.
        -50.0,  # Vacuum: Close to absolute zero.
    ],

    "baseline_pollution_level": [
        3.0,   # Ocean: Pollution from industrial and plastic waste.
        2.0,   # Desert: Sparse pollution due to limited human activity.
        1.0,   # Cloud: Almost no pollution, cleanses atmosphere.
        0.0,   # Ice: Pristine and isolated.
        5.0,   # Forest: Low pollution absorbed by vegetation.
        40.0,  # City: High due to factories and vehicles.
        200.0,   # Air: Moderate, depends on proximity to cities.
        2.0,   # Rain: Low, acts as a natural cleanser.
        0.0,   # Vacuum: No pollution, uninhabitable space.
    ],

    # Pollution Transfer Weights
    "cell_type_pollution_transfer_weights": {
        0: 0.3,  # Ocean: Moderate exchange due to water currents.
        1: 0.1,  # Desert: Minimal exchange due to sparse vegetation.
        2: 0.8,  # Cloud: High due to atmospheric circulation.
        3: 0.1,  # Ice: Low, isolated conditions.
        4: 0.6,  # Forest: Moderate, acts as a pollution sink.
        5: 0.9,  # City: High, concentrated emissions.
        6: 0.7,  # Air: High, pollution disperses easily.
        7: 0.5,  # Rain: Moderate, washes pollution from the air.
        8: 0.0,  # Vacuum: No transfer, uninhabitable space.
    },

    # Temperature Transfer Weights
    "cell_type_temperature_transfer_weights": {
        0: 0.3,  # Ocean: Moderate due to water's heat capacity.
        1: 0.2,  # Desert: Low due to poor heat conductivity.
        2: 0.8,  # Cloud: High due to rapid atmospheric mixing.
        3: 0.1,  # Ice: Very low due to insulation.
        4: 0.5,  # Forest: Moderate due to vegetation as a buffer.
        5: 0.7,  # City: High, urban areas retain and radiate heat.
        6: 1.0,  # Air: Very high due to convection currents.
        7: 0.6,  # Rain: Moderate, transfers heat efficiently.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Water Transfer Weights
    "cell_type_water_transfer_weights": {
        0: 0.8,  # Ocean: High transfer due to large water bodies.
        1: 0.1,  # Desert: Low due to poor water retention.
        2: 0.9,  # Cloud: Very high due to atmospheric water vapor.
        3: 0.3,  # Ice: Low, solid state hinders transfer.
        4: 0.6,  # Forest: Moderate due to vegetation transpiration.
        5: 0.4,  # City: Low, impermeable surfaces limit transfer.
        6: 1.0,  # Air: Very high due to vapor movement.
        7: 0.9,  # Rain: Very high, direct water transfer.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Forest Properties
    # Rate of pollution absorption by forests.
    "forest_pollution_absorption_rate": 0.1,
    "forest_cooling_effect": 0.1,  # Cooling effect of vegetation.
    # Pollution level beyond which forests die.
    "forest_pollution_extinction_point": 100.0,
    # Temperature beyond which forests die.
    "forest_temperature_extinction_point": 100.0,

    # City Properties
    # Rate of pollution generation in urban areas.
    "city_pollution_generation_rate": 0.1,
    "city_warming_effect": 0.1,  # Heat retention in cities.
    # Max temperature before urban collapse.
    "city_temperature_extinction_point": 70.0,
    # Pollution level before urban collapse.
    "city_pollution_extinction_point": 100.0,

    # Physical Properties
    "freezing_point": -15.0,  # Freezing temperature for water (°C).
    "melting_point": 20.0,  # Melting temperature for ice (°C).
    "evaporation_point": 35.0,  # Evaporation temperature for water (°C).

    # Water Transfer
    # Minimum water mass difference for transfer.
    "water_transfer_threshold": 0.05,
    "water_transfer_rate": 0.1,  # Rate of water transfer between cells.
    # Water mass needed to convert a cell to ocean.
    "ocean_conversion_threshold": 1.0,

    # Pollution Dynamics
    # Pollution level causing damage to ecosystems.
    "pollution_damage_threshold": 10.0,
    # Pollution level beyond which damage accelerates.
    "pollution_level_tipping_point": 50.0,
    # Rate at which pollution decays naturally.
    "natural_pollution_decay_rate": 0.01,

    # Temperature Dynamics
    # Rate at which temperature equalizes to baseline.
    "natural_temperature_decay_rate": 0.01,

    # Cloud Properties
    # Minimum water mass for clouds to precipitate.
    "cloud_saturation_threshold": 2.0,

    # Environmental Change Rates
    "melting_rate": 0.15,  # Rate at which ice melts.
    "evaporation_rate": 0.05,  # Rate at which water evaporates.


    "cell_type_collision_weights": {
        # Ocean: High conversion likelihood due to fluid dynamics but less energy dissipation.
        0: 1.2,
        # Desert: Moderate conversion due to sand and dust, which partially absorbs impacts.
        1: 0.7,
        # Cloud: Very low conversion as clouds are gaseous and diffuse energy quickly.
        2: 0.7,
        # Ice: High conversion as ice can transfer energy efficiently while fracturing.
        3: 0.9,
        # Forest: High due to vegetation density, which buffers and redirects energy.
        4: 1.4,
        # City: Very high as dense urban structures lead to strong interactions and energy dissipation.
        5: 1.8,
        # Air: Moderate as energy dissipates through air currents but may redirect particles.
        6: 0.6,
        # Rain: Moderate as water droplets can transfer some energy but dissipate quickly.
        7: 0.8,
        8: 0.0,  # Vacuum: No conversion as collisions can't occur in a vacuum.
    },

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.2),  # Air: Light white with some transparency
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud: Neutral gray, opaque
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean: Deep blue, opaque
        3: (0.6, 0.8, 1.0, 1.0),  # Ice: Pale blue, opaque
        7: (0.5, 0.5, 1.0, 1.0),  # Rain: Medium blue, opaque
        1: (1.0, 0.7, 0.3, 1.0),  # Desert: warm sandy tone
        4: (0.0, 0.6, 0.0, 1.0),  # Forest: Vibrant green, opaque
        5: (0.4, 0.0, 0.4, 1.0),  # City: Purple tone, opaque
        8: (1.0, 1.0, 1.0, 0.0),  # Vacuum: Fully transparent
    }


},
   "Exteemely High Air Pollution - Mass Extinction Of Forests and Cities (500.0)" : {

    # General Simulation Parameters
    "days": 365,  # Total number of simulation days.
    "grid_size": (10, 10, 10),  # Dimensions of the simulation grid (X, Y, Z).
    "initial_ratios": {
        "forest": 0.3,  # 30% of the grid is forest.
        "city": 0.3,  # 30% of the grid is urban areas.
        "desert": 0.2,  # 20% of the grid is desert.
        "vacuum": 0.2,  # 20% of the grid is uninhabitable.
    },

    # Baseline Environmental Properties
    "baseline_temperature": [
        15.0,   # Ocean: Moderate temperature due to high heat capacity.
        35.0,   # Desert: Hot due to direct sunlight and arid conditions.
        5.0,    # Cloud: Cool at high altitudes.
        -20.0,  # Ice: Below freezing point.
        25.0,   # Forest: Moderate, buffered by vegetation.
        30.0,   # City: Warmer due to urban heat islands.
        10.0,   # Air: Cool and variable depending on altitude.
        12.0,   # Rain: Mild temperature, absorbs heat.
        -50.0,  # Vacuum: Close to absolute zero.
    ],

    "baseline_pollution_level": [
        3.0,   # Ocean: Pollution from industrial and plastic waste.
        2.0,   # Desert: Sparse pollution due to limited human activity.
        1.0,   # Cloud: Almost no pollution, cleanses atmosphere.
        0.0,   # Ice: Pristine and isolated.
        5.0,   # Forest: Low pollution absorbed by vegetation.
        40.0,  # City: High due to factories and vehicles.
        500.0,   # Air: Moderate, depends on proximity to cities.
        2.0,   # Rain: Low, acts as a natural cleanser.
        0.0,   # Vacuum: No pollution, uninhabitable space.
    ],

    # Pollution Transfer Weights
    "cell_type_pollution_transfer_weights": {
        0: 0.3,  # Ocean: Moderate exchange due to water currents.
        1: 0.1,  # Desert: Minimal exchange due to sparse vegetation.
        2: 0.8,  # Cloud: High due to atmospheric circulation.
        3: 0.1,  # Ice: Low, isolated conditions.
        4: 0.6,  # Forest: Moderate, acts as a pollution sink.
        5: 0.9,  # City: High, concentrated emissions.
        6: 0.7,  # Air: High, pollution disperses easily.
        7: 0.5,  # Rain: Moderate, washes pollution from the air.
        8: 0.0,  # Vacuum: No transfer, uninhabitable space.
    },

    # Temperature Transfer Weights
    "cell_type_temperature_transfer_weights": {
        0: 0.3,  # Ocean: Moderate due to water's heat capacity.
        1: 0.2,  # Desert: Low due to poor heat conductivity.
        2: 0.8,  # Cloud: High due to rapid atmospheric mixing.
        3: 0.1,  # Ice: Very low due to insulation.
        4: 0.5,  # Forest: Moderate due to vegetation as a buffer.
        5: 0.7,  # City: High, urban areas retain and radiate heat.
        6: 1.0,  # Air: Very high due to convection currents.
        7: 0.6,  # Rain: Moderate, transfers heat efficiently.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Water Transfer Weights
    "cell_type_water_transfer_weights": {
        0: 0.8,  # Ocean: High transfer due to large water bodies.
        1: 0.1,  # Desert: Low due to poor water retention.
        2: 0.9,  # Cloud: Very high due to atmospheric water vapor.
        3: 0.3,  # Ice: Low, solid state hinders transfer.
        4: 0.6,  # Forest: Moderate due to vegetation transpiration.
        5: 0.4,  # City: Low, impermeable surfaces limit transfer.
        6: 1.0,  # Air: Very high due to vapor movement.
        7: 0.9,  # Rain: Very high, direct water transfer.
        8: 0.0,  # Vacuum: No transfer possible.
    },

    # Forest Properties
    # Rate of pollution absorption by forests.
    "forest_pollution_absorption_rate": 0.1,
    "forest_cooling_effect": 0.1,  # Cooling effect of vegetation.
    # Pollution level beyond which forests die.
    "forest_pollution_extinction_point": 100.0,
    # Temperature beyond which forests die.
    "forest_temperature_extinction_point": 100.0,

    # City Properties
    # Rate of pollution generation in urban areas.
    "city_pollution_generation_rate": 0.1,
    "city_warming_effect": 0.1,  # Heat retention in cities.
    # Max temperature before urban collapse.
    "city_temperature_extinction_point": 70.0,
    # Pollution level before urban collapse.
    "city_pollution_extinction_point": 100.0,

    # Physical Properties
    "freezing_point": -15.0,  # Freezing temperature for water (°C).
    "melting_point": 20.0,  # Melting temperature for ice (°C).
    "evaporation_point": 35.0,  # Evaporation temperature for water (°C).

    # Water Transfer
    # Minimum water mass difference for transfer.
    "water_transfer_threshold": 0.05,
    "water_transfer_rate": 0.1,  # Rate of water transfer between cells.
    # Water mass needed to convert a cell to ocean.
    "ocean_conversion_threshold": 1.0,

    # Pollution Dynamics
    # Pollution level causing damage to ecosystems.
    "pollution_damage_threshold": 10.0,
    # Pollution level beyond which damage accelerates.
    "pollution_level_tipping_point": 50.0,
    # Rate at which pollution decays naturally.
    "natural_pollution_decay_rate": 0.01,

    # Temperature Dynamics
    # Rate at which temperature equalizes to baseline.
    "natural_temperature_decay_rate": 0.01,

    # Cloud Properties
    # Minimum water mass for clouds to precipitate.
    "cloud_saturation_threshold": 2.0,

    # Environmental Change Rates
    "melting_rate": 0.15,  # Rate at which ice melts.
    "evaporation_rate": 0.05,  # Rate at which water evaporates.


    "cell_type_collision_weights": {
        # Ocean: High conversion likelihood due to fluid dynamics but less energy dissipation.
        0: 1.2,
        # Desert: Moderate conversion due to sand and dust, which partially absorbs impacts.
        1: 0.7,
        # Cloud: Very low conversion as clouds are gaseous and diffuse energy quickly.
        2: 0.7,
        # Ice: High conversion as ice can transfer energy efficiently while fracturing.
        3: 0.9,
        # Forest: High due to vegetation density, which buffers and redirects energy.
        4: 1.4,
        # City: Very high as dense urban structures lead to strong interactions and energy dissipation.
        5: 1.8,
        # Air: Moderate as energy dissipates through air currents but may redirect particles.
        6: 0.6,
        # Rain: Moderate as water droplets can transfer some energy but dissipate quickly.
        7: 0.8,
        8: 0.0,  # Vacuum: No conversion as collisions can't occur in a vacuum.
    },

    "base_colors": {
        6: (1.0, 1.0, 1.0, 0.2),  # Air: Light white with some transparency
        2: (0.7, 0.7, 0.7, 1.0),  # Cloud: Neutral gray, opaque
        0: (0.0, 0.3, 1.0, 1.0),  # Ocean: Deep blue, opaque
        3: (0.6, 0.8, 1.0, 1.0),  # Ice: Pale blue, opaque
        7: (0.5, 0.5, 1.0, 1.0),  # Rain: Medium blue, opaque
        1: (1.0, 0.7, 0.3, 1.0),  # Desert: warm sandy tone
        4: (0.0, 0.6, 0.0, 1.0),  # Forest: Vibrant green, opaque
        5: (0.4, 0.0, 0.4, 1.0),  # City: Purple tone, opaque
        8: (1.0, 1.0, 1.0, 0.0),  # Vacuum: Fully transparent
    }


},
}

DEFAULT_PRESET = PRESET_CONFIGS["Normal Air Pollution (80.0) - Stable"]

REQUIRED_KEYS = {
    "days": int,
    "grid_size": tuple,
    "initial_ratios": {
        "forest": float,
        "city": float,
        "desert": float,
        "vacuum": float,
    },
    "baseline_temperature": list,
    "baseline_pollution_level": list,
    "cell_type_collision_weights": {
        0: float,  # Ocean
        1: float,  # Desert
        2: float,  # Cloud
        3: float,  # Ice
        4: float,  # Forest
        5: float,  # City
        6: float,  # Air
        7: float,  # Rain
        8: float  # Vacuum
    },
    "cell_type_pollution_transfer_weights": {
        0: float,  # Ocean
        1: float,  # Desert
        2: float,  # Cloud
        3: float,  # Ice
        4: float,  # Forest
        5: float,  # City
        6: float,  # Air
        7: float,  # Rain
        8: float  # Vacuum
    },
    "cell_type_temperature_transfer_weights": {

        0: float,  # Ocean
        1: float,  # Desert
        2: float,  # Cloud
        3: float,  # Ice
        4: float,  # Forest
        5: float,  # City
        6: float,  # Air
        7: float,  # Rain
        8: float  # Vacuum

    },
    "forest_pollution_absorption_rate": float,
    "forest_cooling_effect": float,
    "forest_pollution_extinction_point": float,
    "forest_temperature_extinction_point": float,
    "city_pollution_generation_rate": float,
    "city_warming_effect": float,
    "city_temperature_extinction_point": float,
    "city_pollution_extinction_point": float,
    "freezing_point": float,
    "melting_point": float,
    "evaporation_point": float,
    "water_transfer_threshold": float,
    "water_transfer_rate": float,
    "ocean_conversion_threshold": float,
    "pollution_damage_threshold": float,
    "pollution_level_tipping_point": float,
    "natural_pollution_decay_rate": float,
    "natural_temperature_decay_rate": float,
    "cloud_saturation_threshold": float,
    "melting_rate": float,
    "evaporation_rate": float,
    "base_colors": {
        0: tuple,  # Ocean
        1: tuple,  # Desert
        2: tuple,  # Cloud
        3: tuple,  # Ice
        4: tuple,  # Forest
        5: tuple,  # City
        6: tuple,  # Air
        7: tuple,  # Rain
        8: tuple,  # Vacuum
    },
}
