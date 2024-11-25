import logging
from core.State import State  # Import the State class

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

        # Initialize aggregates
        self.pollution_over_time = []
        self.temperature_over_time = []
        self.water_mass_over_time = []
        self.city_population_over_time = []
        self.forest_count_over_time = []


    def _update_aggregates(self, state):
        """
        Update aggregates based on the current state's attributes.
        """
        self.pollution_over_time.append(state.avg_pollution)
        self.temperature_over_time.append(state.avg_temperature)
        self.water_mass_over_time.append(state.avg_water_mass)
        self.city_population_over_time.append(state.total_cities)
        self.forest_count_over_time.append(state.total_forests)

        logging.debug(
            f"Updated aggregates - Pollution: {state.avg_pollution}, Temperature: {state.avg_temperature}, "
            f"Water Mass: {state.avg_water_mass}, Cities: {state.total_cities}, Forests: {state.total_forests}"
        )

    def run(self):
        """
        Run the simulation for the specified number of days.
        """
        logging.info("Simulation started.")
        
        # Initialize the first state
        initial_state = State(
            grid_size=self.grid_size,
            initial_temperature=self.initial_temperature,
            initial_pollution=self.initial_pollution,
            initial_water_mass=self.initial_water_mass,
            initial_cities=self.initial_cities,
            initial_forests=self.initial_forests,
            prev_state_index=-1
        )
        initial_state.initialize_grid(
            initial_temperature=self.initial_temperature,
            initial_pollution=self.initial_pollution,
            initial_water_mass=self.initial_water_mass,
            initial_cities=self.initial_cities,
            initial_forests=self.initial_forests
        )
        
        self.states.append(initial_state)
        self._update_aggregates(initial_state)

        for day in range(self.days):
            logging.info(f"Simulating day {day + 1}...")

            # Get the current state
            current_state = self.states[-1].clone()
            logging.debug(f"Current state (Day {day + 1}): {current_state}")

            # Compute the next state by cloning and updating
            next_state = current_state.clone()
            next_state.move_cells_on_grid()
            next_state.update_cells_on_grid()
            next_state.prev_state_index = day + 1

            # Append the new state and update aggregates
            self.states.append(next_state)
            self._update_aggregates(next_state)

            logging.debug(f"Next state (Day {day + 1}) added.")

        logging.info("Simulation complete.")

    def analyze(self):
        """
        Analyze the simulation history and return aggregates.
        """
        return {
            "pollution": self.pollution_over_time,
            "temperature": self.temperature_over_time,
            "water_mass": self.water_mass_over_time,
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
            "water_mass": self.water_mass_over_time,
            "cities": self.city_population_over_time,
            "forests": self.forest_count_over_time,
        }
