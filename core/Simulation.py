from core.World import World  # Import the World class
import logging
import numpy as np

class Simulation:
    """
    The Simulation class is responsible for managing the lifecycle of a simulation,
    including initialization, precomputing states over a specified number of days,
    and analyzing results.
    """

    def __init__(self, grid_size, initial_ratios, days):
        """
        Initialize the Simulation class with initial conditions.

        Args:
            grid_size (tuple): Dimensions of the grid (x, y, z).
            initial_ratios (dict): Initial ratios for different cell types (e.g., forest, city, desert).
            days (int): Number of days to run the simulation.
        """
        self.grid_size = grid_size
        self.initial_ratios = initial_ratios
        self.days = days
        self.states = []  # Store the history of World objects (one per day)
        # Aggregates to track various metrics over time
        self.pollution_over_time = []  # Average pollution over time
        self.temperature_over_time = []  # Average temperature over time
        self.city_population_over_time = []  # Total number of city cells over time
        self.forest_count_over_time = []  # Total number of forest cells over time
        self.water_mass_over_time = []  # Average water mass over time
        self.std_dev_pollution_over_time = []  # Standard deviation of pollution
        self.std_dev_temperature_over_time = []  # Standard deviation of temperature
        self.std_dev_water_mass_over_time = []  # Standard deviation of water mass
        # Track counts of each cell type
        self.cell_type_counts_over_time = {
            cell_type: [] for cell_type in range(10)}
        self.cell_type_std_dev_over_time = {
            # Track std dev per cell type
            cell_type: [] for cell_type in range(10)}
        # Standard deviation of cell type distribution over time
        self.std_dev_cell_distribution_over_time = []
        self.std_dev_forest_count_over_time = []  # Standard deviation of forest count
        # Standard deviation of city population
        self.std_dev_city_population_over_time = []



    def precompute(self):
        """
        Run the simulation for the specified number of days and precompute all states.
        This function initializes the grid and iteratively updates it for each day.

        Steps:
        1. Initialize the first state (Day 0).
        2. For each day, clone the last state, update it, and store it.
        3. Update aggregates for analysis.
        """
        # Initialize the first state (Day 0)
        initial_state = World(
            grid_size=self.grid_size,
            initial_ratios=self.initial_ratios,
            day_number=0
        )
        initial_state.initialize_grid()
        self.states.append(initial_state)
        self._update_aggregates(initial_state)  # Update aggregates for Day 0

        # # Simulate for the specified number of days
        for day in range(self.days):
            logging.info(f"Pre-computing Day {day}...")

            # Compute the next state by cloning the current state
            next_state = self.states[-1].clone()
            next_state.day_number += 1  # Increment the day number
            next_state.update_cells_on_grid()  # Update the grid cells
            next_state._recalculate_global_attributes()  # Recalculate global attributes
            self.states.append(next_state)  # Store the new state
            self._update_aggregates(next_state)  # Update aggregates
        
        self.print_simulation_metrics()


    def _update_aggregates(self, state):
        """
        Update aggregate metrics based on the current state of the simulation.

        Args:
            state (World): Current World object representing the state of the grid.
        """
        # Append spatial averages from World
        self.pollution_over_time.append(state.avg_pollution)
        self.temperature_over_time.append(state.avg_temperature)
        self.water_mass_over_time.append(state.avg_water_mass)
        self.city_population_over_time.append(state.total_cities)
        self.forest_count_over_time.append(state.total_forests)

        # Append spatial std devs from World
        self.std_dev_pollution_over_time.append(state.std_dev_pollution)
        self.std_dev_temperature_over_time.append(state.std_dev_temperature)
        self.std_dev_water_mass_over_time.append(state.std_dev_water_mass)

        # Calculate temporal std devs dynamically
        self.std_dev_forest_count_over_time.append(
            np.std(self.forest_count_over_time) if len(self.forest_count_over_time) > 1 else 0
        )
        self.std_dev_city_population_over_time.append(
            np.std(self.city_population_over_time) if len(self.city_population_over_time) > 1 else 0
        )


    def print_simulation_metrics(self):
        logging.info("\n===== Simulation Metrics =====\n")
        
        logging.info("** Pollution Metrics **")
        logging.info(f"Average Pollution Over Time: {self.pollution_over_time}")
        logging.info(f"Standard Deviation of Pollution Over Time: {self.std_dev_pollution_over_time}\n")
        
        logging.info("** Temperature Metrics **")
        logging.info(f"Average Temperature Over Time: {self.temperature_over_time}")
        logging.info(f"Standard Deviation of Temperature Over Time: {self.std_dev_temperature_over_time}\n")
        
        logging.info("** Water Mass Metrics **")
        logging.info(f"Average Water Mass Over Time: {self.water_mass_over_time}")
        logging.info(f"Standard Deviation of Water Mass Over Time: {self.std_dev_water_mass_over_time}\n")
        
        logging.info("** City and Forest Metrics **")
        logging.info(f"City Population Over Time: {self.city_population_over_time}")
        logging.info(f"Standard Deviation of City Population: {self.std_dev_city_population_over_time}")
        logging.info(f"Forest Count Over Time: {self.forest_count_over_time}")
        logging.info(f"Standard Deviation of Forest Count: {self.std_dev_forest_count_over_time}\n")
        
        logging.info("** Cell Type Metrics **")
        for cell_type, counts in self.cell_type_counts_over_time.items():
            logging.info(f"Cell Type {cell_type} Counts Over Time: {counts}")
        for cell_type, std_devs in self.cell_type_std_dev_over_time.items():
            logging.info(f"Cell Type {cell_type} Std Dev Over Time: {std_devs}\n")
        
        logging.info("** Cell Distribution Metrics **")
        logging.info(f"Standard Deviation of Cell Distribution Over Time: {self.std_dev_cell_distribution_over_time}")
        logging.info("\n=================================\n")
