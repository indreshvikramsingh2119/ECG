from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QStatusBar, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Monitor")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.create_menu()
        self.create_status_bar()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def show_about(self):
        self.status_bar.showMessage("Pulse Monitor Application - Version 1.0", 5000)