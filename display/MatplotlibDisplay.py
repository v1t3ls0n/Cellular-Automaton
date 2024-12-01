import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np
import logging
from core.conf import config, key_labels,  format_config_value
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MatplotlibDisplay:
    config = config

    def __init__(self, simulation):
        self.simulation = simulation
        self.precomputed_results = simulation.states  # Use precomputed results
        self.current_day = 0
        self.fig = None
        self.ax_3d = None
        self.three_d_window = None
        self.ax_pollution = None
        self.ax_temperature = None
        self.ax_population = None
        self.ax_forests = None
        self.ax_std_dev_pollution_graph = None
        self.ax_std_dev_temperature_graph = None
        self.ax_ice_coverage = None
        self.precomputed_data = []  # Cache for precomputed 3D scatter data
        self.current_elev = 20  # Default elevation
        self.current_azim = 45  # Default azimuth

    def plot_3d(self):
        self.precompute_visualizations()

        # Open 3D visualization in a separate window
        self.open_3d_in_new_window()

        
        """Create the plot with all relevant graphs, including the configuration window."""
        # Create the main Tkinter root window for the simulation
        root = tk.Tk()
        root.title("Environmental Simulation Results")

        # Maximize the window without entering full-screen mode
        root.state("zoomed")

        # Define a clean exit function
        def on_close():
            root.destroy()  # Close the main simulation window
            exit(0)  # Ensure the Python script exits

        # Set the window close protocol
        root.protocol("WM_DELETE_WINDOW", on_close)


        # Configure row and column resizing for the root
        root.rowconfigure(1, weight=1)  # Make the plot area expandable
        root.columnconfigure(0, weight=1)

        # Create a frame for the buttons (minimal height)
        control_frame = tk.Frame(root)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Create a frame for the control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Add buttons to the control frame with reduced width
        # button_width = 25  # Set a fixed width for all buttons
        tk.Button(control_frame, text="Bring Initial Parameters Table Window to Front",
                command=self.bring_config_to_front, width=button_width).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Minimize Initial Parameters Table Window",
                command=self.minimize_config_window, width=button_width).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Minimize 3D Window",
                command=self.minimize_3d_window, width=button_width).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Bring 3D Visualization to Front",
                command=self.bring_3d_to_front, width=button_width).pack(side=tk.LEFT, padx=5)

        # Create a frame for the plots (maximum height)
        plot_frame = tk.Frame(root)
        plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Configure plot frame to expand
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)

        # Create the main figure
        self.fig = plt.Figure(figsize=(16, 8), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")


        # Use GridSpec for flexible layout
        spec = gridspec.GridSpec(nrows=3, ncols=2, figure=self.fig)
        
        # Configure axes for the plots
        self.ax_pollution = self.fig.add_subplot(spec[0, 0])
        self.ax_std_dev_pollution_graph = self.fig.add_subplot(spec[1, 0])
        self.ax_temperature = self.fig.add_subplot(spec[0, 1])
        self.ax_std_dev_temperature_graph = self.fig.add_subplot(spec[1, 1])
        self.ax_population = self.fig.add_subplot(spec[2, 0])
        self.ax_forests = self.fig.add_subplot(spec[2, 1])

        # Render initial graphs
        self.render_pollution_graph()
        self.render_temperature_graph()
        self.render_population_graph()
        self.render_forests_graph()
        self.render_std_dev_pollution_graph()
        self.render_std_dev_temperature_graph()



        # Start the Tkinter event loop
        root.mainloop()

    def bring_config_to_front(self):
        """Bring the configuration window to the front."""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.deiconify()
            self.config_window.lift()
            self.config_window.focus_force()

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

    def minimize_3d_window(self):
        """Minimize the 3D visualization window."""
        if self.three_d_window and self.three_d_window.winfo_exists():
            self.three_d_window.iconify()

    def add_config_table_with_scrollbar(self, root=None):
        """Create a configuration table window with scrollbars and add control buttons."""
        # Create a new window for the configuration table
        self.config_window = tk.Toplevel(root)
        self.config_window.title("Configuration Table")

        # Ensure the configuration window stays on top of the main window initially
        # Keeps the window in front
        self.config_window.attributes("-topmost", True)
        self.config_window.lift()  # Brings it to the top
        # self.config_window.focus_force()  # Sets focus to this window

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

        # Dynamically adjust the window size based on table content
        table_width = parameter_width + value_width + 50  # Extra padding
        # Adjust height to avoid oversized windows
        table_height = min(500, len(self.config) * 25 + 100)

        # Apply the calculated dimensions to the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = min(table_width, screen_width * 0.9)
        window_height = min(table_height, screen_height * 0.9)

        self.config_window.geometry(
            f"{int(window_width)}x{int(window_height)}")

        # Remove the topmost attribute after focusing on the window
        self.config_window.after(
            1000, lambda: self.config_window.attributes("-topmost", False))
   













    def open_3d_in_new_window(self):
        """Open a resizable 3D graph window with a Matplotlib legend and keyboard navigation."""
        self.three_d_window = tk.Toplevel()
        self.three_d_window.title("3D Visualization")
        self.three_d_window.geometry("1200x600")  # Default size
        self.three_d_window.minsize(800, 500)  # Minimum size
        self.three_d_window.columnconfigure(0, weight=3)  # Column for 3D plot
        self.three_d_window.columnconfigure(1, weight=1)  # Column for legend
        self.three_d_window.rowconfigure(0, weight=1)  # Flexible row for content

        # Frame for the 3D plot
        fig = plt.Figure(figsize=(8, 6), constrained_layout=True)
        ax_3d = fig.add_subplot(111, projection="3d")

        # Fetch data for the current day
        points, colors, sizes = self.precomputed_data[self.current_day]
        xs, ys, zs = zip(*points) if points else ([], [], [])
        ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        ax_3d.set_title(f"Day {self.current_day}")
        ax_3d.set_xlabel("X Axis")
        ax_3d.set_ylabel("Y Axis")
        ax_3d.set_zlabel("Z Axis")

        # Add the 3D plot to the window
        canvas = FigureCanvasTkAgg(fig, master=self.three_d_window)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        canvas.draw()

        # Create a separate Matplotlib figure for the legend
        legend_fig = plt.Figure(figsize=(2, 6), constrained_layout=True)
        legend_ax = legend_fig.add_subplot(111)
        legend_ax.axis("off")  # Hide axes

        # Create legend elements
        legend_elements = [
            plt.Line2D([0], [0], marker="o", color="w", label="0: Ocean", markersize=10,
                    markerfacecolor=self.config["base_colors"][0]),
            plt.Line2D([0], [0], marker="o", color="w", label="1: Desert", markersize=10,
                    markerfacecolor=self.config["base_colors"][1]),
            plt.Line2D([0], [0], marker="o", color="w", label="2: Cloud", markersize=10,
                    markerfacecolor=self.config["base_colors"][2]),
            plt.Line2D([0], [0], marker="o", color="w", label="3: Ice", markersize=10,
                    markerfacecolor=self.config["base_colors"][3]),
            plt.Line2D([0], [0], marker="o", color="w", label="4: Forest", markersize=10,
                    markerfacecolor=self.config["base_colors"][4]),
            plt.Line2D([0], [0], marker="o", color="w", label="5: City", markersize=10,
                    markerfacecolor=self.config["base_colors"][5]),
            plt.Line2D([0], [0], marker="o", color="w", label="6: Air", markersize=10,
                    markerfacecolor=self.config["base_colors"][6]),
            plt.Line2D([0], [0], marker="o", color="w", label="7: Rain", markersize=10,
                    markerfacecolor=self.config["base_colors"][7]),
            plt.Line2D([0], [0], marker="o", color="w", label="8: Vacuum", markersize=10,
                    markerfacecolor=self.config["base_colors"][8]),
        ]

        if self.config.get("tint"):
            legend_elements.append(
                plt.Line2D([0], [0], marker="o", color="w", label="9: Pollution", markersize=10,
                        markerfacecolor="red")
            )

        # Add the legend to the legend_ax
        legend_ax.legend(
            handles=legend_elements,
            loc="center",
            title="Cell Types",
            frameon=True,
            fontsize=10,
            title_fontsize=12,
        )

        # Add the legend figure to the Tkinter window
        legend_canvas = FigureCanvasTkAgg(legend_fig, master=self.three_d_window)
        legend_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        legend_canvas.draw()

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
            """Update the 3D plot in the separate window."""
            ax_3d.cla()
            ax_3d.set_title(f"Day {self.current_day}")
            ax_3d.set_xlabel("X Axis")
            ax_3d.set_ylabel("Y Axis")
            ax_3d.set_zlabel("Z Axis")

            # Fetch data for the updated day
            points, colors, sizes = self.precomputed_data[self.current_day]
            xs, ys, zs = zip(*points) if points else ([], [], [])
            ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

            # Redraw the canvas
            canvas.draw_idle()

        # Bind the keyboard event handler to the canvas
        fig.canvas.mpl_connect("key_press_event", handle_key_press)

        # Add dynamic resizing
        def on_resize(event):
            """Adjust the 3D plot and legend dynamically."""
            plot_width = self.three_d_window.winfo_width() * 0.7 / 100
            plot_height = self.three_d_window.winfo_height() / 100
            legend_width = self.three_d_window.winfo_width() * 0.2 / 100
            fig.set_size_inches(plot_width, plot_height)
            legend_fig.set_size_inches(legend_width, plot_height)
            canvas.draw_idle()
            legend_canvas.draw_idle()

        self.three_d_window.bind("<Configure>", on_resize)











    def add_cell_type_legend_to_frame(self, legend_frame):
        """Add a well-padded legend explaining the cell colors and cell type numbers."""
        # Add a title at the top of the legend
        title_label = tk.Label(
            legend_frame,
            text="Cell Types",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        title_label.pack(pady=(10, 10))  # Add space above and below the title

        # Define legend items
        legend_items = [
            ("0: Ocean", self.config["base_colors"][0]),
            ("1: Desert", self.config["base_colors"][1]),
            ("2: Cloud", self.config["base_colors"][2]),
            ("3: Ice", self.config["base_colors"][3]),
            ("4: Forest", self.config["base_colors"][4]),
            ("5: City", self.config["base_colors"][5]),
            ("6: Air (White With Low Opacity)", self.config["base_colors"][6]),
            ("7: Rain", self.config["base_colors"][7]),
            ("8: Vacuum (Transparent)", self.config["base_colors"][8]),
        ]

        # Add tinted pollution if enabled
        if self.config.get("tint"):
            legend_items.append(("9: Pollution Levels (Tinted Color)", "red"))

        # Function to convert RGBA to Hex
        def rgba_to_hex(rgba):
            r, g, b, a = rgba  # Extract RGBA components
            return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

        # Add each legend item with padding
        for text, color in legend_items:
            # Convert RGBA color to Hex if necessary
            hex_color = rgba_to_hex(color) if isinstance(color, tuple) else color

            item_frame = tk.Frame(legend_frame, bg="white")
            item_frame.pack(fill=tk.X, padx=(20, 20), pady=(10, 10))  # Add padding around each item

            # Create a circular color indicator using Canvas
            canvas = tk.Canvas(item_frame, width=24, height=24, bg="white", highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(10, 10))
            canvas.create_oval(2, 2, 22, 22, fill=hex_color, outline="black")  # Draw a circle

            # Add the text description
            text_label = tk.Label(
                item_frame,
                text=text,
                font=("Arial", 10),
                bg="white",
                anchor="w"
            )
            text_label.pack(side=tk.LEFT, padx=(10, 10))  # Add space between text and circle


    def precompute_visualizations(self):
        # # Render initial graphs
        """Precompute 3D scatter data for all precomputed states."""
        logging.info("Precomputing 3D visualizations...")
        for state in self.simulation.states:
            points = []
            colors = []
            sizes = []  # Add a list for point sizes
            for x in range(state.grid.shape[0]):
                for y in range(state.grid.shape[1]):
                    for z in range(state.grid.shape[2]):

                        cell = state.grid[x][y][z]
                        if cell.get_color() is not None:
                            # Interpolate multiple points for "densification"
                            # Fine-tune interpolation
                            # for dx in np.linspace(-0.1, 0.1, 2):
                            #     for dy in np.linspace(-0.1, 0.1, 2):
                            #         for dz in np.linspace(-0.1, 0.1, 2):
                            #             points.append((x + dx, y + dy, z + dz))
                            #             colors.append(
                            #                 to_rgba(cell.get_color()))
                            #             # Larger size for denser appearance
                            #             sizes.append(80)

                            points.append((x , y , z ))
                            colors.append(to_rgba(cell.get_color()))
                            sizes.append(100)  # Larger size for denser appearance

            self.precomputed_data.append((points, colors, sizes))
        logging.info("3D Precomputation complete.")

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
        xs, ys, zs = zip(*points) if points else ([], [], [])
        self.ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

        # Restore the saved viewing angles
        self.ax_3d.view_init(elev=self.current_elev, azim=self.current_azim)

        self.fig.canvas.draw_idle()

    def render_population_graph(self):
        """Render the city population graph over time."""
        self.ax_population.cla()
        self.ax_population.set_title("City Population Over Time")
        self.ax_population.set_xlabel("Day")
        self.ax_population.set_ylabel("Number of Cities")

        # Retrieve data
        days = range(len(self.simulation.city_population_over_time))
        city_population = self.simulation.city_population_over_time

        # Ensure data matches the length of days
        if len(days) == len(city_population):
            self.ax_population.plot(
                days, city_population, color="purple", label="Cities")
            self.ax_population.legend()
        else:
            logging.error("Data length mismatch in population graph.")

    def render_forests_graph(self):
        """Render the forest count graph over time."""
        self.ax_forests.cla()
        self.ax_forests.set_title("Forest Count Over Time")
        self.ax_forests.set_xlabel("Day")
        self.ax_forests.set_ylabel("Number of Forests")

        # Retrieve data
        days = range(len(self.simulation.forest_count_over_time))
        forest_count = self.simulation.forest_count_over_time

        if len(days) == len(forest_count):
            self.ax_forests.plot(days, forest_count,
                                 color="green", label="Forests")
            self.ax_forests.legend()
        else:
            logging.error("Data length mismatch in forest graph.")

    def render_temperature_graph(self):
        """Render the standard deviation of temperature graph over time."""
        self.ax_temperature.cla()
        self.ax_temperature.set_title(
            "Temperature Standard Deviation Over Time")
        self.ax_temperature.set_xlabel("Day")
        self.ax_temperature.set_ylabel(
            "Standard Deviation Temperature")

        # Ensure correct data availability
        days = range(len(self.simulation.std_dev_temperature_over_time))
        std_dev_temperature = self.simulation.std_dev_temperature_over_time

        if len(days) == len(std_dev_temperature):
            avg_temperature = self.simulation.temperature_over_time

            # Add standard deviation as shaded region
            self.ax_temperature.fill_between(
                days,
                np.array(avg_temperature) - np.array(std_dev_temperature),
                np.array(avg_temperature) + np.array(std_dev_temperature),
                color="blue", alpha=0.1, label="Temperature Std Dev Range")

            self.ax_temperature.plot(
                days, avg_temperature, color="blue", label="Average Temperature")
            self.ax_temperature.legend()
        else:
            logging.error(
                "Data length mismatch in temperature standard deviation graph.")

    def render_pollution_graph(self):
        """Render the pollution graph over time with standard deviation."""
        self.ax_pollution.cla()
        self.ax_pollution.set_title("Pollution Over Time")
        self.ax_pollution.set_xlabel("Day")
        self.ax_pollution.set_ylabel("Average Pollution")

        # Retrieve data
        days = range(len(self.simulation.pollution_over_time))
        avg_pollution = self.simulation.pollution_over_time

        # Calculate standard deviation for pollution
        pollution_std_dev = self.simulation.std_dev_pollution_over_time

        if len(days) == len(avg_pollution) and len(days) == len(pollution_std_dev):
            # Add standard deviation as shaded region
            self.ax_pollution.fill_between(
                days,
                np.array(avg_pollution) - np.array(pollution_std_dev),
                np.array(avg_pollution) + np.array(pollution_std_dev),
                color="red", alpha=0.2, label="Pollution Std Dev Range"
            )

            # Plot the average pollution
            self.ax_pollution.plot(days, avg_pollution, color="red", label="Pollution")
            self.ax_pollution.legend()
        else:
            logging.error("Data length mismatch in pollution graph or standard deviation.")
    def render_std_dev_pollution_graph(self):
        """Render the standard deviation of pollution graph over time."""
        self.ax_std_dev_pollution_graph.cla()
        self.ax_std_dev_pollution_graph.set_title(
            "Pollution Standard deviation Over Time")
        self.ax_std_dev_pollution_graph.set_xlabel("Day")
        self.ax_std_dev_pollution_graph.set_ylabel(
            "Standard deviation Pollution")

        # Corrected attribute name
        days = range(len(self.simulation.std_dev_pollution_over_time))
        # Corrected attribute name
        std_dev_pollution = self.simulation.std_dev_pollution_over_time

        if len(days) == len(std_dev_pollution):
            self.ax_std_dev_pollution_graph.plot(
                days, std_dev_pollution, color="orange", label="Pollution Standard deviation"
            )
            self.ax_std_dev_pollution_graph.legend()
        else:
            logging.error(
                "Data length mismatch in pollution Standard deviation graph.")

    def render_std_dev_temperature_graph(self):
        """Render the standard deviation of temperature graph over time."""
        self.ax_std_dev_temperature_graph.cla()
        self.ax_std_dev_temperature_graph.set_title(
            "Temperature Standard deviation Over Time")
        self.ax_std_dev_temperature_graph.set_xlabel("Day")
        self.ax_std_dev_temperature_graph.set_ylabel(
            "Standard deviation Temperature")

        # Corrected attribute name
        days = range(len(self.simulation.std_dev_temperature_over_time))
        # Corrected attribute name
        std_dev_temperature = self.simulation.std_dev_temperature_over_time

        if len(days) == len(std_dev_temperature):
            self.ax_std_dev_temperature_graph.plot(
                days, std_dev_temperature, color="cyan", label="Temperature Standard deviation"
            )
            self.ax_std_dev_temperature_graph.legend()
        else:
            logging.error(
                "Data length mismatch in temperature Standard deviation graph.")

    def next_day(self):
        if self.current_day < len(self.simulation.states) - 1:
            self.current_day += 1
            self.render_day(self.current_day)

    def previous_day(self):
        if self.current_day > 0:
            self.current_day -= 1
            self.render_day(self.current_day)