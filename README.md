### Maman 11 Question 2 (Computational Biology Course) By Guy Vitelson (203379706)
# Environmental Simulation Project

## Overview

This project is a simulation of environmental dynamics using a **cellular automaton** approach. The goal is to model and analyze the interactions between various environmental components, such as oceans, forests, deserts, cities, clouds, air, rain, and vacuum. It incorporates realistic environmental processes like pollution dynamics, temperature changes, and water cycles.


## Features

1. **Cellular Automaton Framework**: 
   - Each cell in the grid represents an environmental element (e.g., forest, ocean, city).
   - The grid evolves over time based on defined rules and interactions between neighboring cells.

2. **Environmental Processes**:
   - Water transfer between clouds, rain, air, and other elements.
   - Pollution dynamics with decay and absorption by forests.
   - Temperature adjustments due to interactions between cells.

3. **Dynamic Elements**:
   - Rain forms in clouds, falls to the ground, and is absorbed by forests or deserts.
   - Cities emit pollution and generate heat, influencing nearby cells.
   - Forests cool the environment and absorb pollution.

4. **Simulation Flexibility**:
   - Adjustable grid size and simulation duration.
   - Configurable environmental parameters (e.g., baseline temperature, pollution thresholds).
   - Customizable initial ratios for different cell types.

5. **Analysis Tools**:
   - Aggregates environmental data (pollution, temperature, city count, forest count) over time.
   - Visualizes the evolution of the environment.

---

## System Design

### 1. **Key Components**

- **World**: Represents the simulation environment, a 3D grid where each cell is a `Particle`. Manages the initialization, updates, and global attributes of the grid.
- **Particle**: Represents an individual cell in the grid with attributes like `cell_type`, `temperature`, `water_mass`, and `pollution_level`. Handles state transitions and interactions with neighbors.
- **Simulation**: Controls the simulation process, including precomputing states, running the simulation for multiple days, and collecting data for analysis.

### 2. **Cell Types**
The simulation uses the following cell types:

| **Type**  | **ID** | **Description**                           |
|-----------|--------|-------------------------------------------|
| Ocean     | 0      | Covers the majority of the grid; evaporates water. |
| Desert    | 1      | Hot and dry; minimal interaction with water. |
| Cloud     | 2      | Forms rain when saturated.                |
| Ice       | 3      | Freezes water in cold temperatures.       |
| Forest    | 4      | Absorbs pollution and cools the environment. |
| City      | 5      | Generates pollution and heat.             |
| Air       | 6      | Transports water and pollution.           |
| Rain      | 7      | Water falling from clouds.                |
| Vacuum    | 8      | Represents empty space; no interaction.   |

---

## Configuration

The `config.py` file contains all the simulation parameters, including:

1. **Grid and Simulation Settings**:
   - `default_grid_size`: Dimensions of the simulation grid.
   - `default_days`: Number of days the simulation runs by default.

2. **Environmental Parameters**:
   - `baseline_temperature`: Default temperature for each cell type.
   - `baseline_pollution_level`: Initial pollution levels for each cell type.
   - `cell_type_weights`: Weights used to resolve collisions between cells.

3. **Dynamic Behavior**:
   - `pollution_damage_threshold`: Level of pollution causing damage to cells.
   - `cloud_saturation_threshold`: Water mass at which clouds turn into rain.
   - `forest_pollution_absorption_rate`: Rate at which forests absorb pollution.

4. **Visualization Settings**:
   - `tint`: Toggle for red-tinted visualization based on pollution.

---

## How It Works

1. **Grid Initialization**:
   - The 3D grid is initialized with cell types distributed based on predefined ratios (e.g., forests, cities, deserts).
   - An elevation map is generated using Perlin noise to simulate realistic terrain.

2. **Simulation Process**:
   - Each day, the grid is updated based on rules specific to each cell type.
   - Water, pollution, and temperature are exchanged between cells.

3. **Data Aggregation**:
   - Global attributes like average temperature and pollution are recalculated after each update.
   - Historical data is stored for analysis.

4. **Collision Resolution**:
   - When multiple cells attempt to occupy the same position, a weighted resolution mechanism decides the final occupant.

---

## Theoretical Basis

The simulation is inspired by cellular automata, a mathematical model used for simulating complex systems through simple local interactions. Theoretical principles applied include:

- **Conservation Laws**: Water and pollution are conserved during transfers between cells.
- **Equilibrium Dynamics**: Cells stabilize temperature and pollution levels based on neighbors.
- **Threshold Effects**: Processes like evaporation and cloud saturation occur only beyond specific thresholds.

### Environmental Dynamics Modeled

1. **Water Cycle**:
   - Evaporation: Water moves from oceans to clouds.
   - Precipitation: Clouds form rain, which falls to the ground.
   - Absorption: Forests and deserts absorb rainwater.

2. **Pollution Dynamics**:
   - Emission: Cities increase pollution levels.
   - Absorption: Forests reduce pollution.
   - Natural Decay: Pollution levels decrease over time.

3. **Temperature Regulation**:
   - Heat Generation: Cities increase local temperatures.
   - Cooling Effect: Forests lower temperatures through natural processes.

---

## Code Overview

### Main Files

1. `Particle.py`: Defines the behavior of individual cells.
2. `World.py`: Manages the 3D grid and global environmental attributes.
3. `Simulation.py`: Controls the simulation process and data aggregation.
4. `config.py`: Stores configurable parameters.

### Key Functions

- **World**:
  - `initialize_grid`: Sets up the grid with initial cell types and attributes.
  - `update_cells_on_grid`: Updates all cells in the grid for one simulation step.
  - `accumulate_water_transfers`: Computes water exchange between neighboring cells.

- **Particle**:
  - `compute_next_state`: Calculates the next state of a cell based on its type and neighbors.
  - `convert_to_*`: Handles state transitions (e.g., air to cloud, cloud to rain).
  - `equilibrate_*`: Balances temperature and pollution between cells.

- **Simulation**:
  - `precompute`: Runs the simulation for a predefined number of days.
  - `analyze`: Aggregates and returns historical data.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/environmental-simulation.git
   cd environmental-simulation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulation:
   ```bash
   python main.py
   ```

## Example Output

[UI Results, without tint color](./docs/ui_print_screen_01.png)