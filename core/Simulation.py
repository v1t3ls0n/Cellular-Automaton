import numpy as np
from core.State import State
from core.Cell import Cell
from copy import deepcopy

class Simulation:
    def __init__(self, grid_size, days, initial_cities=None, initial_forests=None, initial_pollution=None, initial_temperature=None, initial_water_level=None):
        self.grid_size = grid_size
        self.days = days
        self.states = []  # Initialize an empty list to store states
        self.precomputed_results = []  # Store precomputed states for all days

        if all(param is not None for param in [initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level]):
            # Create the initial state with dynamic input
            initial_state = self.create_dynamic_initial_state(initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level)
        else:
            # Create the initial state with default settings
            initial_state = self.create_default_initial_state()

        self.states.append(initial_state)

    def create_default_initial_state(self):
        """Create an initial state using the grid size with default values."""
        return State(self.grid_size)

    def create_dynamic_initial_state(self, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level):
        """Create an initial state with dynamic parameters."""
        return State(self.grid_size, initial_cities, initial_forests, initial_pollution, initial_temperature, initial_water_level)

    def run(self):
        """Simulate for the given number of days."""
        print("Starting simulation...")
        for day in range(1, self.days + 1):  # Iterate from day 1 to the last day
            new_state = deepcopy(self.states[-1])  # Start with the last state
            new_state.day = day
            new_state.update()  # Apply updates to the state
            self.states.append(new_state)  # Save the new state
        print(f"Simulation completed for {self.days} days.")

    def precompute(self):
        """Precompute all the states for the simulation."""
        print("Precomputing all states...")
        current_state = deepcopy(self.states[0])  # Start from the initial state
        for day in range(1, self.days + 1):
            # print(f"Precomputing day {day}...")
            next_state = deepcopy(current_state)  # Create a new state from the current one
            next_state.update()  # Update the state
            next_state.day = day  # Set the day for the new state
            self.precomputed_results.append(next_state)  # Store precomputed state
            current_state = next_state  # Move to the next state
        print("Precomputation complete.")

    def get_state(self, day):
        """Retrieve the state for a specific day."""
        if 0 <= day < len(self.states):
            return self.states[day]
        else:
            raise IndexError(f"Day {day} is out of range. The simulation has {len(self.states)} states.")
