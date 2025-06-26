import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFileDialog, QStackedWidget, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QGraphicsBlurEffect
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from PulsemonitorX.ecg_plotter import ECGPlotter
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np

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

# --- Test Page ---
class ECGTestPage(QWidget):
    LEADS_MAP = {
        "Lead II ECG Test": ["Lead II"],
        "Lead III ECG Test": ["Lead III"],
        "7 Lead ECG Test": ["V1", "V2", "V3", "V4", "V5", "V6", "Lead II"],
        "12 Lead ECG Test": ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
        "ECG Live Monitoring": ["Lead II"]
    }
    def __init__(self, test_name, stacked_widget):
        super().__init__()
        self.test_name = test_name
        self.leads = self.LEADS_MAP[test_name]
        self.buffer_size = 80  # Show only 80 samples for clarity
        self.data = {lead: [] for lead in self.leads}
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.serial_reader = None
        self.stacked_widget = stacked_widget
        self.lines = []
        self.axs = []
        self.canvases = []

        main_layout = QVBoxLayout(self)
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
        main_layout.addLayout(conn_layout)

        # --- Plot area ---
        self.plot_area = QWidget()
        main_layout.addWidget(self.plot_area)
        self.update_lead_layout()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.export_pdf_btn = QPushButton("Export as PDF")
        self.export_csv_btn = QPushButton("Export as CSV")
        self.back_btn = QPushButton("Back")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.export_pdf_btn)
        btn_layout.addWidget(self.export_csv_btn)
        btn_layout.addWidget(self.back_btn)
        main_layout.addLayout(btn_layout)

        self.start_btn.clicked.connect(self.start_acquisition)
        self.stop_btn.clicked.connect(self.stop_acquisition)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.back_btn.clicked.connect(self.go_back)

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
        value = self.serial_reader.read_value()
        if value is not None:
            for i, lead in enumerate(self.leads):
                v = value + i*100  # For demo, offset each lead
                self.data[lead].append(v)
                if len(self.data[lead]) > self.buffer_size:
                    self.data[lead].pop(0)
                ax = self.axs[i]
                ax.clear()
                ax.set_facecolor('#000')
                ax.set_ylim(0, 999)
                ax.set_xlim(0, self.buffer_size)
                ax.plot(self.data[lead], color='#00ff99', lw=2)
                ax.set_title(lead, color='white', fontsize=10)
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
                self.canvases[i].draw_idle()

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

    def expand_lead(self, idx):
        import matplotlib.pyplot as plt
        import numpy as np

        lead = self.leads[idx]
        data = np.array(self.data[lead]) - np.mean(self.data[lead])  # Centered

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(data, color='#00ff99', lw=2)
        ax.set_title(f"Enlarged View: {lead}")
        ax.set_facecolor('#000')
        ax.set_ylim(-400, 400)  # Or adjust as needed
        ax.set_xlim(0, len(data))
        ax.grid(True, color='gray', alpha=0.3)
        plt.show()

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
        overlay_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        overlay_layout.setContentsMargins(40, 40, 40, 40)
        overlay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Deckmount logo ---
        logo_label = QLabel()
        logo_pixmap = QPixmap("Deckmount.webp")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(logo_label)

        # --- Title ---
        title = QLabel("PulseMonitorX")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("color: #00ff99; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        overlay_layout.addWidget(title)

        # --- Buttons ---
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(20)
        btn_names = [
            "Lead II ECG Test",
            "Lead III ECG Test",
            "7 Lead ECG Test",
            "12 Lead ECG Test",
            "ECG Live Monitoring"
        ]
        self.buttons = []
        for name in btn_names:
            btn = QPushButton(name)
            btn.setMinimumHeight(48)
            btn.setFont(QFont("Arial", 18, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background: #fff;
                    color: #000;
                    border-radius: 16px;
                    padding: 12px 0;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #00ff99;
                    color: #000;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.open_test_page(n))
            btn_layout.addWidget(btn)
            self.buttons.append(btn)
        overlay_layout.addLayout(btn_layout)

        # --- Make overlay fill the window ---
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.raise_()
        self.overlay = overlay

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
        # img_label = QLabel()
        # pixmap = QPixmap("pulse.png")
        # img_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # img_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(img_label)
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
def run_ecg_live_plot(port='COM5', baudrate=9600, buffer_size=100):
    # Serial setup
    ser = serial.Serial('COM5', 9600, timeout=0.01)
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
                    line.set_ydata(data_buffer)
                    ax.set_ylim(0, 999)  # Fixed y-limits for last 3 digits
            except Exception as e:
                print("Error:", e)
        return line,

    ani = FuncAnimation(fig, update, interval=10, blit=False)
    plt.show()

    # Cleanup
    ser.write(b'0\r\n')
    ser.close()
    print("Serial port closed.")

# To run this as a script:
if __name__ == "__main__":
    run_ecg_live_plot(port='COM5', baudrate=9600, buffer_size=100)