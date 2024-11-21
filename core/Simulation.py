import numpy as np
from .State import State
from .Cell import Cell
import matplotlib.pyplot as plt
import logging

class Simulation:
    def __init__(self, grid_size, days,  initial_pollution, initial_temperature, initial_water_mass, initial_cities, initial_forests):

        self.grid_size = grid_size,
        self.initial_temperature = initial_temperature,
        self.initial_pollution = initial_pollution,
        self.initial_water_mass = initial_water_mass,
        self.initial_cities = initial_cities,
        self.initial_forests = initial_forests
        print("initial Simulation paramaters:")
        print(f"grid_size : {grid_size}")
        print(f"temperature : {initial_temperature}")
        print(f"pollution : {initial_pollution}")
        print(f"initial_cities : {initial_cities}")
        print(f"initial_forests : {initial_forests}")
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


    def run(self):
        """Run the simulation."""
        for day in range(self.days):
            print(f"Simulating day {day + 1}...")
            next_state = self.states[-1].next_state()
            self.states.append(next_state)

    def simulate(self):
        """
        Run the simulation for the defined number of days.
        """
        print(f"Starting simulation for {self.days} days...")
        for day in range(self.days - 1):  # Iterate over all days
            print(f"Simulating day {day + 1}...")
            # Copy the current state to the next day's state and calculate the next state
            self.states[day + 1].grid = np.copy(self.states[day].grid)
            self.states[day + 1].next_state()

        print("Simulation complete.")

    def analyze(self):
        """
        Analyze the simulation data for trends over time.
        Generates data for pollution, temperature, water mass, city population, and forests.
        """
        logging.info("Analyzing simulation results...")

        pollution_over_time = []
        temperature_over_time = []
        water_mass_over_time = []
        city_population_over_time = []
        forest_count_over_time = []

        for state in self.states:
            total_pollution, total_temperature, total_water_mass = 0, 0, 0
            city_count, forest_count = 0, 0

            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x, y, z]
                        if cell.cell_type != 6:  # Exclude air cells
                            total_pollution += cell.pollution_level
                            total_temperature += cell.temperature
                            total_water_mass += cell.water_mass

                            if cell.cell_type == 5:  # City
                                city_count += 1
                            elif cell.cell_type == 4:  # Forest
                                forest_count += 1

            # Compute averages and save for graphing
            total_cells = state.grid.size
            avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
            avg_temperature = total_temperature / total_cells if total_cells > 0 else 0
            avg_water_mass = total_water_mass / total_cells if total_cells > 0 else 0

            pollution_over_time.append(avg_pollution)
            temperature_over_time.append(avg_temperature)
            water_mass_over_time.append(avg_water_mass)
            city_population_over_time.append(city_count)  # Count of cities on this day
            forest_count_over_time.append(forest_count)  # Count of forests on this day
       
        logging.debug("Pollution over time: %s", pollution_over_time)
        logging.debug("Temperature over time: %s", temperature_over_time)
        logging.debug("City population over time: %s", city_population_over_time)
        logging.debug("Forest count over time: %s", forest_count)
        logging.debug("Water mass over time: %s", water_mass_over_time)

        return (
            pollution_over_time,
            temperature_over_time,
            water_mass_over_time,
            city_population_over_time,
            forest_count_over_time,
        )

    def visualize(self):
        """
        Generate graphs based on simulation data.
        """
        pollution, temperature, city_count, forest_count = self.analyze()

        # Create subplots for graphs
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Pollution over time
        axes[0, 0].plot(pollution, color='red', label='Pollution')
        axes[0, 0].set_title("Pollution Over Time")
        axes[0, 0].set_xlabel("Day")
        axes[0, 0].set_ylabel("Average Pollution")
        axes[0, 0].legend()

        # Temperature over time
        axes[0, 1].plot(temperature, color='blue', label='Temperature')
        axes[0, 1].set_title("Temperature Over Time")
        axes[0, 1].set_xlabel("Day")
        axes[0, 1].set_ylabel("Average Temperature")
        axes[0, 1].legend()

        # City count over time
        axes[1, 0].plot(city_count, color='purple', label='Cities')
        axes[1, 0].set_title("City Count Over Time")
        axes[1, 0].set_xlabel("Day")
        axes[1, 0].set_ylabel("Number of Cities")
        axes[1, 0].legend()

        # Forest count over time
        axes[1, 1].plot(forest_count, color='green', label='Forests')
        axes[1, 1].set_title("Forest Count Over Time")
        axes[1, 1].set_xlabel("Day")
        axes[1, 1].set_ylabel("Number of Forests")
        axes[1, 1].legend()

        plt.tight_layout()
        plt.show()

    def visualize_3d(self, day=None):
        """
        Visualize the 3D grid of a specific day.
        :param day: The day to visualize (default is the current day).
        """
        if day is None:
            day = self.current_day

        if 0 <= day < self.days:
            self.states[day].visualize()
        else:
            print(f"Day {day} is out of range (0-{self.days - 1}).")


# Example usage:
# sim = Simulation(grid_size=(10, 10, 10), initial_temperature=20, initial_pollution=5, initial_water_mass=10)
# sim.simulate()
# sim.visualize()
# sim.visualize_3d(day=100)
