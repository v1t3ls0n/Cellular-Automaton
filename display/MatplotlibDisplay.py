import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from config.config_state_handler import get_config
from config.conf_presets import KEY_LABELS, PARTICLE_MAPPING
from utils.helpers import format_config_value,  rgba_to_hex
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class MatplotlibDisplay:
    config = get_config()

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
        self.tint = False  # Tint state (False for untinted, True for tinted)

    def render_graphic_user_interface(self):
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
        fig = plt.Figure(figsize=(18.8,22), tight_layout=True)  # Adjust figure size
        # 7 rows for standardized and non-standardized graphs
        gs = fig.add_gridspec(5, 3)  # 7 rows for standardized and non-standardized graphs
        fig.subplots_adjust(hspace=0.4)  # Adjust spacing between plots

        self.fig = fig
        self.canvas = FigureCanvasTkAgg(self.fig, master=scrollable_frame)
        self.canvas.get_tk_widget().pack(fill="both",padx=4)


        # fit the 3-column layout
        self.axes = {
            # Standardized graphs
            "std_pollution": self.fig.add_subplot(gs[0, 0]),
            "std_temperature": self.fig.add_subplot(gs[0, 1]),
            "std_population": self.fig.add_subplot(gs[0, 2]),
            "std_forests": self.fig.add_subplot(gs[1, 0]),
            "std_water_mass": self.fig.add_subplot(gs[1, 1]),

            # Leave an empty slot at the second row, third column (gs[1, 2] is unused)

            # Non-Standardized graphs
            "pollution": self.fig.add_subplot(gs[2, 0]),
            "temperature": self.fig.add_subplot(gs[2, 1]),
            "water_mass": self.fig.add_subplot(gs[2, 2]),  # Right of temperature
            "forests": self.fig.add_subplot(gs[3, 0]),  # Left of population
            "population": self.fig.add_subplot(gs[3, 1]),  # Right of forests

            # Standard Deviation graphs
            "std_dev_pollution": self.fig.add_subplot(gs[4, 0]),
            "std_dev_temperature": self.fig.add_subplot(gs[4, 1]),
            "std_dev_water_mass": self.fig.add_subplot(gs[4, 2]),
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
        """
        Open a resizable 3D graph window with a 3D plot and integrated legend,
        allowing switching between tinted and untinted modes.
        """
        three_d_window = tk.Toplevel()
        three_d_window.title("3D Visualization")
        three_d_window.geometry("1280x600")  # Default size
        three_d_window.minsize(1000, 600)  # Minimum size

        # Configure flexible resizing
        three_d_window.columnconfigure(0, weight=1)
        three_d_window.rowconfigure(0, weight=0)  # Control buttons
        three_d_window.rowconfigure(1, weight=1)  # Plot area
        self.three_d_window = three_d_window
        # Control buttons frame
        control_frame = tk.Frame(three_d_window)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Add buttons to toggle tinted and untinted modes

            # Add buttons to toggle tinted and untinted modes
        tk.Button(
            control_frame,
            text="Show Tinted",
            command=lambda: self.toggle_tint(True),
        ).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(
            control_frame,
            text="Show Untinted",
            command=lambda: self.toggle_tint(False),
        ).pack(side=tk.LEFT, padx=5, pady=5)


        tk.Button(
            control_frame,
            text="Show Statistics Graphs (Main Window)",
            command=lambda: self.bring_main_window_to_front(),
        ).pack(side=tk.LEFT, padx=5, pady=5)


        # Navigation buttons
        tk.Button(control_frame, text="Previous Day", command=self.previous_day).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Next Day", command=self.next_day).pack(side=tk.LEFT, padx=5, pady=5)

        # Create a Matplotlib figure with GridSpec for 3D plot and legend
        fig = plt.Figure(figsize=(10, 6))
        gs = fig.add_gridspec(1, 2, width_ratios=[4, 1], wspace=0.4)

        # 3D plot
        ax_3d = fig.add_subplot(gs[0, 0], projection="3d")
        ax_3d.set_title(f"Day {self.current_day}", pad=20)
        ax_3d.set_xlabel("X Axis")
        ax_3d.set_ylabel("Y Axis")
        ax_3d.set_zlabel("Z Axis")

        # Legend area
        ax_color_map = fig.add_subplot(gs[0, 1])
        ax_color_map.axis("off")  # Hide axes for the legend

        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker="o", color="w", label=f"{cell_type}: {PARTICLE_MAPPING[cell_type]}",
                    markersize=10, markerfacecolor=rgba_to_hex(color))
            for cell_type, color in self.config["base_colors"].items()
        ]
    
        legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w', label='Pollution Tint', markersize=10, markerfacecolor='black')
            )
        legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w', label='Temperature Tint', markersize=10, markerfacecolor='red')
            )

        ax_color_map.legend(handles=legend_elements, loc="center", title="Cell Types", frameon=False)

        # Add figure to the window
        canvas = FigureCanvasTkAgg(fig, master=three_d_window)
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        canvas.draw()

        # Save axes for future updates
        self.ax_3d = ax_3d
        self.ax_color_map = ax_color_map
        self.fig = fig

        # Handle keyboard events for navigation
        def handle_key_press(event):
            """Handle key presses for navigating between days in the separate window."""
            if event.key == "right":  # Move to the next day
                if self.current_day < len(self.simulation.states) - 1:
                    self.current_day += 1
                    self.render_day(self.current_day)
            elif event.key == "left":  # Move to the previous day
                if self.current_day > 0:
                    self.current_day -= 1
                    self.render_day(self.current_day)

        # Bind the keyboard event handler
        fig.canvas.mpl_connect("key_press_event", handle_key_press)

        # Render the first day with the default tinting state
        self.render_day(self.current_day)



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
            text="Bring Graph Metrics To Front",
            command=lambda: root.lift(),  # Brings the main window to the front
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
                
        tk.Button(
            button_frame,
            text="Bring 3D Visualization Window To Front",
            command=lambda: self.bring_3d_to_front(),  # Brings the main window to the front
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
            if key in KEY_LABELS:
                formatted_value = format_config_value(key, value)
                tree.insert("", "end", values=(
                    KEY_LABELS[key], formatted_value))
                # Calculate maximum width for the Parameter column
                parameter_width = max(
                    parameter_width, len(KEY_LABELS[key]) * 10)

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

    def precompute_visualizations(self):
        """
        Precompute 3D visualization data for all days.
        """
        for state in self.simulation.states:
            points = []
            untinted_colors = []
            tinted_colors = []
            sizes = []

            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):
                        cell = state.grid[x][y][z]
                        base_color = cell.get_base_color()
                        tinted_color = cell.get_color_tinted_by_attributes()

                        if base_color:
                            points.append((x, y, z))
                            untinted_colors.append(base_color)
                            tinted_colors.append(tinted_color)
                            sizes.append(200.0)  # Adjust size as needed

            self.precomputed_data.append({
                "points": points,
                "untinted_colors": untinted_colors,
                "tinted_colors": tinted_colors,
                "sizes": sizes
            })



    def render_day(self, day):
        """
        Render the cached 3D visualization for a specific day with or without tinting.

        Args:
            day (int): The day to render.
        """
        # Save the current viewing angles
        if self.ax_3d:
            self.current_elev = self.ax_3d.elev
            self.current_azim = self.ax_3d.azim

        # Clear the existing plot
        self.ax_3d.cla()
        self.ax_3d.set_title(f"Day {day}")
        self.ax_3d.set_xlabel("X Axis")
        self.ax_3d.set_ylabel("Y Axis")
        self.ax_3d.set_zlabel("Z Axis")

        # Fetch precomputed data for the current day
        data = self.precomputed_data[day]
        points = data["points"]
        colors = data["tinted_colors" if self.tint else "untinted_colors"]
        sizes = data["sizes"]

        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore the saved viewing angles
        if hasattr(self, "current_elev") and hasattr(self, "current_azim"):
            self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)

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
            print(f"Data length mismatch in graph: {title}")

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
        standardized_data = self.standardize_data(self.simulation.city_population_over_time)
        # Assuming std deviation for population if available; if not, skip.
        standardized_std_dev = self.standardize_data(self.simulation.std_dev_city_population_over_time) 
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

    def toggle_tint(self, enable):
        """
        Toggle the tinting mode and re-render the current day's visualization.

        Args:
            enable (bool): Whether to enable tinting.
        """
        self.tint = enable  # Update the instance variable
        self.render_day(self.current_day)


