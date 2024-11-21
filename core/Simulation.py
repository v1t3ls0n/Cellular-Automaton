import numpy as np
from .State import State
from .Cell import Cell
import matplotlib.pyplot as plt
import logging

class Simulation:
    def __init__(self, initial_pollution, initial_temperature, initial_water_mass, initial_cities, initial_forests, grid_size = (10,10,10), days = 5):

        self.grid_size = grid_size,
        self.initial_temperature = initial_temperature,
        self.initial_pollution = initial_pollution,
        self.initial_water_mass = initial_water_mass,
        self.initial_cities = initial_cities,
        self.initial_forests = initial_forests


        
        self.days = days
        self.states = []
        # Initialize the first state
        initial_state = State(
           grid_size,
           initial_temperature,
           initial_pollution,
           initial_water_mass,
           initial_cities,
           initial_forests,
           prev_state_index = -1
        )

        self.states.append(initial_state)

    def precompute(self):
        """Precompute all states for the simulation."""
        print(f"self.states:{self.states[-1]}")

        logging.info("Precomputing all states...")

        for day in range(1, self.days + 1):
            next_state = self.states[-1].next_state()
            self.states.append(next_state)

        logging.info("Precomputed all states.")

class Simulation:
    def __init__(self, initial_pollution, initial_temperature, initial_water_mass, initial_cities, initial_forests, grid_size=(10, 10, 10), days=5):
        """
        Initialize the Simulation class with initial conditions.
        """
        self.grid_size = grid_size
        self.initial_temperature = initial_temperature
        self.initial_pollution = initial_pollution
        self.initial_water_mass = initial_water_mass
        self.initial_cities = initial_cities
        self.initial_forests = initial_forests
        self.days = days

        self.states = []  # Store the history of State objects
        self.avg_temperature = []
        self.avg_pollution = []
        self.avg_water_mass = []
        self.city_counts = []
        self.forest_counts = []

        # Initialize the first state
        initial_state = State(
            grid_size=self.grid_size,
            initial_temperature=self.initial_temperature,
            initial_pollution=self.initial_pollution,
            initial_water_mass=self.initial_water_mass,
            initial_cities=self.initial_cities,
            initial_forests=self.initial_forests,
        )
        self.states.append(initial_state)

    def _calculate_aggregates(self):
        """
        Compute and store aggregates for all states (pollution, temperature, water mass, city count, forest count).
        These aggregates are stored as arrays to track changes over time.
        """
        self.pollution_over_time = []
        self.temperature_over_time = []
        self.water_mass_over_time = []
        self.city_population_over_time = []
        self.forest_count_over_time = []

        for state in self.states:
            total_pollution = 0
            total_temperature = 0
            total_water_mass = 0
            city_count = 0
            forest_count = 0
            total_cells = 0

            for i in range(state.grid.shape[0]):
                for j in range(state.grid.shape[1]):
                    for k in range(state.grid.shape[2]):
                        cell = state.grid[i, j, k]
                        if cell.cell_type != 6:  # Exclude air cells
                            total_cells += 1
                            total_pollution += cell.pollution_level
                            total_temperature += cell.temperature
                            total_water_mass += cell.water_mass
                            if cell.cell_type == 5:
                                city_count += 1
                            elif cell.cell_type == 4:
                                forest_count += 1

            # Compute averages
            avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
            avg_temperature = total_temperature / total_cells if total_cells > 0 else 0
            avg_water_mass = total_water_mass / total_cells if total_cells > 0 else 0

            # Append to history lists
            self.pollution_over_time.append(avg_pollution)
            self.temperature_over_time.append(avg_temperature)
            self.water_mass_over_time.append(avg_water_mass)
            self.city_population_over_time.append(city_count)
            self.forest_count_over_time.append(forest_count)

        logging.info(f"Aggregate calculation complete for {len(self.states)} states.")


    def run(self):
        """
        Simulate the environment for the specified number of days.
        """
        logging.info("Simulation started.")
        for day in range(1, self.days + 1):
            logging.info("Simulating day %d...", day)
            current_state = self.states[-1]
            next_state = current_state.next_state()  # Calculate the next state
            self.states.append(next_state)  # Append the new state to the history

        logging.info("Simulation complete.")

    def get_averages_over_time(self):
        """
        Retrieve averages and counts over time.
        """
        return {
            "temperature": self.avg_temperature,
            "pollution": self.avg_pollution,
            "water_mass": self.avg_water_mass,
            "cities": self.city_counts,
            "forests": self.forest_counts,
        }

    def get_state_by_day(self, day):
        """
        Retrieve the state object for a specific day.
        :param day: The day index (0-based).
        :return: The State object for the given day.
        """
        if 0 <= day < len(self.states):
            return self.states[day]
        else:
            raise IndexError("Invalid day index.")

    def log_summary(self):
        """
        Log a summary of the simulation results.
        """
        logging.info("Simulation Summary:")
        averages = self.get_averages_over_time()
        logging.info("Average Temperature Over Time: %s", averages["temperature"])
        logging.info("Average Pollution Over Time: %s", averages["pollution"])
        logging.info("Average Water Mass Over Time: %s", averages["water_mass"])
        logging.info("City Population Over Time: %s", averages["cities"])
        logging.info("Forest Count Over Time: %s", averages["forests"])

    def analyze(self):
        """
        Analyze the simulation history and return aggregates.
        """
        if not hasattr(self, 'pollution_over_time'):
            self._calculate_aggregates()  # Calculate if not already done

        return {
            "pollution": self.pollution_over_time,
            "temperature": self.temperature_over_time,
            "water_mass": self.water_mass_over_time,
            "cities": self.city_population_over_time,
            "forests": self.forest_count_over_time,
        }

# Example usage:
# sim = Simulation(grid_size=(10, 10, 10), initial_temperature=20, initial_pollution=5, initial_water_mass=10)
# sim.simulate()
# sim.visualize()
# sim.visualize_3d(day=100)
