from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap

class SplashScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        img = QLabel()
        img.setPixmap(QPixmap("assets/pulse.png"))
        layout.addWidget(img)
        label = QLabel("PulseMonitorX")
        layout.addWidget(label)