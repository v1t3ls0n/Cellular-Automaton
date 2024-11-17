from .State import State

import numpy as np
class Simulation:
    def __init__(self, grid_size, days=365):
        self.days = days
        self.states = []
        self.grid_size = grid_size
        self.initialize_simulation()

    def initialize_simulation(self):
        initial_state = State(grid_size=self.grid_size)
        self.states.append(initial_state)

    def run(self):
        for day in range(1, self.days):
            new_state = State(grid_size=self.grid_size)
            new_state.grid = np.copy(self.states[-1].grid)
            new_state.update()
            self.states.append(new_state)

    def get_state(self, day):
        if 0 <= day < len(self.states):
            return self.states[day]
        else:
            raise ValueError("Invalid day")

    def display(self, day, z_slice=0):
        state = self.get_state(day)
        for x in range(self.grid_size):
            print([state.grid[x, y, z_slice].water_level for y in range(self.grid_size)])  # לדוגמה: מפלס מים
