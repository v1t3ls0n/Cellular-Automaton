import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import to_rgba
import numpy as np
import logging
from core.conf import config, key_labels, format_config_value
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
        self.main_window.title("Environmental Simulation Application Main Window")
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


        style = ttk.Style()
        style.configure("TScrollbar", gripcount=0, background="gray", width=40)

        # Create a scrollable canvas
        scrollable_canvas = tk.Canvas(self.main_window, highlightthickness=0)
        scrollable_canvas.grid(row=1, column=0, sticky="nsew")

        # Add vertical and horizontal scrollbars
        vertical_scrollbar = tk.Scrollbar(self.main_window, orient="vertical", command=scrollable_canvas.yview,width=30)
        vertical_scrollbar.grid(row=1, column=1, sticky="ns")

        horizontal_scrollbar = tk.Scrollbar(self.main_window, orient="horizontal", command=scrollable_canvas.xview,width = 30)
        horizontal_scrollbar.grid(row=2, column=0, sticky="ew")

        scrollable_canvas.configure(yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

        # Create a frame inside the canvas for Matplotlib content
        scrollable_frame = tk.Frame(scrollable_canvas)
        scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Dynamically adjust the canvas size
        def _on_configure(event):
            scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_configure)

        # Enable mouse wheel scrolling
        def _on_mouse_wheel(event):
            if event.state & 0x1:  # Shift key pressed -> horizontal scroll
                scrollable_canvas.xview_scroll(-1 * (event.delta // 120), "units")
            else:
                scrollable_canvas.yview_scroll(-1 * (event.delta // 120), "units")

        scrollable_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        # Create a Matplotlib figure
        fig = plt.Figure(figsize=(20, 25), constrained_layout=True)  # Adjust figure size
        gs = fig.add_gridspec(5, 2, width_ratios=[1, 1], hspace=0.3, wspace=0.3)

        self.fig = fig
        self.canvas = FigureCanvasTkAgg(self.fig, master=scrollable_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Create subplots
        self.axes = {
            "pollution": self.fig.add_subplot(gs[0, 0]),
            "std_dev_pollution": self.fig.add_subplot(gs[0, 1]),
            "temperature": self.fig.add_subplot(gs[1, 0]),
            "std_dev_temperature": self.fig.add_subplot(gs[1, 1]),
            "water_mass": self.fig.add_subplot(gs[2, 0]),
            "std_dev_water_mass": self.fig.add_subplot(gs[2, 1]),
            "population": self.fig.add_subplot(gs[3, 0]),
            "forests": self.fig.add_subplot(gs[3, 1]),
            "cell_distribution_std_dev": self.fig.add_subplot(gs[4, 0]),
        }

        # Render graphs
        self.render_pollution_graph(self.axes["pollution"], color="red")
        self.render_std_dev_pollution_graph(self.axes["std_dev_pollution"], color="orange")
        self.render_temperature_graph(self.axes["temperature"], color="blue")
        self.render_std_dev_temperature_graph(self.axes["std_dev_temperature"], color="cyan")
        self.render_water_mass_graph(self.axes["water_mass"], color="green")
        self.render_std_dev_water_mass_graph(self.axes["std_dev_water_mass"], color="lime")
        self.render_population_graph(self.axes["population"], color="purple")
        self.render_forests_graph(self.axes["forests"], color="brown")
        self.render_std_dev_cell_distribution_graph(self.axes["cell_distribution_std_dev"], color="darkgoldenrod")
        # Set square aspect ratio for all graphs
        for ax in self.axes.values():
            ax.set_box_aspect(1)



        def _on_resize(self, event):
            """Adjust the figure size dynamically on window resize."""
            canvas_width = event.width
            canvas_height = event.height
            self.fig.set_size_inches(canvas_width / 100, canvas_height / 100)
            self.fig.tight_layout()
            self.canvas.draw_idle()
            # Optimize layout to reduce gray areas
            self.fig.tight_layout(pad=0.5, h_pad=0.2, w_pad=0.2)

            # Add 3D visualization and config table
            self.open_3d_in_new_window(self.main_window)
            self.add_config_table_with_scrollbar(self.main_window)
        # Bind resizing event to dynamically adjust figure size
        self.canvas.get_tk_widget().bind("<Configure>", _on_resize)

        # Add scrollbars
        self._add_scrollbars()


        # Optimize layout to reduce gray areas
        self.fig.tight_layout(pad=0.5, h_pad=0.2, w_pad=0.2)

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
            ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)

            # Legend area
            ax_color_map = fig.add_subplot(gs[0, 1])
            ax_color_map.axis("off")  # Hide axes for the legend

            # Legend elements
            legend_elements = [
                plt.Line2D([0], [0], marker="o", color="w", label="0 : Ocean", markersize=10,
                           markerfacecolor=self.config["base_colors"][0]),
                plt.Line2D([0], [0], marker="o", color="w", label="1 : Desert", markersize=10,
                           markerfacecolor=self.config["base_colors"][1]),
                plt.Line2D([0], [0], marker="o", color="w", label="2 : Cloud", markersize=10,
                           markerfacecolor=self.config["base_colors"][2]),
                plt.Line2D([0], [0], marker="o", color="w", label="3 : Ice", markersize=10,
                           markerfacecolor=self.config["base_colors"][3]),
                plt.Line2D([0], [0], marker="o", color="w", label="4 : Forest", markersize=10,
                           markerfacecolor=self.config["base_colors"][4]),
                plt.Line2D([0], [0], marker="o", color="w", label="5 : City", markersize=10,
                           markerfacecolor=self.config["base_colors"][5]),
                plt.Line2D([0], [0], marker="o", color="w", label="6 : Air", markersize=10,
                           markerfacecolor=self.config["base_colors"][6]),
                plt.Line2D([0], [0], marker="o", color="w", label="7 : Rain", markersize=10,
                           markerfacecolor=self.config["base_colors"][7]),
                plt.Line2D([0], [0], marker="o", color="w", label="8 : Vacuum", markersize=10,
                           markerfacecolor=self.config["base_colors"][8]),
            ]
            if self.config.get('tint'):
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w', label='9: Pollution (Tint)',
                               markersize=10, markerfacecolor='red')
                )

            # Add a single legend to the color map axis
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
                        ax_3d.scatter(xs, ys, zs, c=colors, s=sizes)
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
            def rgba_to_hex(rgba):
                r, g, b, a = rgba  # Extract RGBA components
                return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

                    # Add each legend item with padding
                for text, color in legend_items:
                        # Convert RGBA color to Hex if necessary
                        hex_color = rgba_to_hex(color) if isinstance(
                            color, tuple) else color

                        item_frame = tk.Frame(legend_frame, bg="white")
                        item_frame.pack(fill=tk.X, padx=(20, 20), pady=(
                            10, 10))  # Add padding around each item

                        # Create a circular color indicator using Canvas
                        canvas = tk.Canvas(item_frame, width=24, height=24,
                                        bg="white", highlightthickness=0)
                        canvas.pack(side=tk.LEFT, padx=(10, 10))
                        canvas.create_oval(2, 2, 22, 22, fill=hex_color,
                                        outline="black")  # Draw a circle

                        # Add the text description
                        text_label = tk.Label(
                            item_frame,
                            text=text,
                            font=("Arial", 10),
                            bg="white",
                            anchor="w"
                        )
                        # Add space between text and circle
                        text_label.pack(side=tk.LEFT, padx=(10, 10))

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
                                for dx in np.linspace(-0.1, 0.1, 2):
                                    for dy in np.linspace(-0.1, 0.1, 2):
                                        for dz in np.linspace(-0.1, 0.1, 2):
                                            points.append(
                                                (x + dx, y + dy, z + dz))
                                            colors.append(
                                                to_rgba(cell.get_color()))
                                            # Larger size for denser appearance
                                            sizes.append(80)

                                points.append((x, y, z))
                                colors.append(to_rgba(cell.get_color()))
                                # Larger size for denser appearance
                                sizes.append(100)

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
            self.ax_3d.view_init(elev=self.current_elev,
                                 azim=self.current_azim)

            self.fig.canvas.draw_idle()






    def render_population_graph(self, ax, color):
        """Render the city population graph over time."""
        ax.cla()
        ax.set_title("City Population Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Number of Cities")

        # Retrieve data
        city_population = self.simulation.city_population_over_time

        # Plot the data
        ax.plot(self.days, city_population, color=color, label="Cities")
        ax.legend()


        
    def render_forests_graph(self, ax, color):
        """Render the forest count graph over time."""
        ax.cla()
        ax.set_title("Forest Count Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Number of Forests")

        # Retrieve data
        forest_count = self.simulation.forest_count_over_time

        ax.plot(self.days, forest_count, color=color, label="Forests")
        ax.legend()



    def render_temperature_graph(self, ax, color):
        """Render the standard deviation of temperature graph over time."""
        ax.cla()
        ax.set_title("Temperature Standard Deviation Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Standard Deviation Temperature")

        # Ensure correct data availability
        avg_temperature = self.simulation.temperature_over_time
        std_dev_temperature = self.simulation.std_dev_temperature_over_time

        # Add standard deviation as shaded region
        ax.fill_between(
            self.days,
            np.array(avg_temperature) - np.array(std_dev_temperature),
            np.array(avg_temperature) + np.array(std_dev_temperature),
            color="blue", alpha=0.1, label="Temperature Std Dev Range"
        )

        ax.plot(self.days, avg_temperature, color=color, label="Average Temperature")
        ax.legend()



    def render_pollution_graph(self, ax, color):
        """Render the pollution graph over time with standard deviation."""
        ax.cla()
        ax.set_title("Pollution Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Average Pollution")

        avg_pollution = self.simulation.pollution_over_time
        pollution_std_dev = self.simulation.std_dev_pollution_over_time

        # Add standard deviation as shaded region
        ax.fill_between(
            self.days,
            np.array(avg_pollution) - np.array(pollution_std_dev),
            np.array(avg_pollution) + np.array(pollution_std_dev),
            color="red", alpha=0.2, label="Pollution Std Dev Range"
        )

        ax.plot(self.days, avg_pollution, color=color, label="Pollution")
        ax.legend()



    def render_std_dev_pollution_graph(self, ax, color):
        """Render the standard deviation of pollution graph over time."""
        ax.cla()
        ax.set_title("Pollution Standard Deviation Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Standard Deviation Pollution")

        std_dev_pollution = self.simulation.std_dev_pollution_over_time
        ax.plot(self.days, std_dev_pollution, color=color, label="Pollution Std Dev")
        ax.legend()



    def render_std_dev_temperature_graph(self, ax, color):
        """Render the standard deviation of temperature graph over time."""
        ax.cla()
        ax.set_title("Temperature Standard Deviation Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Standard Deviation Temperature")

        std_dev_temperature = self.simulation.std_dev_temperature_over_time
        ax.plot(self.days, std_dev_temperature, color=color, label="Temperature Std Dev")
        ax.legend()



    def render_water_mass_graph(self, ax, color):
        """Render the average water mass graph over time with standard deviation limits."""
        ax.cla()
        ax.set_title("Average Water Mass Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Average Water Mass")

        avg_water_mass = self.simulation.water_mass_over_time
        std_dev_water_mass = self.simulation.std_dev_water_mass_over_time

        # Add standard deviation as shaded region
        ax.fill_between(
            self.days,
            np.array(avg_water_mass) - np.array(std_dev_water_mass),
            np.array(avg_water_mass) + np.array(std_dev_water_mass),
            color="blue", alpha=0.1, label="Water Mass Std Dev Range"
        )

        ax.plot(self.days, avg_water_mass, color=color, label="Average Water Mass")
        ax.legend()



    def render_std_dev_water_mass_graph(self, ax, color):
        """Render the standard deviation of water mass graph over time."""
        ax.cla()
        ax.set_title("Standard Deviation of Water Mass Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Water Mass Std Dev")

        std_dev_water_mass = self.simulation.std_dev_water_mass_over_time
        ax.plot(self.days, std_dev_water_mass, color=color, label="Water Mass Std Dev")
        ax.legend()



    def render_std_dev_cell_distribution_graph(self, ax, color):
        """Render the standard deviation of cell type distribution over time."""
        ax.cla()
        ax.set_title("Std Dev of Cell Type Distribution Over Time")
        ax.set_xlabel("Day")
        ax.set_ylabel("Std Dev of Cell Counts")

        std_dev_distribution = self.simulation.std_dev_cell_distribution_over_time
        ax.plot(self.days, std_dev_distribution, color=color, label="Std Dev Cell Distribution")
        ax.legend()

















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
