import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import logging
from core.conf import config, key_labels, format_config_value, particle_mapping, rgba_to_hex
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class MatplotlibDisplay:
    config = config

    def __init__(self, simulation):
        self.simulation = simulation
        self.precomputed_results = simulation.states
        self.fig = None
        self.scrollable_frame = None
        self.current_day = 0  # משתנה זה חובה לשימוש בגרף 3D
        self.config_window = None
        self.three_d_window = None
        self.main_window = None
        self.precomputed_data = []  # לשמירת הנתונים לגרף ה-3D
        self.days = range(len(simulation.states))

    def plot_3d(self):
        """Create a scrollable and resizable window with compact graphs."""
        self.precompute_visualizations()

        # Initialize main Tkinter window
        self.main_window = tk.Tk()
        self.main_window.title(
            "Environmental Simulation Application Main Window")
        self.main_window.state("zoomed")  # Start in full-screen mode

        # Configure grid layout for the main window
        self.main_window.rowconfigure(1, weight=1)
        self.main_window.columnconfigure(0, weight=1)

        # Add control buttons
        control_frame = tk.Frame(self.main_window)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        tk.Button(control_frame, text="Show Custom Parameters Table",
                  command=self.bring_config_to_front).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Hide Custom Parameters Table",
                  command=self.minimize_config_window).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Show 3D Grid",
                  command=self.bring_3d_to_front).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Hide 3D Grid",
                  command=self.minimize_3d_window).pack(side=tk.LEFT, padx=5)

        # Create a scrollable canvas
        scrollable_canvas = tk.Canvas(self.main_window, highlightthickness=0)
        scrollable_canvas.grid(row=1, column=0, sticky="nsew")

        # Add vertical and horizontal scrollbars
        vertical_scrollbar = tk.Scrollbar(
            self.main_window, orient="vertical", command=scrollable_canvas.yview, width=25)
        vertical_scrollbar.grid(row=1, column=1, sticky="ns")

        horizontal_scrollbar = tk.Scrollbar(
            self.main_window, orient="horizontal", command=scrollable_canvas.xview, width=25)
        horizontal_scrollbar.grid(row=2, column=0, sticky="ew")

        scrollable_canvas.configure(
            yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

        # Create a frame inside the canvas for Matplotlib content
        scrollable_frame = tk.Frame(scrollable_canvas)
        scrollable_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw")

        # Dynamically adjust the canvas size
        def _on_configure(event):
            scrollable_canvas.configure(
                scrollregion=scrollable_canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_configure)

        # Enable mouse wheel scrolling
        def _on_mouse_wheel(event):
            if event.state & 0x1:  # Shift key pressed -> horizontal scroll
                scrollable_canvas.xview_scroll(-1 *
                                               (event.delta // 120), "units")
            else:
                scrollable_canvas.yview_scroll(-1 *
                                               (event.delta // 120), "units")

        scrollable_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        # Create a Matplotlib figure
        fig = plt.Figure(figsize=(20, 25))  # Adjust figure size
        # 7 rows for standardized and non-standardized graphs
        gs = fig.add_gridspec(7, 2, width_ratios=[
                              1, 1], hspace=0.4, wspace=0.4)

        self.fig = fig
        self.canvas = FigureCanvasTkAgg(self.fig, master=scrollable_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Create subplots
        self.axes = {
            # Standardized Pollution graph
            "std_pollution": self.fig.add_subplot(gs[0, 0]),
            # Standardized Temperature graph
            "std_temperature": self.fig.add_subplot(gs[0, 1]),
            # Standardized Population graph
            "std_population": self.fig.add_subplot(gs[1, 0]),
            # Standardized Forests graph
            "std_forests": self.fig.add_subplot(gs[1, 1]),
            # Standardized Water Mass graph
            "std_water_mass": self.fig.add_subplot(gs[2, 0]),

            "pollution": self.fig.add_subplot(gs[3, 0]),  # Pollution graph
            "temperature": self.fig.add_subplot(gs[3, 1]),  # Temperature graph
            "population": self.fig.add_subplot(gs[4, 0]),  # Population graph
            "forests": self.fig.add_subplot(gs[4, 1]),  # Forests graph
            "water_mass": self.fig.add_subplot(gs[5, 0]),  # Water Mass graph

            # Pollution Standard Deviation graph
            "std_dev_pollution": self.fig.add_subplot(gs[5, 1]),
            # Temperature Standard Deviation graph
            "std_dev_temperature": self.fig.add_subplot(gs[6, 1]),
            # Water Mass Standard Deviation graph
            "std_dev_water_mass": self.fig.add_subplot(gs[6, 0]),
        }

        # Render standardized graphs
        self.render_standardized_pollution_graph(
            self.axes["std_pollution"], color="black")
        self.render_standardized_temperature_graph(
            self.axes["std_temperature"], color="red")
        self.render_standardized_population_graph(
            self.axes["std_population"], color="purple")
        self.render_standardized_forests_graph(
            self.axes["std_forests"], color="green")
        self.render_standardized_water_mass_graph(
            self.axes["std_water_mass"], color="cyan")

        # Render non-standardized graphs
        self.render_pollution_graph(self.axes["pollution"], color="black")
        self.render_temperature_graph(self.axes["temperature"], color="red")
        self.render_population_graph(self.axes["population"], color="purple")
        self.render_forests_graph(self.axes["forests"], color="green")
        self.render_water_mass_graph(self.axes["water_mass"], color="cyan")

        # Render standard deviation graphs
        self.render_std_dev_pollution_graph(
            self.axes["std_dev_pollution"], color="black")
        self.render_std_dev_temperature_graph(
            self.axes["std_dev_temperature"], color="red")
        self.render_std_dev_water_mass_graph(
            self.axes["std_dev_water_mass"], color="cyan")
        # Add 3D visualization and config table
        self.open_3d_in_new_window(self.main_window)
        self.add_config_table_with_scrollbar(self.main_window)

        # Start the Tkinter main loop
        self.main_window.mainloop()

    def open_3d_in_new_window(self, root=None):
        """Open a resizable 3D graph window with a 3D plot and integrated legend."""
        three_d_window = tk.Toplevel()
        three_d_window.title("3D Visualization")
        three_d_window.geometry("1280x600")  # Default size
        three_d_window.minsize(1000, 600)  # Minimum size

        # Configure flexible resizing
        three_d_window.columnconfigure(0, weight=1)
        three_d_window.rowconfigure(0, weight=0)  # Control buttons
        three_d_window.rowconfigure(1, weight=1)  # Plot area

        # Control buttons frame
        control_frame = tk.Frame(three_d_window)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Add a button to bring the main window to the front
        tk.Button(
            control_frame,
            text="Bring Main Window to Front",
            command=lambda: root.lift(),  # Bring the main window to the front
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Create a Matplotlib figure with GridSpec for 3D plot and legend
        fig = plt.Figure(figsize=(10, 6))
        gs = fig.add_gridspec(1, 2, width_ratios=[4, 1], wspace=0.4)

        # 3D plot
        ax_3d = fig.add_subplot(gs[0, 0], projection="3d")
        ax_3d.set_title(f"Day {self.current_day}", pad=20)
        ax_3d.set_xlabel("X Axis")
        ax_3d.set_ylabel("Y Axis")
        ax_3d.set_zlabel("Z Axis")

        # Fetch data for the current day
        points, colors, sizes = self.precomputed_data[self.current_day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)  # 's' for square

        # Legend area
        ax_color_map = fig.add_subplot(gs[0, 1])
        ax_color_map.axis("off")  # Hide axes for the legend

        # Legend elements dynamically generated based on cell types and colors
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=f"{cell_type} : {
                    particle_mapping.get(cell_type, 'Unknown')}",
                markersize=10,
                markerfacecolor=rgba_to_hex(
                    color) if isinstance(color, tuple) else color
            )
            for cell_type, color in self.config["base_colors"].items()
        ]

        # Add Pollution and Temperature tints if enabled
        if self.config.get("tint"):
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w',
                           label='Pollution Tint', markersize=10, markerfacecolor='black')
            )
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w',
                           label='Temperature Tint', markersize=10, markerfacecolor='red')
            )

        # Add the legend to the plot
        ax_color_map.legend(
            handles=legend_elements,
            loc="center",
            title="Cell Types",
            frameon=False
        )

        # Add figure to the window
        canvas = FigureCanvasTkAgg(fig, master=three_d_window)
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        canvas.draw()

        # Save axes for future updates
        self.ax_3d = ax_3d
        self.ax_color_map = ax_color_map
        # Handle keyboard events for navigation

        def handle_key_press(event):
            """Handle key presses for navigating between days in the separate window."""
            if event.key == "right":  # Move to the next day
                if self.current_day < len(self.simulation.states) - 1:
                    self.current_day += 1
                    update_plot()
            elif event.key == "left":  # Move to the previous day
                if self.current_day > 0:
                    self.current_day -= 1
                    update_plot()

        def update_plot():
            """Update the 3D plot and refresh the window."""
            ax_3d.cla()
            ax_3d.set_title(f"Day {self.current_day}", pad=20)
            ax_3d.set_xlabel("X Axis")
            ax_3d.set_ylabel("Y Axis")
            ax_3d.set_zlabel("Z Axis")
            points, colors, sizes = self.precomputed_data[self.current_day]
            xs, ys, zs = zip(*points) if points else ([], [], [])
            ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)  # 's' for square

            canvas.draw_idle()

        # Bind the keyboard event handler
        fig.canvas.mpl_connect("key_press_event", handle_key_press)
        self.three_d_window = three_d_window

    def add_config_table_with_scrollbar(self, root=None):
        """Create a configuration table window with scrollbars and add control buttons."""
        # Create a new window for the configuration table
        self.config_window = tk.Toplevel(root)
        self.config_window.title("Configuration Table")

        # Create a frame for the buttons
        button_frame = tk.Frame(self.config_window)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Add a "Bring Main Window to Front" button
        tk.Button(
            button_frame,
            text="Bring Main Window to Front",
            command=lambda: root.lift(),  # Brings the main window to the front
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Create a frame to hold the table and scrollbars
        frame = tk.Frame(self.config_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Add vertical scrollbar
        vsb = tk.Scrollbar(frame, orient="vertical", width=20)
        vsb.pack(side="right", fill="y")

        # Add horizontal scrollbar
        hsb = tk.Scrollbar(frame, orient="horizontal", width=20)
        hsb.pack(side="bottom", fill="x")

        # Create a treeview for the table
        tree = ttk.Treeview(
            frame,
            columns=("Parameter", "Value"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")

        # Attach the scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Add data to the table
        parameter_width = 0
        value_width = 0

        # Populate the treeview with formatted data
        for key, value in self.config.items():
            if key in key_labels:
                formatted_value = format_config_value(key, value)
                tree.insert("", "end", values=(
                    key_labels[key], formatted_value))
                # Calculate maximum width for the Parameter column
                parameter_width = max(
                    parameter_width, len(key_labels[key]) * 10)

                # Calculate maximum width for the Value column
                value_width = max(value_width, len(formatted_value) * 7)

        # Set the column widths to fit the data
        tree.column("Parameter", width=parameter_width, anchor="w")
        tree.column("Value", width=value_width, anchor="w")
        tree.pack(fill=tk.BOTH, side="top", expand=True)

    def add_cell_type_legend_to_frame(self, legend_frame):
        """Add a well-padded legend explaining the cell colors and cell type numbers."""
        # Add a title at the top of the legend
        title_label = tk.Label(
            legend_frame,
            text="Cell Types",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        # Add space above and below the title
        title_label.pack(pady=(10, 10))
        # self.config_window.attributes("-topmost", True)

        # Define legend items
        legend_items = [
            ("0: Ocean", self.config["base_colors"][0]),
            ("1: Desert", self.config["base_colors"][1]),
            ("2: Cloud", self.config["base_colors"][2]),
            ("3: Ice", self.config["base_colors"][3]),
            ("4: Forest", self.config["base_colors"][4]),
            ("5: City", self.config["base_colors"][5]),
            ("6: Air (White With Low Opacity)",
             self.config["base_colors"][6]),
            ("7: Rain", self.config["base_colors"][7]),
            ("8: Vacuum (Transparent)", self.config["base_colors"][8]),
        ]

        # Add tinted pollution if enabled
        if self.config.get("tint"):
            legend_items.append(
                ("9: Pollution Levels (Tinted Color)", "red"))

            # Function to convert RGBA to Hex

    def add_square(self, ax, x, y, z, size, color):
        """Add a square to the 3D plot."""
        half_size = size / 2.0
        square = [
            (x - half_size, y - half_size, z),
            (x + half_size, y - half_size, z),
            (x + half_size, y + half_size, z),
            (x - half_size, y + half_size, z),
        ]
        poly = Poly3DCollection([square], color=color)
        ax.add_collection3d(poly)

    def precompute_visualizations(self):
        """
        Precompute 3D scatter data for all precomputed states to make particles appear denser.
        """
        logging.info("Precomputing 3D visualizations...")
        for state in self.simulation.states:
            points = []
            colors = []
            sizes = []  # Add a list for point sizes
            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x][y][z]
                        color = to_rgba(cell.get_color())

                        # Ignore fully transparent cells
                        if color and color[3] != 0.0:
                            # Add interpolation for density
                            # 3 interpolated points along x-axis
                            for dx in np.linspace(-0.2, 0.2, 3):
                                # 3 interpolated points along y-axis
                                for dy in np.linspace(-0.2, 0.2, 3):
                                    # 3 interpolated points along z-axis
                                    for dz in np.linspace(-0.2, 0.2, 3):
                                        points.append((x + dx, y + dy, z + dz))
                                        # Slightly reduced alpha
                                        interpolated_color = (
                                            color[0], color[1], color[2], 0.9)
                                        colors.append(interpolated_color)
                                        # Adjust size for interpolated points
                                        sizes.append(50.0)

                            # Add the original point
                            points.append((x, y, z))
                            # Full opacity
                            solid_color = (color[0], color[1], color[2], 1.0)
                            colors.append(solid_color)
                            # Larger size for original points
                            sizes.append(100.0)

            self.precomputed_data.append((points, colors, sizes))
        logging.info("3D precomputation complete.")

    def render_day(self, day):
        """Render the cached 3D visualization for a specific day."""
        # Save the current viewing angles
        self.current_elev = self.ax_3d.elev
        self.current_azim = self.ax_3d.azim

        # Clear the existing plot
        self.ax_3d.cla()
        self.ax_3d.set_title(f"Day {day}")
        self.ax_3d.set_axis_on()  # Simplify visualization

        # Add grid for spatial reference
        self.ax_3d.grid(True)

        points, colors, sizes = self.precomputed_data[day]
        for (x, y, z), color, size in zip(points, colors, sizes):
            self.add_square(self.ax_3d, x, y, z, size=size, color=color)

        self.fig.canvas.draw_idle()

        # Restore the saved viewing angles
        self.ax_3d.view_init(elev=self.current_elev,
                             azim=self.current_azim)

        self.fig.canvas.draw_idle()

    def render_generic_graph(self, ax, title, xlabel, ylabel, days, data, std_dev=None, color="blue", label=None, fill_label=None):
        """
        Render a generic graph with optional standard deviation shading.

        Args:
            ax (matplotlib.axes.Axes): The Axes to draw the graph on.
            title (str): Title of the graph.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            days (range): Range of days for the x-axis.
            data (list): Data points for the graph.
            std_dev (list, optional): Standard deviation values for shading. Defaults to None.
            color (str): Color of the graph. Defaults to "blue".
            label (str, optional): Label for the main line. Defaults to None.
            fill_label (str, optional): Label for the shaded area. Defaults to None.
        """
        ax.cla()
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if len(days) == len(data):
            if std_dev is not None:
                ax.fill_between(
                    days,
                    np.array(data) - np.array(std_dev),
                    np.array(data) + np.array(std_dev),
                    color=color, alpha=0.2, label=fill_label
                )
            ax.plot(days, data, color=color, label=label)
            if label or fill_label:
                ax.legend()
        else:
            logging.error(f"Data length mismatch in graph: {title}")

    def render_population_graph(self, ax, color):
        """Render the city population graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="City Population Over Time",
            xlabel="Day",
            ylabel="Number of Cities",
            days=self.days,
            data=self.simulation.city_population_over_time,
            color="purple",
            label="Cities"
        )

    def render_forests_graph(self, ax, color):
        """Render the forest count graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="Forest Count Over Time",
            xlabel="Day",
            ylabel="Number of Forests",
            days=self.days,
            data=self.simulation.forest_count_over_time,
            color="green",
            label="Forests"
        )

    def render_temperature_graph(self, ax, color):
        """Render the temperature graph with standard deviation over time."""
        self.render_generic_graph(
            ax=ax,
            title="Temperature Over Time",
            xlabel="Day",
            ylabel="Average Temperature",
            days=self.days,
            data=self.simulation.temperature_over_time,
            std_dev=self.simulation.std_dev_temperature_over_time,
            color="red",
            label="Average Temperature",
            fill_label="Temperature Std Dev Range"
        )

    def render_pollution_graph(self, ax, color):
        """Render the pollution graph with standard deviation over time."""
        self.render_generic_graph(
            ax=ax,
            title="Pollution Over Time",
            xlabel="Day",
            ylabel="Average Pollution",
            days=self.days,
            data=self.simulation.pollution_over_time,
            std_dev=self.simulation.std_dev_pollution_over_time,
            color=color,
            label="Pollution",
            fill_label="Pollution Std Dev Range"
        )

    def render_water_mass_graph(self, ax, color):
        """Render the average water mass graph with standard deviation over time."""
        self.render_generic_graph(
            ax=ax,
            title="Average Water Mass Over Time",
            xlabel="Day",
            ylabel="Average Water Mass",
            days=self.days,
            data=self.simulation.water_mass_over_time,
            std_dev=self.simulation.std_dev_water_mass_over_time,
            color=color,
            label="Average Water Mass",
            fill_label="Water Mass Std Dev Range"
        )

    def render_std_dev_pollution_graph(self, ax, color):
        """Render the standard deviation of pollution graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="Pollution Standard Deviation Over Time",
            xlabel="Day",
            ylabel="Standard Deviation Pollution",
            days=self.days,
            data=self.simulation.std_dev_pollution_over_time,
            color=color,
            label="Pollution Std Dev"
        )

    def render_std_dev_temperature_graph(self, ax, color):
        """Render the standard deviation of temperature graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="Temperature Standard Deviation Over Time",
            xlabel="Day",
            ylabel="Standard Deviation Temperature",
            days=self.days,
            data=self.simulation.std_dev_temperature_over_time,
            color=color,
            label="Temperature Std Dev"
        )

    def render_std_dev_water_mass_graph(self, ax, color):
        """Render the standard deviation of water mass graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="Standard Deviation of Water Mass Over Time",
            xlabel="Day",
            ylabel="Water Mass Std Dev",
            days=self.days,
            data=self.simulation.std_dev_water_mass_over_time,
            color=color,
            label="Water Mass Std Dev"
        )

    def render_std_dev_cell_distribution_graph(self, ax, color="blue"):
        """Render the standard deviation of cell type distribution graph over time."""
        self.render_generic_graph(
            ax=ax,
            title="Cell Type Distribution Std Dev Over Time",
            xlabel="Day",
            ylabel="Std Dev of Cell Counts",
            days=self.days,
            data=self.simulation.std_dev_cell_distribution_over_time,
            color="blue",
            label="Cell Type Distribution Std Dev"
        )

    def render_standardized_pollution_graph(self, ax, color="black"):
        """Render the pollution graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.pollution_over_time)
        standardized_std_dev = self.standardize_data(
            self.simulation.std_dev_pollution_over_time)
        self.render_generic_graph(
            ax=ax,
            title="Pollution Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Pollution",
            days=self.days,
            data=standardized_data,
            std_dev=standardized_std_dev,
            color=color,
            label="Standardized Pollution",
            fill_label="Pollution Std Dev Range"
        )

    def render_standardized_temperature_graph(self, ax, color="red"):
        """Render the temperature graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.temperature_over_time)
        standardized_std_dev = self.standardize_data(
            self.simulation.std_dev_temperature_over_time)
        self.render_generic_graph(
            ax=ax,
            title="Temperature Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Temperature",
            days=self.days,
            data=standardized_data,
            std_dev=standardized_std_dev,
            color=color,
            label="Standardized Temperature",
            fill_label="Temperature Std Dev Range"
        )

    def render_standardized_population_graph(self, ax, color="purple"):
        """Render the population graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.city_population_over_time)
        # Assuming std deviation for population if available; if not, skip.
        standardized_std_dev = self.standardize_data(self.simulation.std_dev_population_over_time) if hasattr(
            self.simulation, "std_dev_population_over_time") else None
        self.render_generic_graph(
            ax=ax,
            title="City Population Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Number of Cities",
            days=self.days,
            data=standardized_data,
            std_dev=standardized_std_dev,
            color=color,
            label="Standardized Cities",
            fill_label="Population Std Dev Range"
        )

    def render_standardized_forests_graph(self, ax, color="green"):
        """Render the forests graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.forest_count_over_time)
        standardized_std_dev = self.standardize_data(
            self.simulation.std_dev_forest_count_over_time)
        self.render_generic_graph(
            ax=ax,
            title="Forest Count Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Number of Forests",
            days=self.days,
            data=standardized_data,
            std_dev=standardized_std_dev,
            color=color,
            label="Standardized Forests",
            fill_label="Forest Std Dev Range"
        )

    def render_standardized_water_mass_graph(self, ax, color="cyan"):
        """Render the water mass graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.water_mass_over_time)
        standardized_std_dev = self.standardize_data(
            self.simulation.std_dev_water_mass_over_time)
        self.render_generic_graph(
            ax=ax,
            title="Water Mass Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Water Mass",
            days=self.days,
            data=standardized_data,
            std_dev=standardized_std_dev,
            color=color,
            label="Standardized Water Mass",
            fill_label="Water Mass Std Dev Range"
        )

    def render_standardized_cell_distribution_graph(self, ax, color="grey"):
        """Render the cell type distribution graph (Standardized)."""
        standardized_data = self.standardize_data(
            self.simulation.std_dev_cell_distribution_over_time)
        self.render_generic_graph(
            ax=ax,
            title="Cell Type Distribution Graph (Standardized)",
            xlabel="Day",
            ylabel="Standardized Cell Type Distribution",
            days=self.days,
            data=standardized_data,
            std_dev=None,  # Assuming no std deviation for cell distribution
            color=color,
            label="Standardized Cell Distribution"
        )

    def standardize_data(self, data):
        """
        Standardize data to have a mean of 0 and standard deviation of 1.

        Args:
            data (list): List of data points.

        Returns:
            list: Standardized data points.
        """
        mean = np.mean(data)
        std_dev = np.std(data)
        if std_dev == 0:
            # Avoid division by zero; return zeros if std_dev is zero
            return [0] * len(data)
        return [(x - mean) / std_dev for x in data]

    def next_day(self):
        if self.current_day < len(self.simulation.states) - 1:
            self.current_day += 1
            self.render_day(self.current_day)

    def previous_day(self):
        if self.current_day > 0:
            self.current_day -= 1
            self.render_day(self.current_day)

    def bring_config_to_front(self):
        """Bring the configuration window to the front."""
        if self.config_window:
            self.config_window.deiconify()
            self.config_window.lift()
            self.config_window.focus_force()
        else:
            self.add_config_table_with_scrollbar(self.main_window)

    def bring_main_window_to_front(self):
        """Bring the main window to the front."""
        self.minimize_3d_window()
        self.minimize_config_window()
        if self.main_window and self.main_window.winfo_exists():
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()

    def bring_3d_to_front(self):
        """Bring the 3D visualization window to the front."""
        if self.three_d_window and self.three_d_window.winfo_exists():
            self.three_d_window.deiconify()
            self.three_d_window.lift()
            self.three_d_window.focus_force()
        else:
            self.open_3d_in_new_window()

    def minimize_config_window(self):
        """Minimize the configuration window."""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.iconify()
        else:
            self.add_config_table_with_scrollbar(self.main_window)

    def minimize_3d_window(self):
        """Minimize the 3D visualization window."""
        if self.three_d_window and self.three_d_window.winfo_exists():
            self.three_d_window.iconify()
        else:
            self.open_3d_in_new_window()

    def apply_tint(self, base_color, tint_factor, tint_type):
        """
        Apply a tint to the base color based on a tint factor and type.

        Args:
            base_color (tuple): The RGBA base color.
            tint_factor (float): Tint intensity in the range [0.0, 1.0].
            tint_type (str): Type of tint ("red" for temperature, "black" for pollution).

        Returns:
            tuple: The tinted RGBA color.
        """
        r, g, b, a = base_color
        if tint_type == "red":
            r = min(1.0, r + tint_factor)  # Increase red
            g = max(0.0, g * (1.0 - tint_factor))  # Reduce green
            b = max(0.0, b * (1.0 - tint_factor))  # Reduce blue
        elif tint_type == "black":
            r = max(0.0, r * (1.0 - tint_factor))  # Reduce red
            g = max(0.0, g * (1.0 - tint_factor))  # Reduce green
            b = max(0.0, b * (1.0 - tint_factor))  # Reduce blue
        return (r, g, b, a)

    def get_color(self):
        """
        Get the color of the cell with optional tinting for pollution and temperature.

        Returns:
            tuple: RGBA color.
        """
        base_color = config["base_colors"].get(
            self.cell_type, (1.0, 1.0, 1.0, 0.0))
        if config.get("tint"):
            pollution_intensity = max(
                0.0, min(self.pollution_level / 50.0, 1.0))
            temperature_intensity = max(0.0, min(self.temperature / 50.0, 1.0))

            if pollution_intensity > temperature_intensity:
                return self.apply_tint(base_color, pollution_intensity, "black")
            elif temperature_intensity > pollution_intensity:
                return self.apply_tint(base_color, temperature_intensity, "red")

        return base_color
