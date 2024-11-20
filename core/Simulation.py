import numpy as np
from .State import State
from .Cell import Cell
import matplotlib.pyplot as plt


class Simulation:
    def __init__(self, grid_size, days,  initial_pollution, initial_temperature, initial_water_mass, initial_cities=None, initial_forests=None,):
        self.grid_size = grid_size
        self.days = days
        self.initial_cities = initial_cities
        self.initial_forests = initial_forests
        self.initial_pollution = initial_pollution
        self.initial_temperature = initial_temperature
        self.initial_water_mass = initial_water_mass
        self.states = []

        # Initialize the first state
        initial_state = State(
            grid_size=self.grid_size,
            initial_cities=self.initial_cities,
            initial_forests=self.initial_forests,
            initial_pollution=self.initial_pollution,
            initial_temperature=self.initial_temperature,
            initial_water_mass=self.initial_water_mass,
        )
        self.states.append(initial_state)

    def precompute(self):
        """Precompute all states for the simulation."""
        print(f"self.states:{self.states[-1]}")
        for day in range(1, self.days + 1):
            next_state = self.states[-1].next_state()
            self.states.append(next_state)

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
        Generates data for pollution, temperature, and other attributes.
        """
        pollution_over_time = []
        temperature_over_time = []
        city_count_over_time = []
        forest_count_over_time = []

        for state in self.states:
            total_pollution = 0
            total_temperature = 0
            total_cities = 0
            total_forests = 0
            total_cells = 0

            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    for k in range(self.grid_size[2]):
                        cell = state.grid[i, j, k]
                        if cell.cell_type != 6:  # Exclude air cells
                            total_pollution += cell.pollution_level
                            total_temperature += cell.temperature
                            total_cells += 1

                            if cell.cell_type == 5:  # City
                                total_cities += 1
                            elif cell.cell_type == 4:  # Forest
                                total_forests += 1

            # Compute averages and save for graphing
            avg_pollution = total_pollution / total_cells if total_cells > 0 else 0
            avg_temperature = total_temperature / total_cells if total_cells > 0 else 0

            pollution_over_time.append(avg_pollution)
            temperature_over_time.append(avg_temperature)
            city_count_over_time.append(total_cities)
            forest_count_over_time.append(total_forests)

        return pollution_over_time, temperature_over_time, city_count_over_time, forest_count_over_time

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
