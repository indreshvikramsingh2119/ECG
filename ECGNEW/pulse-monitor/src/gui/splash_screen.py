from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont

class SplashScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Pulse Monitor - Splash Screen")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("Welcome to Pulse Monitor")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Logo
        logo_pixmap = QPixmap("path/to/logo.png")  # Update with the actual path to your logo
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Timer to transition to main window
        QTimer.singleShot(3000, self.goto_main)

    def goto_main(self):
        self.main_window.show()
        self.close()