Here is an analysis of the extracted project structure to help draft the `README.md` file:

### Project Structure:
1. **Root Directory:**
   - `main.py`: Likely the main entry point for the application.
   - `cli_output.log`: Log file; possibly from previous executions.
   - `Graphic Interface.png`: Screenshot or diagram for the graphic interface.

2. **`config` Directory:**
   - `config_state_handler.py`: Handles configurations related to states.
   - `conf_presets.py`: Contains preset configurations.

3. **`core` Directory:**
   - `Particle.py`, `Simulation.py`, `World.py`: Core components for the simulation.
   - `__init__.py`: Indicates this is a package.

4. **`display` Directory:**
   - `MatplotlibDisplay.py`: Likely responsible for visualization using Matplotlib.
   - `__init__.py`: Indicates this is a package.

5. **`utils` Directory:**
   - `helpers.py`: Contains utility functions.
   - `__pycache__/helpers.cpython-312.pyc`: Compiled Python bytecode.

### README.md Content

```markdown
# Simulation Project

## Overview
This project provides a modular simulation framework designed to model and visualize particle-based systems. The application supports custom configurations, visual displays, and flexible simulation logic.

## Features
- **Customizable Configurations**: Easily adjust settings and presets via configuration files.
- **Dynamic Simulation Core**: Models particles and their interactions within a simulated world.
- **Visualization**: Supports graphical outputs using Matplotlib.
- **Command-line Interface**: Logs execution details for troubleshooting and optimization.

## Project Structure
```
```plaintext
.
├── main.py                    # Main entry point of the application
├── cli_output.log             # Log file containing CLI execution output
├── Graphic Interface.png      # Image representing the graphical interface
├── config/                    # Configuration files
│   ├── config_state_handler.py
│   └── conf_presets.py
├── core/                      # Core simulation logic
│   ├── Particle.py
│   ├── Simulation.py
│   ├── World.py
│   └── __init__.py
├── display/                   # Visualization modules
│   ├── MatplotlibDisplay.py
│   └── __init__.py
└── utils/                     # Utility functions
    ├── helpers.py
    └── __pycache__/helpers.cpython-312.pyc
```
```

## Installation
1. Clone this repository or download the ZIP file and extract it.
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```
2. Install required dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application.
   ```bash
   python main.py
   ```

## Usage
1. Adjust configuration files in the `config` directory to suit your simulation requirements.
2. Launch the simulation with:
   ```bash
   python main.py
   ```
3. Logs are stored in `cli_output.log` for later review.

## Visualization
- The simulation's graphical output is generated using Matplotlib. Refer to the file `Graphic Interface.png` for a sample interface.

## Modules
- **Main (`main.py`)**: Starts the simulation and coordinates between modules.
- **Core (`core/`)**:
  - `Particle.py`: Manages individual particle behavior.
  - `Simulation.py`: Handles the overall simulation lifecycle.
  - `World.py`: Defines the environment and its properties.
- **Config (`config/`)**:
  - `config_state_handler.py`: Loads and manages configuration states.
  - `conf_presets.py`: Provides default settings and presets.
- **Display (`display/`)**: Renders the simulation using Matplotlib.
- **Utils (`utils/`)**: Helper functions for reusable logic.

## Contributing
1. Fork the repository.
2. Create a feature branch.
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes and push to the branch.
4. Open a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Acknowledgments
Special thanks to the contributors and open-source libraries used in this project.
```

This README.md file is ready to use or customize further based on specific project goals or details. Let me know if you need any modifications!