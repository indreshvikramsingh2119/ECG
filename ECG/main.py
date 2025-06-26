from PyQt5.QtWidgets import QApplication, QStackedWidget
from ecg.ui.main_menu import MainMenu
import sys

def main():
    app = QApplication(sys.argv)
    stacked = QStackedWidget()
    main_menu = MainMenu(stacked)
    stacked.addWidget(main_menu)
    stacked.setCurrentWidget(main_menu)
    stacked.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()