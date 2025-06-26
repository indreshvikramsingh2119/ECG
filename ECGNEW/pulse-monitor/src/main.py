import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.db_data import init_db

def main():
    app = QApplication(sys.argv)
    init_db()  # Initialize the database
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()