from core.old.World import World  # Import the World class
import logging

class Simulation:
    def __init__(self, grid_size, initial_ratios, days):
        """
        Initialize the Simulation class with initial conditions.
        """
        self.grid_size = grid_size
        self.initial_ratios = initial_ratios
        self.days = days

        self.states = []  # Store the history of World objects
        # Initialize aggregates
        self.pollution_over_time = []
        self.temperature_over_time = []
        self.city_population_over_time = []
        self.forest_count_over_time = []

    def _update_aggregates(self, state):
        """
        Update aggregates based on the current state's attributes.
        """
        self.pollution_over_time.append(state.avg_pollution)
        self.temperature_over_time.append(state.avg_temperature)
        self.city_population_over_time.append(state.total_cities)
        self.forest_count_over_time.append(state.total_forests)

    def precompute(self):
        """
        Run the simulation for the specified number of days.
        """
        # Initialize the first state
        initial_state = World(
            grid_size=self.grid_size,
            initial_ratios=self.initial_ratios,
            day_number=0
        )
        initial_state.initialize_grid()
        self.states.append(initial_state)
        self._update_aggregates(initial_state)

        for day in range(self.days):
            logging.info(f"Day {day + 1}...")
            # Compute the next state by cloning and updating
            next_state = self.states[-1].clone()
            next_state.day_number += 1
            next_state.update_cells_on_grid()
            self.states.append(next_state)
            self._update_aggregates(next_state)
            logging.debug(f"Next state (Day {day + 1}) added.")

    def analyze(self):
        """
        Analyze the simulation history and return aggregates.
        """
        return {
            "pollution": self.pollution_over_time,
            "temperature": self.temperature_over_time,
            "cities": self.city_population_over_time,
            "forests": self.forest_count_over_time,
        }

    def get_averages_over_time(self):
        """
        Retrieve averages and counts over time.
        """
        return {
            "temperature": self.temperature_over_time,
            "pollution": self.pollution_over_time,
            "cities": self.city_population_over_time,
            "forests": self.forest_count_over_time,
        }
