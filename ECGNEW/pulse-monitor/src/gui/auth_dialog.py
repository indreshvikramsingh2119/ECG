from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox, QHBoxLayout, QWidget
)
from PyQt5.QtGui import QFont, QPixmap
from firebase_auth import sign_up, sign_in
from db_data import save_user

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guest Login")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000, stop:1 #00ff99);
                border-radius: 18px;
            }
            QLabel {
                color: #fff;
                font-size: 18px;
                font-weight: bold;
            }
            QLineEdit {
                background: #222;
                color: #fff;
                border: 2px solid #00ff99;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff99, stop:1 #00b894);
                color: #000;
                border-radius: 14px;
                padding: 10px 0;
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #fff;
                color: #00b894;
                border: 2px solid #00ff99;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_pixmap = QPixmap("pulse.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        title = QLabel("Guest Login")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)

        self.name = QLineEdit()
        self.name_row_added = False

        form_widget = QWidget()
        form_widget.setLayout(form)
        layout.addWidget(form_widget)

        self.action_btn = QPushButton("Sign In")
        self.switch_btn = QPushButton("Register User?")
        self.action_btn.clicked.connect(self.handle_auth)
        self.switch_btn.clicked.connect(self.toggle_mode)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.action_btn)
        btn_row.addWidget(self.switch_btn)
        layout.addLayout(btn_row)

        self.is_signup = False
        self.form = form

    def toggle_mode(self):
        self.is_signup = not self.is_signup
        if self.is_signup:
            self.setWindowTitle("Register User")
            self.action_btn.setText("Sign Up")
            self.switch_btn.setText("Already Registered?")
            if not self.name_row_added:
                self.form.insertRow(1, "Name:", self.name)
                self.name_row_added = True
        else:
            self.setWindowTitle("Guest Login")
            self.action_btn.setText("Sign In")
            self.switch_btn.setText("Register User?")
            if self.name_row_added:
                self.form.removeRow(1)
                self.name_row_added = False

    def handle_auth(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        if self.is_signup:
            name = self.name.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Please enter your name.")
                return
            result = sign_up(email, password)
            if "error" in result:
                QMessageBox.warning(self, "Error", result["error"]["message"])
            else:
                save_user(result["localId"], email, name)
                QMessageBox.information(self, "Success", "Sign Up successful!")
                self.accept()
        else:
            result = sign_in(email, password)
            if "error" in result:
                QMessageBox.warning(self, "Error", result["error"]["message"])
            else:
                QMessageBox.information(self, "Success", "Sign In successful!")
                self.accept()