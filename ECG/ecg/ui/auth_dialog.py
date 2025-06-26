from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guest Login")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Email:"))
        self.email = QLineEdit()
        layout.addWidget(self.email)
        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        btn = QPushButton("Sign In")
        layout.addWidget(btn)