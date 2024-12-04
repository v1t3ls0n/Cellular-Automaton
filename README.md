```markdown
# Environmental Cellular Automaton Simulation

## Overview
This project implements a **Cellular Automaton Model** to simulate environmental dynamics. It provides insights into interactions between various elements such as forests, cities, oceans, and pollution levels. The simulation is customizable and visualizes data using 3D representations and statistical graphs.

---

## Features
- **Environmental Simulation**:
  - Models diverse cell types (e.g., Ocean, Forest, City, Air, etc.).
  - Captures dynamic behaviors like pollution diffusion, temperature equilibrium, and water transfer.
- **Customizable Configurations**:
  - Default presets provided in `conf_presets.py`.
  - Custom configurations can be loaded and applied dynamically.
- **Visualization**:
  - Real-time 3D grid visualization.
  - Graphs for pollution, temperature, forest/city populations, and other metrics.
- **Dynamic Interactions**:
  - Rules for cell transitions based on their states and neighbors.

---

## File Structure

### `config/`
This directory manages configuration presets and runtime configurations.

#### `conf_presets.py`
- Contains predefined environmental scenarios.
- Variables:
  - `DEFAULT_PRESET`: Specifies the default configuration to be used.
  - `PRESETS`: A dictionary of named configurations, including:
    - `Low Air Pollution - Stable Environment`.
    - `High Air Pollution - Mass Extinction Scenario`.
- Functions:
  - `get_preset(preset_name: str) -> dict`: Retrieves the configuration for a given preset.

#### `config_state_handler.py`
- Handles the loading and validation of simulation configurations.
- Key Methods:
  - `get_config() -> dict`: Returns the currently active configuration.
  - `validate_config(config: dict) -> None`: Ensures the configuration follows expected rules.
  - `set_config(new_config: dict) -> None`: Allows dynamic updates to the configuration.

---

### `core/`
The heart of the simulation, containing logic for particles, the world grid, and simulation updates.

#### `Particle.py`
- Implements the behavior of individual cells in the simulation.
- Classes:
  - `Particle`:
    - Attributes:
      - `cell_type`: Type of the cell (e.g., air, ocean, city).
      - `temperature`, `water_mass`, `pollution_level`: Environmental properties.
      - `direction`: Movement direction in the grid.
      - `position`: Current (x, y, z) location in the grid.
    - Methods:
      - `clone()`: Creates a copy of the particle.
      - `get_next_position()`: Calculates the next position based on `direction`.
      - `compute_next_state(neighbors: list) -> Particle`: Computes the next state by considering neighboring particles.
      - Cell-specific updates:
        - `_update_ocean()`
        - `_update_forest()`
        - `_update_city()`
        - `_update_cloud()`, etc.

#### `World.py`
- Manages the 3D grid and interactions between cells.
- Classes:
  - `World`:
    - Attributes:
      - `grid_size`: Dimensions of the grid.
      - `grid`: A 3D array of `Particle` objects.
    - Methods:
      - `initialize_grid()`: Sets up the grid with cells based on initial configurations.
      - `update_cells_on_grid()`: Updates the state of all cells.
      - `clone()`: Creates a copy of the world.
      - `accumulate_water_transfers()`: Handles water redistribution among neighboring cells.

#### `Simulation.py`
- Controls the simulation loop and manages time steps.
- Classes:
  - `Simulation`:
    - Attributes:
      - `world`: An instance of the `World` class.
    - Methods:
      - `run_step()`: Executes one time step of the simulation.
      - `run_simulation()`: Runs the simulation for a specified number of steps.

---

### `display/`
This directory contains utilities for visualizing simulation data.

#### `MatplotlibDisplay.py`
- Handles real-time plotting of graphs and metrics.
- Functions:
  - `plot_metric_over_time(metric_data: list, metric_name: str)`: Plots a specific metric (e.g., pollution).
  - `visualize_3d_grid(grid: np.array)`: Generates a 3D visualization of the grid.

---

### `utils/`
Contains auxiliary scripts.

#### `.gitignore`
- Specifies files and directories to ignore in version control.

#### `git_update.sh`
- Automates git updates (e.g., pulling changes or committing code).

---

### Root Files

#### `main.py`
- The entry point for the simulation.
- Handles:
  - Initializing configurations.
  - Running the simulation loop.
  - Displaying results.

---

## Installation

1. Clone the repository:
   ```bash
   git clone [repository URL]
   cd [repository folder]
   ```
2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the simulation:
   ```bash
   python main.py
   ```

---

## Usage

### Running a Simulation
- Edit `conf_presets.py` or create a custom configuration in `config_state_handler.py`.
- Run the simulation:
  ```bash
  python main.py
  ```

### Visualizations
- 3D visualization: Displays the grid and the state of each cell.
- Statistical graphs:
  - Pollution over time.
  - Temperature variations.
  - City/forest population trends.

### Configuration
- Modify the following parameters:
  - `grid_size`: Dimensions of the simulation space.
  - `baseline_temperature` and `baseline_pollution_level`: Starting environmental conditions.
  - `initial_ratios`: Proportion of each cell type.

---

## Example Output

### 3D Visualization
- A real-time 3D representation of the simulation grid:
  ![3D Visualization](Graphic%20Interface.png)

### Statistical Graphs
- Pollution, temperature, and population metrics over time.

---

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit and push your changes.
4. Open a pull request.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

### Contact
- **Developer**: Guy Vitelson (aka v1t3ls0n on GitHub)
```