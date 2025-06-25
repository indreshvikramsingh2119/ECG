from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("PulseMonitorX Main Menu")
        layout.addWidget(label)
        btn = QPushButton("Go to ECG Test")
        layout.addWidget(btn)
        # Connect button to navigation logic