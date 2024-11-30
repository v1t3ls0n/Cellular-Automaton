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

        # Standard deviation tracking
        self.std_dev_pollution = []
        self.std_dev_temperature = []
        self.std_dev_cities = []
        self.std_dev_forests = []


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

        # Standard deviation tracking
        self.std_dev_pollution = []
        self.std_dev_temperature = []
        self.std_dev_cities = []
        self.std_dev_forests = []

    def _update_aggregates(self, state):
        """
        Update aggregate metrics based on the current state.

        Args:
            state (World): The current state of the world.
        """
        self.pollution_over_time.append(state.avg_pollution)
        self.temperature_over_time.append(state.avg_temperature)
        self.city_population_over_time.append(state.total_cities)
        self.forest_count_over_time.append(state.total_forests)

        # Calculate standard deviation for each metric
        self.std_dev_pollution.append(np.std(self.pollution_over_time))
        self.std_dev_temperature.append(np.std(self.temperature_over_time))
        self.std_dev_cities.append(np.std(self.city_population_over_time))
        self.std_dev_forests.append(np.std(self.forest_count_over_time))

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
            logging.info(f"Day {day + 1}...")

            # Compute the next state by cloning the current state
            next_state = self.states[-1].clone()
            next_state.day_number += 1  # Increment the day number
            next_state.update_cells_on_grid()  # Update the grid cells
            self.states.append(next_state)  # Store the new state
            self._update_aggregates(next_state)  # Update aggregates
            # logging.info(f"Next state (Day {day + 1}) added.")

    def get_averages_and_std_dev_over_time(self):
            """
            Retrieve averages and standard deviations of metrics over the simulation period.

            Returns:
                dict: Averages and standard deviations of temperature, pollution, city counts, and forest counts.
            """
            return {
                "averages": {
                    "temperature": self.temperature_over_time,
                    "pollution": self.pollution_over_time,
                    "cities": self.city_population_over_time,
                    "forests": self.forest_count_over_time,
                },
                "std_devs": {
                    "temperature": self.std_dev_temperature,
                    "pollution": self.std_dev_pollution,
                    "cities": self.std_dev_cities,
                    "forests": self.std_dev_forests,
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
                stats[param] = {
                    "mean": np.mean(values),
                    "std_dev": np.std(values)
                }
            return stats