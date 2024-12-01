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
        self.cell_type_counts_over_time = {cell_type: [] for cell_type in range(10)}  # Track counts of each cell type
        self.cell_type_std_dev_over_time = {cell_type: [] for cell_type in range(10)}  # Track std dev per cell type
        self.std_dev_cell_distribution_over_time = []  # Standard deviation of cell type distribution over time

    def _update_aggregates(self, state):
        self.pollution_over_time.append(state.avg_pollution)
        self.temperature_over_time.append(state.avg_temperature)
        self.city_population_over_time.append(state.total_cities)
        self.forest_count_over_time.append(state.total_forests)
        self.water_mass_over_time.append(state.avg_water_mass)
        self.std_dev_pollution_over_time.append(state.std_dev_pollution)
        self.std_dev_temperature_over_time.append(state.std_dev_temperature)
        self.std_dev_water_mass_over_time.append(state.std_dev_water_mass)

        for cell_type, stats in state.cell_type_stats.items():
            self.cell_type_std_dev_over_time[cell_type].append(stats["std_dev_temperature"])
            self.cell_type_counts_over_time[cell_type].append(stats["count"])

        cell_counts = [stats["count"] for stats in state.cell_type_stats.values()]
        if len(cell_counts) > 0:
            std_dev_distribution = np.std(cell_counts)
            self.std_dev_cell_distribution_over_time.append(std_dev_distribution)
        else:
            self.std_dev_cell_distribution_over_time.append(0)
        logging.info(f"Day {state.day_number}: Total forests = {state.total_forests}")
        logging.info(f"Aggregated forest count: {self.forest_count_over_time}")

            
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

        # Simulate for the specified number of days
        for day in range(self.days):
            logging.info(f"Day {day}...")

            # Compute the next state by cloning the current state
            next_state = self.states[-1].clone()
            next_state.day_number += 1  # Increment the day number
            next_state.update_cells_on_grid()  # Update the grid cells
            next_state._recalculate_global_attributes()  # Recalculate global attributes
            self.states.append(next_state)  # Store the new state
            self._update_aggregates(next_state)  # Update aggregates

    def get_averages_and_std_dev_over_time(self):
        """
        Retrieve averages and standard deviations of metrics over the simulation period.

        Returns:
            dict: Averages and standard deviations of temperature, pollution, water mass, 
                  city counts, forest counts, and cell type counts.
        """
        return {
            "averages": {
                "temperature": self.temperature_over_time,
                "pollution": self.pollution_over_time,
                "water_mass": self.water_mass_over_time,
                "cities": self.city_population_over_time,
                "forests": self.forest_count_over_time,
                "cell_type_counts": self.cell_type_counts_over_time,
            },
            "std_devs": {
                "temperature": self.std_dev_temperature_over_time,
                "pollution": self.std_dev_pollution_over_time,
                "water_mass": self.std_dev_water_mass_over_time,
            }
        }

    def calculate_statistics(self):
        """
        Calculate mean and standard deviation for each parameter over the entire simulation.

        Returns:
            dict: Mean and standard deviation for each parameter.
        """
        data = self.get_averages_and_std_dev_over_time()["averages"]
        stats = {}
        for param, values in data.items():
            if param == "cell_type_counts":
                stats[param] = {
                    cell_type: {
                        "mean": np.mean(counts),
                        "std_dev": np.std(counts)
                    }
                    for cell_type, counts in values.items()
                }
            else:
                stats[param] = {
                    "mean": np.mean(values),
                    "std_dev": np.std(values)
                }
        return stats
