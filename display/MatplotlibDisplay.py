import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class MatplotlibDisplay:
    def __init__(self, simulation):
        self.simulation = simulation
        self.grid_size = simulation.grid_size

    def plot_3d(self):
        # יצירת חלון תלת-ממדי
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # רשימות לאחסון מיקומי תאים וצבעים
        x, y, z, colors = [], [], [], []

        # מעבר על הרשת התלת-ממדית
        for xi in range(self.grid_size):
            for yi in range(self.grid_size):
                for zi in range(self.grid_size):
                    cell = self.simulation.states[0].grid[xi, yi, zi]
                    x.append(xi)
                    y.append(yi)
                    z.append(zi)

                    # הגדרת צבעים לפי סוג התא
                    if cell.cell_type == 0:  # ים
                        colors.append('blue')
                    elif cell.cell_type == 1:  # יבשה
                        colors.append('green')
                    elif cell.cell_type == 2:  # עננים
                        colors.append('gray')
                    elif cell.cell_type == 3:  # קרחונים
                        colors.append('white')
                    elif cell.cell_type == 4:  # יערות
                        colors.append('darkgreen')
                    elif cell.cell_type == 5:  # ערים
                        colors.append('red')
                    elif cell.cell_type == 6:  # אוויר
                        colors.append('skyblue')
                    else:
                        colors.append('black')  # עבור תאים לא ידועים

        # ציור נקודות בתלת-ממד
        ax.scatter(x, y, z, c=colors, s=50)

        # הגדרת צירים
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        ax.set_title('3D Simulation Visualization')

        # הצגת הגרף
        plt.show()
