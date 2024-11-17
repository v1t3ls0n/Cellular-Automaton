import matplotlib.pyplot as plt

class GraphDisplay:
    def __init__(self, simulation):
        self.simulation = simulation

    def plot_average_pollution(self):
        days = list(range(self.simulation.days))
        avg_pollution = []
        for state in self.simulation.states:
            total_pollution = sum(
                cell.pollution_level
                for x in range(state.grid_size)
                for y in range(state.grid_size)
                for z in range(state.grid_size)
                for cell in [state.grid[x, y, z]]
            )
            avg_pollution.append(total_pollution / (state.grid_size ** 3))
        
        plt.plot(days, avg_pollution, label="Average Pollution")
        plt.xlabel("Day")
        plt.ylabel("Average Pollution Level")
        plt.title("Pollution Levels Over Time")
        plt.legend()
        plt.show()
