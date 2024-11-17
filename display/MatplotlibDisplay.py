import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.table import Table
from matplotlib.widgets import Button

class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.grid_size = simulation.grid_size
        self.current_day = 0

    def plot_3d(self):
        # Create 3D plot
        self.fig = plt.figure(figsize=(10, 7))
        self.ax = self.fig.add_subplot(121, projection='3d')  # 3D plot
        self.legend_ax = self.fig.add_subplot(122)  # Legend table

        # Initial rendering
        self.render_day(self.current_day)

        # Add "Next" and "Previous" buttons
        self.add_navigation_buttons()

        # Show the plot
        plt.show()

    def render_day(self, day):
        # Clear the current plot
        self.ax.cla()
        self.legend_ax.cla()

        # Set axis labels and title
        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        self.ax.set_zlabel('Z-axis')
        self.ax.set_title(f'3D Simulation - Day {day}')

        # Lists to store cell positions and colors
        x, y, z, colors = [], [], [], []

        # Iterate over the 3D grid for the current day
        for xi in range(self.grid_size):
            for yi in range(self.grid_size):
                for zi in range(self.grid_size):
                    cell = self.simulation.states[day].grid[xi, yi, zi]
                    x.append(xi)
                    y.append(yi)
                    z.append(zi)

                    # Define colors based on cell type
                    if cell.cell_type == 0:  # Sea
                        colors.append((0.0, 0.0, 1.0, 1.0))  # Blue (opaque)
                    elif cell.cell_type == 1:  # Land
                        colors.append((0.0, 1.0, 0.0, 1.0))  # Green (opaque)
                    elif cell.cell_type == 2:  # Clouds
                        colors.append((0.5, 0.5, 0.5, 0.5))  # Gray (semi-transparent)
                    elif cell.cell_type == 3:  # Icebergs
                        colors.append((0.5, 0.8, 1.0, 1.0))  # Sky blue (opaque)
                    elif cell.cell_type == 4:  # Forests
                        colors.append((0.0, 0.5, 0.0, 1.0))  # Dark green (opaque)
                    elif cell.cell_type == 5:  # Cities
                        colors.append((1.0, 0.0, 0.0, 1.0))  # Red (opaque)
                    else:  # Air
                        colors.append((0.7, 0.9, 1.0, 0.3))  # Light blue (transparent)

        # Plot points in 3D
        self.ax.scatter(x, y, z, c=colors, s=50)

        # Add the legend table
        self.render_legend()

    def render_legend(self):
        self.legend_ax.axis('tight')
        self.legend_ax.axis('off')
        table = Table(self.legend_ax, bbox=[0, 0, 1, 1])

        # Define legend entries
        legend_data = [
            ('Blue', 'Sea'),
            ('Green', 'Land'),
            ('Gray', 'Clouds'),
            ('Sky Blue', 'Icebergs'),
            ('Dark Green', 'Forests'),
            ('Red', 'Cities'),
            ('Light Blue (Transparent)', 'Air'),
        ]

        # Add rows to the table
        for i, (color, label) in enumerate(legend_data):
            table.add_cell(i, 0, 0.5, 0.2, text=color, loc='center', facecolor='white')
            table.add_cell(i, 1, 1.0, 0.2, text=label, loc='center', facecolor=color.lower() if 'Transparent' not in color else 'lightblue')

        # Add table header
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        self.legend_ax.add_table(table)

    def add_navigation_buttons(self):
        # Add a "Next Day" button
        ax_next = plt.axes([0.8, 0.05, 0.1, 0.075])  # Position of the button
        btn_next = Button(ax_next, 'Next Day')

        # Add a "Previous Day" button
        ax_prev = plt.axes([0.7, 0.05, 0.1, 0.075])
        btn_prev = Button(ax_prev, 'Previous Day')

        # Bind button actions
        btn_next.on_clicked(self.next_day)
        btn_prev.on_clicked(self.previous_day)

    def next_day(self, event):
        if self.current_day < len(self.simulation.states) - 1:
            self.current_day += 1
            self.render_day(self.current_day)
            self.fig.canvas.draw_idle()

    def previous_day(self, event):
        if self.current_day > 0:
            self.current_day -= 1
            self.render_day(self.current_day)
            self.fig.canvas.draw_idle()
