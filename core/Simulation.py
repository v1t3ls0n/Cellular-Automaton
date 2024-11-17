import numpy as np
from core.State import State
from core.Cell import Cell
from copy import deepcopy

class Simulation:
    def __init__(self, grid_size, days):
        self.grid_size = grid_size
        self.days = days
        self.states = []  # Initialize an empty list to store states

        # Create the initial state
        initial_state = self.create_initial_state()
        self.states.append(initial_state)

    def create_initial_state(self):
        # Create an initial state using the grid size
        return State(self.grid_size)

    def run(self):
        """Simulate for the given number of days."""
        print("Starting simulation...")
        for day in range(1, self.days + 1):  # Iterate from day 1 to the last day
            new_state = deepcopy(self.states[-1])  # Start with the last state
            new_state.day = day
            new_state.update()  # Apply updates to the state

            # Debugging: Check if the state has actually changed
            # if np.array_equal(new_state.grid, self.states[-1].grid):
            #     print(f"Day {day}: No changes detected.")
            # else:
            #     print(f"Day {day}: Changes detected.")

            self.states.append(new_state)  # Save the new state
        # print(f"Simulation completed for {self.days} days.")


    def get_state(self, day):
            """Retrieve the state for a specific day."""
            if 0 <= day < len(self.states):
                return self.states[day]
            else:
                raise IndexError(f"Day {day} is out of range. The simulation has {len(self.states)} states.")