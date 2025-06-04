import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QLineEdit
from PyQt5.QtCore import QTimer

class SerialSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_simulation()

    def init_ui(self):
        self.setWindowTitle("Serial Data Simulation")
        self.setGeometry(200, 200, 400, 300)

        # Create layout
        self.layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        # Create labels for data
        self.labels = {}
        for index, label_name in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
            label = QLabel(f"{label_name}: ")
            value = QLineEdit("0")
            value.setReadOnly(True)
            self.grid_layout.addWidget(label, index, 0)
            self.grid_layout.addWidget(value, index, 1)
            self.labels[label_name] = value

        self.layout.addLayout(self.grid_layout)
        self.setLayout(self.layout)

    def init_simulation(self):
        # Simulation variables
        self.counter = 1
        self.increment = 1

        # Timer for simulation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_values)
        self.timer.start(100)  # Simulate 100ms delay

    def update_values(self):
        # Calculate values
        A = self.counter
        B = 101 - A
        C = A * 2
        D = 200 - (2 * A)
        E = A * 3
        F = 300 - (3 * A)

        # Update the GUI
        self.labels['A'].setText(str(A))
        self.labels['B'].setText(str(B))
        self.labels['C'].setText(str(C))
        self.labels['D'].setText(str(D))
        self.labels['E'].setText(str(E))
        self.labels['F'].setText(str(F))

        # Adjust counter for up and down behavior
        if self.counter >= 100:
            self.increment = -1
        elif self.counter <= 1:
            self.increment = 1

        self.counter += self.increment

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialSimulation()
    window.show()
    sys.exit(app.exec_())
