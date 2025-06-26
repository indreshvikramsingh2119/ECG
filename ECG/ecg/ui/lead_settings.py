from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton

class LeadSettingsDialog(QDialog):
    def __init__(self, parent=None, current_ylim=(-400, 400), current_color="#00ff99"):
        super().__init__(parent)
        self.setWindowTitle("Lead Settings")
        self.setModal(True)
        layout = QFormLayout(self)
        self.ylim_min = QLineEdit(str(current_ylim[0]))
        self.ylim_max = QLineEdit(str(current_ylim[1]))
        self.color = QLineEdit(current_color)
        layout.addRow("Y min:", self.ylim_min)
        layout.addRow("Y max:", self.ylim_max)
        layout.addRow("Line Color (hex):", self.color)
        btns = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addRow(btns)