import matplotlib.pyplot as plt
import numpy as np

class GraphDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.fig, self.ax_pollution, self.ax_temperature, self.ax_population, self.ax_forests = None, None, None, None, None

    def plot_graphs(self):
        """Create the plots for the simulation data."""
        plt.figure(figsize=(16, 10))

        # Create subplots
        self.ax_pollution = plt.subplot(221)  # Pollution graph
        self.ax_temperature = plt.subplot(222)  # Temperature graph
        self.ax_population = plt.subplot(223)  # Population graph
        self.ax_forests = plt.subplot(224)  # Forest graph

        # Render each graph
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()

        # Show all plots
        plt.tight_layout()
        plt.show()

    def render_pollution_graph(self):
        """Render the pollution graph over time."""
        self.ax_pollution.set_title("Pollution Over Time")
        self.ax_pollution.set_xlabel("Day")
        self.ax_pollution.set_ylabel("Average Pollution Level")

        days = range(len(self.simulation.states))
        avg_pollution = [
            np.mean([
                cell.pollution_level
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type not in [6, 0]  # Exclude air and sea cells
            ])
            for state in self.simulation.states
        ]

        self.ax_pollution.plot(days, avg_pollution, color="red", label="Pollution")
        self.ax_pollution.legend()

    def render_temperature_graph(self):
        """Render the temperature graph over time."""
        self.ax_temperature.set_title("Temperature Over Time")
        self.ax_temperature.set_xlabel("Day")
        self.ax_temperature.set_ylabel("Average Temperature")

        days = range(len(self.simulation.states))
        avg_temperature = [
            np.mean([
                cell.temperature
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type not in [6]  # Exclude air cells
            ])
            for state in self.simulation.states
        ]

        self.ax_temperature.plot(days, avg_temperature, color="blue", label="Temperature")
        self.ax_temperature.legend()

    def render_population_graph(self):
        """Render the city population graph over time."""
        self.ax_population.set_title("City Population Over Time")
        self.ax_population.set_xlabel("Day")
        self.ax_population.set_ylabel("Number of Cities")

        days = range(len(self.simulation.states))
        city_counts = [
            sum(
                1
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type == 5  # City cell type
            )
            for state in self.simulation.states
        ]

        self.ax_population.plot(days, city_counts, color="purple", label="Cities")
        self.ax_population.legend()

    def render_forests_graph(self):
        """Render the forest count graph over time."""
        self.ax_forests.set_title("Forest Count Over Time")
        self.ax_forests.set_xlabel("Day")
        self.ax_forests.set_ylabel("Number of Forests")

        days = range(len(self.simulation.states))
        forest_counts = [
            sum(
                1
                for x in range(state.grid.shape[0])
                for y in range(state.grid.shape[1])
                for z in range(state.grid.shape[2])
                if (cell := state.grid[x][y][z]).cell_type == 4  # Forest cell type
            )
            for state in self.simulation.states
        ]

        self.ax_forests.plot(days, forest_counts, color="green", label="Forests")
        self.ax_forests.legend()
