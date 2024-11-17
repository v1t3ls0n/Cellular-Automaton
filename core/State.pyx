import numpy as np
from libc.math cimport abs
from .Cell import Cell

cdef class State:
    cdef public int grid_size
    cdef list grid

    def __init__(self, int grid_size, int day=0):
        self.grid_size = grid_size
        self.grid = [[[None for _ in range(grid_size)]
                      for _ in range(grid_size)]
                      for _ in range(grid_size)]
        self.day = day
        self.initialize_grid()

    def initialize_grid(self):
        cdef int x, y, z
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell_type = self.determine_cell_type(z)
                    cell = Cell(cell_type)
                    self.grid[x][y][z] = cell

    def determine_cell_type(self, int z):
        if z < 5:  # Example thresholds
            return 0  # Sea
        elif z < 10:
            return np.random.choice([1, 4, 5], p=[0.5, 0.3, 0.2])  # Land, Forest, Cities
        else:
            return 2  # Clouds

    def update(self):
        """ Update the state grid based on neighbors' effects. """
        cdef int x, y, z
        cdef list neighbors
        cdef list new_grid = [[[
            self.grid[x][y][z].copy() for z in range(self.grid_size)]
            for y in range(self.grid_size)]
            for x in range(self.grid_size)]
        
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    neighbors = self.get_neighbors(x, y, z)
                    new_grid[x][y][z].update(neighbors)
        
        self.grid = new_grid

    def get_neighbors(self, int x, int y, int z):
        """ Return a list of neighbors for the cell at (x, y, z). """
        cdef int dx, dy, dz, nx, ny, nz
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                        neighbors.append(self.grid[nx][ny][nz])
        return neighbors
