import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFileDialog, QStackedWidget, QGridLayout, QSizePolicy,
    QDialog, QLineEdit, QFormLayout, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QFont, QMovie, QRegExpValidator, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QSize, QRegExp
from PyQt5.QtWidgets import QGraphicsBlurEffect
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np
from db_data import init_db, save_user
from firebase_auth import sign_up, sign_in
import webbrowser
import requests

init_db()  # Initialize the database

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guest Login")
        self.setFixedSize(750, 750)
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

        # Optional: Add a logo or icon
        icon_label = QLabel()
        icon_pixmap = QPixmap("pulse.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # Title
        title = QLabel("Guest Login")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                border-radius: 40px;
                border: 3px solid #00ff99;
                background: #222;
            }
        """)
        # Set a blank/default avatar (empty circle)
        blank_pixmap = QPixmap(100, 100)
        blank_pixmap.fill(Qt.transparent)
        self.avatar_label.setPixmap(blank_pixmap)
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        self.avatar_label.mousePressEvent = self.upload_profile_pic  # Make avatar clickable
        
        # Set default avatar from URL
        try:
            url = "https://img1.pnghut.com/1/25/23/T3q5NKrnTX/black-and-white-monochrome-alphanumeric-button-number.jpg"
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                # Crop to square (centered)
                size = min(pixmap.width(), pixmap.height())
                x = (pixmap.width() - size) // 2
                y = (pixmap.height() - size) // 2
                square = pixmap.copy(x, y, size, size)
                # Scale to fit avatar
                square = square.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                # Make it circular
                final_pixmap = QPixmap(100, 100)
                final_pixmap.fill(Qt.transparent)
                painter = QPainter(final_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, 100, 100)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, square)
                painter.end()
                self.avatar_label.setPixmap(final_pixmap)
            else:
                blank_pixmap = QPixmap(100, 100)
                blank_pixmap.fill(Qt.transparent)
                self.avatar_label.setPixmap(blank_pixmap)
        except Exception as e:
            print("Avatar image download failed:", e)
            blank_pixmap = QPixmap(100, 100)
            blank_pixmap.fill(Qt.transparent)
            self.avatar_label.setPixmap(blank_pixmap)

        layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)

        # Form fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setVerticalSpacing(16)
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password2 = QLineEdit()
        self.password2.setEchoMode(QLineEdit.Password)
        form.addRow("Email:", self.email)
        form.addRow("Password:", self.password)

        self.name = QLineEdit()
        self.name_row_added = False
        
        # Country code combo
        self.country_code = QComboBox()
        self.country_code.addItems([
            "+91 (India)", "+1 (USA)", "+44 (UK)", "+61 (Australia)", "+81 (Japan)", "+49 (Germany)", "+86 (China)", "+971 (UAE)"
        ])
        self.country_code.setFixedWidth(130)
        
        # Phone number field (digits only)
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone Number")
        digit_validator = QRegExpValidator(QRegExp(r'^\d{0,15}$'))  # Up to 15 digits, digits only
        self.phone.setValidator(digit_validator)
        self.age = QLineEdit()
        self.age.setPlaceholderText("Age")
        self.gender = QComboBox()
        self.gender.addItems(["M", "F", "Not Applicable"])
        self.address = QLineEdit()
        self.address.setPlaceholderText("Address")
        self.profile_pic_path = None

        form_widget = QWidget()
        form_widget.setLayout(form)
        layout.addWidget(form_widget)

        # Action buttons
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
        
    def create_phone_widget(self):
        phone_row = QHBoxLayout()
        phone_row.addWidget(self.country_code)
        phone_row.addWidget(self.phone)
        phone_widget = QWidget()
        phone_widget.setLayout(phone_row)
        return phone_widget

    def toggle_mode(self):
        self.is_signup = not self.is_signup
        if self.is_signup:
            self.setWindowTitle("Register User")
            self.action_btn.setText("Sign Up")
            self.switch_btn.setText("Already Registered?")
            if not self.name_row_added:
                self.form.insertRow(1, "Name:", self.name)
                
                phone_row = QHBoxLayout()
                phone_row.addWidget(self.country_code)
                phone_row.addWidget(self.phone)
                phone_widget = QWidget()
                phone_widget.setLayout(phone_row)

                self.form.insertRow(2, "Phone:", self.create_phone_widget())
                
                self.form.insertRow(3, "Age:", self.age)
                self.form.insertRow(4, "Gender:", self.gender)
                self.form.insertRow(5, "Address:", self.address)
                self.form.insertRow(7, "Confirm Password:", self.password2)
                self.name_row_added = True
        else:
            self.setWindowTitle("Guest Login")
            self.action_btn.setText("Sign In")
            self.switch_btn.setText("Register User?")
            if self.name_row_added:
                for _ in range(6):
                    self.form.removeRow(1)
                self.name_row_added = False
                
    def upload_profile_pic(self, event=None):
        path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.profile_pic_path = path
            pixmap = QPixmap(path)
            # Crop to square (centered)
            size = min(pixmap.width(), pixmap.height())
            x = (pixmap.width() - size) // 2
            y = (pixmap.height() - size) // 2
            square = pixmap.copy(x, y, size, size)
            # Scale to fit avatar
            square = square.scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            # Make it circular
            final_pixmap = QPixmap(100, 100)
            final_pixmap.fill(Qt.transparent)
            painter = QPainter(final_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, 100, 100)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, square)
            painter.end()
            self.avatar_label.setPixmap(final_pixmap)
            
    def google_sign_in(self):
        # Your Google OAuth 2.0 client info (from Google Cloud Console)
        CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
        REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
        SCOPE = "openid email profile"
        AUTH_URL = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={SCOPE}"
        )

        # Open browser for user to sign in
        webbrowser.open(AUTH_URL)
        # Ask user to paste the code
        code, ok = QInputDialog.getText(self, "Google Sign-In", "Paste the code from browser here:")
        if not ok or not code:
            return

        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        resp = requests.post(token_url, data=data)
        if resp.status_code != 200:
            QMessageBox.warning(self, "Error", "Failed to get token from Google.")
            return
        tokens = resp.json()
        id_token = tokens.get("id_token")

        # Get user info from id_token (JWT)
        userinfo = requests.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
        ).json()
        email = userinfo.get("email")
        name = userinfo.get("name")
        uid = userinfo.get("sub")

        # Save to your local DB
        from db_data import save_user
        save_user(uid, email, name)
        QMessageBox.information(self, "Success", f"Signed in as {name} ({email})")
        self.accept()

    def handle_auth(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        if self.is_signup:
            password2 = self.password2.text().strip()
            if password != password2:
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            name = self.name.text().strip()
            country_code = self.country_code.currentText().split()[0]  # e.g., "+91"
            phone = self.phone.text().strip()
            full_phone = f"{country_code}{phone}"
            age = self.age.text().strip()
            gender = self.gender.currentText()
            address = self.address.text().strip()
            profile_pic = self.profile_pic_path
            if not name or not phone or not age or not address:
                QMessageBox.warning(self, "Error", "Please fill all fields.")
                return
            result = sign_up(email, password)
            if "error" in result:
                QMessageBox.warning(self, "Error", result["error"]["message"])
            else:
                # Save user with all details
                save_user(
                    result["localId"], email, name,
                    phone=full_phone, age=age, gender=gender, address=address, profile_pic=profile_pic
                )
                self.logged_in_name = name
                QMessageBox.information(self, "Success", "Sign Up successful!")
                self.accept()
        else:
            result = sign_in(email, password)
            if "error" in result:
                QMessageBox.warning(self, "Error", result["error"]["message"])
            else:
                # You may want to fetch the user's name from your DB here
                from db_data import get_user_by_email
                user = get_user_by_email(email)
                self.logged_in_name = user[3] if user else email  # user[3] is name
                QMessageBox.information(self, "Success", "Sign In successful!")
                self.accept()

# --- Serial Reader ---
class SerialECGReader:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.running = False

    def start(self):
        self.ser.reset_input_buffer()
        self.ser.write(b'1\r\n')
        time.sleep(0.5)  # Wait half a second
        self.running = True

    def stop(self):
        self.ser.write(b'0\r\n')
        self.running = False

    def read_value(self):
        if not self.running:
            return None
        try:
            line_raw = self.ser.readline()
            line_data = line_raw.decode('utf-8', errors='replace').strip()
            if line_data:
                print("Received:", line_data)
            if line_data.isdigit():
                return int(line_data[-3:])  # Last 3 digits as sample
        except Exception as e:
            print("Error:", e)
        return None

    def close(self):
        self.ser.close()

# --- Live Lead Window ---
class LiveLeadWindow(QWidget):
    def __init__(self, lead_name, data_source, buffer_size=80, color="#00ff99"):
        super().__init__()
        self.setWindowTitle(f"Live View: {lead_name}")
        self.resize(900, 300)
        self.lead_name = lead_name
        self.data_source = data_source  # Should be a callable returning the latest buffer for this lead
        self.buffer_size = buffer_size
        self.color = color

        layout = QVBoxLayout(self)
        self.fig = Figure(facecolor='#000')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#000')
        self.ax.set_ylim(-400, 400)
        self.ax.set_xlim(0, buffer_size)
        self.line, = self.ax.plot([0]*buffer_size, color=self.color, lw=2)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # 10 FPS instead of 20

    def update_plot(self):
        data = self.data_source()
        if data and len(data) > 0:
            plot_data = np.full(self.buffer_size, np.nan)
            n = min(len(data), self.buffer_size)
            centered = np.array(data[-n:]) - np.mean(data[-n:])
            plot_data[-n:] = centered
            self.line.set_ydata(plot_data)
            self.canvas.draw_idle()

# --- Test Page ---
class ECGTestPage(QWidget):
    LEADS_MAP = {
        "Lead II ECG Test": ["Lead II"],
        "Lead III ECG Test": ["Lead III"],
        "7 Lead ECG Test": ["V1", "V2", "V3", "V4", "V5", "V6", "Lead II"],
        "12 Lead ECG Test": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "ECG Live Monitoring": ["Lead II"]
    }

    LEAD_COLORS = {
        "I": "#00ff99",
        "II": "#ff0055",
        "III": "#0099ff",
        "aVR": "#ff9900",
        "aVL": "#cc00ff",
        "aVF": "#00ccff",
        "V1": "#ffcc00",
        "V2": "#00ffcc",
        "V3": "#ff6600",
        "V4": "#6600ff",
        "V5": "#00b894",
        "V6": "#ff0066"
    }

    def expand_lead(self, idx):
        lead = self.leads[idx]
        def get_lead_data():
            return self.data[lead]
        # Assign a color for the lead
        color = self.LEAD_COLORS.get(lead, "#00ff99")
        win = LiveLeadWindow(lead, get_lead_data, buffer_size=self.buffer_size, color=color)
        win.show()
        # Keep a reference so it doesn't get garbage collected
        if not hasattr(self, "_live_windows"):
            self._live_windows = []
        self._live_windows.append(win)
    def __init__(self, test_name, stacked_widget):
        super().__init__()
        self.test_name = test_name
        self.leads = self.LEADS_MAP[test_name]
        self.buffer_size = 80
        self.data = {lead: [] for lead in self.leads}
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.serial_reader = None
        self.stacked_widget = stacked_widget
        self.lines = []
        self.axs = []
        self.canvases = []

        # --- Add menu buttons on the left ---
        menu_frame = QGroupBox("Menu")
        menu_layout = QVBoxLayout(menu_frame)
        menu_buttons = [
            ("Save ECG", self.save_ecg),
            ("Open ECG", self.open_ecg),
            ("Working Mode", self.working_mode),
            ("Printer Setup", self.printer_setup),
            ("Set Filter", self.set_filter),
            ("System Setup", self.system_setup),
            ("Load Default", self.load_default),
            ("Version", self.version_info),
            ("Factory Maintain", self.factory_maintain),
            ("Exit", self.exit_app)
        ]
        for text, handler in menu_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            btn.clicked.connect(handler)
            menu_layout.addWidget(btn)
        menu_layout.addStretch(1)

        # --- Main vertical layout for content (right side) ---
        main_vbox = QVBoxLayout()
        # --- Connection settings ---
        conn_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.baud_combo = QComboBox()
        self.baud_combo.addItem("Select Baud Rate")
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        conn_layout.addWidget(QLabel("Serial Port:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(QLabel("Baud Rate:"))
        conn_layout.addWidget(self.baud_combo)
        self.refresh_ports()
        main_vbox.addLayout(conn_layout)

        # --- Plot area ---
        self.plot_area = QWidget()
        main_vbox.addWidget(self.plot_area)
        self.update_lead_layout()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.export_pdf_btn = QPushButton("Export as PDF")
        self.export_csv_btn = QPushButton("Export as CSV")
        self.back_btn = QPushButton("Back")
        self.ecg_plot_btn = QPushButton("Open ECG Live Plot")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        btn_layout.addWidget(self.export_csv_btn)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.ecg_plot_btn)
        main_vbox.addLayout(btn_layout)

        self.start_btn.clicked.connect(self.start_acquisition)
        self.stop_btn.clicked.connect(self.stop_acquisition)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.back_btn.clicked.connect(self.go_back)
        self.ecg_plot_btn.clicked.connect(lambda: run_ecg_live_plot(port='/cu.usbserial-10', baudrate=9600, buffer_size=100))

        # --- Combine menu and main content ---
        main_hbox = QHBoxLayout(self)
        main_hbox.addWidget(menu_frame)
        main_hbox.addLayout(main_vbox)
        self.setLayout(main_hbox)

        # --- Style ---
        self.setStyleSheet("""
            QWidget { background-color: #000; color: #fff; }
            QGroupBox {
                border: 2px solid #fff;
                border-radius: 10px;
                margin-top: 10px;
                font-weight: bold;
                color: #fff;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #fff;
            }
            QPushButton {
                background-color: #fff;
                color: #000;
                border-radius: 16px;
                padding: 12px 0;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff99;
                color: #000;
            }
            QComboBox, QLineEdit {
                background-color: #000;
                color: #fff;
                border: 1px solid #fff;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #000;
                color: #fff;
                selection-background-color: #fff;
                selection-color: #000;
            }
        """)

    def refresh_ports(self):
        self.port_combo.clear()
        self.port_combo.addItem("Select Port")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def update_lead_layout(self):
        # Remove old layout/widgets
        old_layout = self.plot_area.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            self.plot_area.setLayout(None)
        # Clear old lists
        self.figures = []
        self.canvases = []
        self.axs = []
        self.lines = []
        # Create grid layout
        grid = QGridLayout()
        self.figures = []
        self.canvases = []
        self.axs = []
        n_leads = len(self.leads)
        if n_leads == 12:
            rows, cols = 3, 4
        elif n_leads == 7:
            rows, cols = 2, 4
        else:
            rows, cols = 1, 1
        for idx, lead in enumerate(self.leads):
            row, col = divmod(idx, cols)
            group = QGroupBox(lead)
            vbox = QVBoxLayout(group)
            fig = Figure(facecolor='#000', figsize=(6, 2.5))  # Large, clear plot
            ax = fig.add_subplot(111)
            ax.set_facecolor('#000')
            ax.set_ylim(0, 999)
            ax.set_xlim(0, self.buffer_size)
            line, = ax.plot([0]*self.buffer_size, color='#00ff99', lw=1.5)
            self.lines.append(line)
            canvas = FigureCanvas(fig)
            vbox.addWidget(canvas)
            grid.addWidget(group, row, col)
            self.figures.append(fig)
            self.canvases.append(canvas)
            self.axs.append(ax)
        self.plot_area.setLayout(grid)

        for i, canvas in enumerate(self.canvases):
            canvas.mpl_connect('button_press_event', lambda event, idx=i: self.expand_lead(idx))

    def start_acquisition(self):
        port = self.port_combo.currentText()
        baud = self.baud_combo.currentText()
        if port == "Select Port" or baud == "Select Baud Rate":
            self.show_connection_warning()
            return
        try:
            if self.serial_reader:
                self.serial_reader.close()
            self.serial_reader = SerialECGReader(port, int(baud))
            self.serial_reader.start()
            self.timer.start(50)
        except Exception as e:
            self.show_connection_warning(str(e))

    def stop_acquisition(self):
        port = self.port_combo.currentText()
        baud = self.baud_combo.currentText()
        if port == "Select Port" or baud == "Select Baud Rate":
            self.show_connection_warning()
            return
        if self.serial_reader:
            self.serial_reader.stop()
        self.timer.stop()

    def update_plot(self):
        if not self.serial_reader:
            return
        line = self.serial_reader.ser.readline()
        line_data = line.decode('utf-8', errors='replace').strip()
        if not line_data:
            return

        # Print the raw received data to the terminal
        print("Received:", line_data)

        # Split the incoming string into values (assuming space-separated)
        try:
            values = [int(x) for x in line_data.split()]
            if len(values) != 8:
                return  # Not enough data, skip this frame

            # Map values to leads
            lead1 = values[0]
            v4    = values[1]
            v5    = values[2]
            lead2 = values[3]
            v3    = values[4]
            v6    = values[5]
            v1    = values[6]
            v2    = values[7]

            # Calculate derived leads
            lead3 = lead2 - lead1
            avr = - (lead1 + lead2) / 2
            avl = (lead1 - lead3) / 2
            avf = (lead2 + lead3) / 2

            # Assign all 12 leads
            lead_data = {
                "I": lead1,
                "II": lead2,
                "III": lead3,
                "aVR": avr,
                "aVL": avl,
                "aVF": avf,
                "V1": v1,
                "V2": v2,
                "V3": v3,
                "V4": v4,
                "V5": v5,
                "V6": v6
            }

            # Append to buffers and plot
            for i, lead in enumerate(self.leads):
                self.data[lead].append(lead_data[lead])
                if len(self.data[lead]) > self.buffer_size:
                    self.data[lead].pop(0)

            # Plot as before
            for i, lead in enumerate(self.leads):
                if len(self.data[lead]) > 0:
                    if len(self.data[lead]) < self.buffer_size:
                        pad = [self.data[lead][0]] * (self.buffer_size - len(self.data[lead]))
                        data = pad + self.data[lead]
                    else:
                        data = self.data[lead]
                    centered = np.array(data) - np.mean(data)
                    self.lines[i].set_ydata(centered)
                    self.axs[i].set_ylim(-400, 400)
                    self.canvases[i].draw_idle()
        except Exception as e:
            print("Error parsing ECG data:", e)

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export ECG Data as PDF", "", "PDF Files (*.pdf)")
        if path:
            from matplotlib.backends.backend_pdf import PdfPages
            with PdfPages(path) as pdf:
                for fig in self.figures:
                    pdf.savefig(fig)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export ECG Data as CSV", "", "CSV Files (*.csv)")
        if path:
            import csv
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Sample"] + self.leads)
                for i in range(self.buffer_size):
                    row = [i]
                    for lead in self.leads:
                        if i < len(self.data[lead]):
                            row.append(self.data[lead][i])
                        else:
                            row.append("")
                    writer.writerow(row)

    def go_back(self):
        self.stop_acquisition()
        if self.serial_reader:
            self.serial_reader.close()
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(1)  # MainMenu is at index 1

    def show_connection_warning(self, extra_msg=""):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Connection Required")
        msg.setText("❤️ Please select a COM port and baud rate.\n\nStay healthy!" + ("\n\n" + extra_msg if extra_msg else ""))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def save_ecg(self):
        QMessageBox.information(self, "Save ECG", "Save ECG clicked.")

    def open_ecg(self):
        QMessageBox.information(self, "Open ECG", "")

    def working_mode(self):
        QMessageBox.information(self, "Working Mode", "Working Mode clicked.")

    def printer_setup(self):
        QMessageBox.information(self, "Printer Setup", "Printer Setup clicked.")

    def set_filter(self):
        QMessageBox.information(self, "Set Filter", "Set Filter clicked.")

    def system_setup(self):
        QMessageBox.information(self, "System Setup", "System Setup clicked.")

    def load_default(self):
        QMessageBox.information(self, "Load Default", "Load Default clicked.")

    def version_info(self):
        QMessageBox.information(self, "Version", "Version clicked.")

    def factory_maintain(self):
        QMessageBox.information(self, "Factory Maintain", "Factory Maintain clicked.")

    def exit_app(self):
        self.close()

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
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addRow(btns)

    def get_settings(self):
        try:
            ymin = float(self.ylim_min.text())
            ymax = float(self.ylim_max.text())
            color = self.color.text()
            return (ymin, ymax), color
        except Exception:
            return None, None

    def expand_lead(self, idx):
        lead = self.leads[idx]
        def get_lead_data():
            return self.data[lead]
        win = LiveLeadWindow(lead, get_lead_data, buffer_size=self.buffer_size)
        win.show()
        # Keep a reference so it doesn't get garbage collected
        if not hasattr(self, "_live_windows"):
            self._live_windows = []
        self._live_windows.append(win)

# --- Main Menu ---
class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # --- Fullscreen blurred background ---
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_pixmap = QPixmap("ecg-electrodes-chest-athlete-vector-illustration-106463995.webp")
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(20)
        self.bg_label.setGraphicsEffect(blur)
        self.bg_label.lower()

        # --- Overlay layout for main content ---
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        overlay_layout.setContentsMargins(40, 40, 40, 40)
        overlay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Deckmount logo ---
        logo_label = QLabel()
        logo_pixmap = QPixmap("Deckmount.webp")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(logo_label)

        # --- Title ---
        self.title_label = QLabel("PulseMonitorX")
        self.title_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.title_label.setStyleSheet("color: #00ff99; background: transparent; letter-spacing: 2px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(self.title_label)
        
        # ---  User name display 
        self.user_label = QLabel("")
        self.user_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.user_label.setStyleSheet("color: #000; background: transparent;")
        self.user_label.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(self.user_label)

        # --- Guest Login Button ---
        self.guest_btn = QPushButton("Guest Login")
        self.guest_btn.setMinimumHeight(48)
        self.guest_btn.setFont(QFont("Arial", 16, QFont.Bold))
        self.guest_btn.setCursor(Qt.PointingHandCursor)
        self.guest_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fff, stop:1 #00ff99);
                color: #00b894;
                border-radius: 24px;
                padding: 12px 36px;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #00ff99;
                box-shadow: 0px 4px 12px #00ff9955;
            }
            QPushButton:hover {
                background: #00ff99;
                color: #fff;
                border: 2px solid #fff;
            }
        """)
        self.guest_btn.clicked.connect(self.show_auth_dialog)
        overlay_layout.addWidget(self.guest_btn)
        overlay_layout.addSpacing(30)
        
        # --- Sign Out Button ---
        self.signout_btn = QPushButton("Sign Out")
        self.signout_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.signout_btn.setStyleSheet("""
            QPushButton {
                background: #fff;
                color: #00b894;
                border-radius: 16px;
                padding: 8px 24px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #00ff99;
            }
            QPushButton:hover {
                background: #00ff99;
                color: #fff;
                border: 2px solid #fff;
            }
        """)
        self.signout_btn.setCursor(Qt.PointingHandCursor)
        self.signout_btn.hide()
        self.signout_btn.clicked.connect(self.sign_out)
        
        # --- Sign Out Button centered below user name ---
        signout_row = QHBoxLayout()
        signout_row.addStretch(1)
        signout_row.addWidget(self.signout_btn)
        signout_row.addStretch(1)
        overlay_layout.addLayout(signout_row)

        # --- Two Square Buttons ---
        btn_grid = QGridLayout()
        btn_grid.setSpacing(40)
        btn_names = [
            "12 Lead ECG Test",
            "ECG Live Monitoring"
        ]
        self.buttons = []
        for i, name in enumerate(btn_names):
            btn = QPushButton(name)
            btn.setMinimumSize(220, 220)
            btn.setFont(QFont("Arial", 20, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ff99, stop:1 #00b894);
                    color: #000;
                    border-radius: 32px;
                    font-size: 22px;
                    font-weight: bold;
                    border: 4px solid #fff;
                    box-shadow: 0px 8px 24px #00ff9955;
                }
                QPushButton:hover {
                    background: #fff;
                    color: #00b894;
                    border: 4px solid #00ff99;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.open_test_page(n))
            btn_grid.addWidget(btn, i // 2, i % 2, Qt.AlignCenter)
            self.buttons.append(btn)
        overlay_layout.addLayout(btn_grid)

        # --- ECG Wave GIF at the Bottom ---
        overlay_layout.addStretch(1)
        ecg_gif_label = QLabel()
        ecg_gif_label.setAlignment(Qt.AlignCenter)
        ecg_movie = QMovie("ecgwave.gif")
        ecg_gif_label.setMovie(ecg_movie)
        ecg_movie.setScaledSize(QSize(400, 60))  # Adjust width/height as needed
        ecg_movie.start()
        overlay_layout.addWidget(ecg_gif_label, alignment=Qt.AlignCenter)
        overlay_layout.addSpacing(10)

        # --- Make overlay fill the window ---
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.raise_()
        self.overlay = overlay
        
    def show_auth_dialog(self):
        dlg = AuthDialog()
        if dlg.exec_() == QDialog.Accepted:
            user_name = dlg.logged_in_name
            if user_name:
                self.user_label.setText(f"Welcome, {user_name}!")
                self.guest_btn.hide()
                self.signout_btn.show()
                
    def sign_out(self):
        self.user_label.setText("")
        self.guest_btn.show()
        self.signout_btn.hide()

    def resizeEvent(self, event):
        self.bg_label.setPixmap(self.bg_pixmap.scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def open_test_page(self, test_name):
        test_page = ECGTestPage(test_name, self.stacked_widget)
        self.stacked_widget.addWidget(test_page)
        self.stacked_widget.setCurrentWidget(test_page)

# --- Splash Screen ---
class SplashScreen(QWidget):
    def __init__(self, stacked_widget, main_page):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_page = main_page
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("PulseMonitorX by Divyansh")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # GIF animation
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignCenter)
        movie = QMovie("tenor.gif")
        gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(gif_label)

        # Auto-continue after 3.5 seconds
        QTimer.singleShot(3500, self.goto_main)

    def goto_main(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

# --- Main Application ---
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PulseMonitorX")
        self.resize(1200, 900)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.menu = MainMenu(self.stacked_widget)
        self.splash = SplashScreen(self.stacked_widget, self.menu)
        self.stacked_widget.addWidget(self.splash)    # index 0
        self.stacked_widget.addWidget(self.menu)    # index 1
        self.stacked_widget.setCurrentWidget(self.splash)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked = QStackedWidget()

    # Replace YourMainPage with your actual main page class
    main_page = MainMenu(stacked)  
    splash = SplashScreen(stacked, main_page)

    stacked.addWidget(splash)
    stacked.addWidget(main_page)
    stacked.setCurrentWidget(splash)
    stacked.resize(900, 600)
    stacked.show()
    sys.exit(app.exec_())

    # --- ECG Live Plot Function ---
def run_ecg_live_plot(port='/cu.usbserial-10', baudrate=9600, buffer_size=100):
    # Serial setup
    ser = serial.Serial(port, baudrate, timeout=0.01)
    time.sleep(2)

    data_buffer = [0] * buffer_size

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    line, = ax.plot(range(buffer_size), data_buffer, color='#00ff99', lw=1.5)
    ax.set_title("Real-Time ECG Graph (Lead II)")
    ax.set_xlabel("Samples")
    ax.set_ylabel("Amplitude")
    ax.set_xlim(0, buffer_size)
    ax.set_ylim(0, 1200)
    ax.set_facecolor('#000')
    ax.grid(which='major', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(which='minor', color='lightgray', linestyle=':', linewidth=0.3, alpha=0.3)
    ax.minorticks_on()
    ax.xaxis.set_major_locator(plt.MultipleLocator(20))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
    ax.yaxis.set_major_locator(plt.MultipleLocator(200))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(50))

    is_running = [False]

    def start_clicked(event):
        if not is_running[0]:
            ser.write(b'1\r\n')
            ser.reset_input_buffer()   # Flush old data immediately after sending start
            is_running[0] = True
            print("Started receiving data...")

    def stop_clicked(event):
        if is_running[0]:
            ser.write(b'0\r\n')
            is_running[0] = False
            print("Stopped receiving data.")

    ax_start = plt.axes([0.3, 0.05, 0.15, 0.075])
    ax_stop = plt.axes([0.55, 0.05, 0.15, 0.075])
    btn_start = Button(ax_start, 'Start')
    btn_stop = Button(ax_stop, 'Stop')
    btn_start.on_clicked(start_clicked)
    btn_stop.on_clicked(stop_clicked)

    def update(frame):
        if is_running[0]:
            try:
                line_raw = ser.readline()
                line_data = line_raw.decode('utf-8', errors='replace').strip()
                if line_data.isdigit():
                    value = int(line_data[-3:])  # Only last three digits
                    print("Received (last 3 digits):", value)
                    data_buffer.append(value)
                    if len(data_buffer) > buffer_size:
                        data_buffer.pop(0)
                    centered = np.array(data_buffer) - np.mean(data_buffer)
                    line.set_ydata(centered)
                    ax.set_ylim(-500, 500)  # Adjust as needed
            except Exception as e:
                print("Error:", e)
        return line,

    ani = FuncAnimation(fig, update, interval=10, blit=False)
    plt.show()

    # Cleanup
    ser.write(b'0\r\n')
    ser.close()
    print("Serial port closed.")

    airflow = np.array([...])  # your data
    centered = airflow - np.mean(airflow)
    plt.plot(centered)

    # --- Derived Leads Calculation ---
lead3 = lead2 - lead1
avr = - (lead1 + lead2) / 2
avl = (lead1 - lead3) / 2
avf = (lead2 + lead3) / 2

lead_data = {
    "I": lead1,
    "II": lead2,
    "III": lead3,
    "aVR": avr,
    "aVL": avl,
    "aVF": avf,
    "V1": v1,
    "V2": v2,
    "V3": v3,
    "V4": v4,
    "V5": v5,
    "V6": v6
}

import threading