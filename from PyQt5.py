from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsBlurEffect, QHBoxLayout, QPushButton
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        # Fullscreen background image with blur
        self.bg_label = QLabel(self)
        pixmap = QPixmap("ecg-electrodes-chest-athlete-vector-illustration-106463995.webp")
        self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setScaledContents(True)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(25)
        self.bg_label.setGraphicsEffect(blur)
        self.bg_label.lower()  # Make sure it's behind everything

        # Overlay layout for main content
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)

        # Example: Title and buttons
        title = QLabel("PulseMonitorX")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("color: #00ff99; background: transparent;")
        overlay_layout.addWidget(title)

        # Buttons (example)
        btn_layout = QHBoxLayout()
        for text in ["Lead II", "Lead III", "Lead 7", "Lead 12", "ECG Live Monitoring"]:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #fff;
                    color: #000;
                    border-radius: 12px;
                    padding: 16px 32px;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #00ff99;
                    color: #000;
                }
            """)
            btn_layout.addWidget(btn)
        overlay_layout.addLayout(btn_layout)

        # Make overlay fill the window
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.raise_()

    def resizeEvent(self, event):
        # Keep background and overlay full screen on resize
        self.bg_label.setPixmap(QPixmap("ecg-electrodes-chest-athlete-vector-illustration-106463995.webp").scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.children()[1].setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)