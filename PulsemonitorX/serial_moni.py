import sys
import serial
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider
)
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import find_peaks, butter, filtfilt

class SerialECGReader:
    def __init__(self, port='COM5', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.running = False

    def start(self):
        self.ser.reset_input_buffer()
        self.ser.write(b'1\r\n')
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
            print("Received:", line_data)
            if line_data.isdigit():
                return int(line_data[-3:])  # Last 3 digits as sample
        except Exception as e:
            print("Error:", e)
        return None

    def close(self):
        self.ser.close()

class ECGMonitor(QMainWindow):
    def __init__(self, port='COM5', baudrate=9600):
        super().__init__()
        self.setWindowTitle("ECG Serial Monitor")
        self.resize(1000, 500)

        self.buffer_size = 100
        self.data_buffer = [0] * self.buffer_size
        self.amplitude = 1200
        self.speed = 50  # ms per update
        self.fs = int(1000 / self.speed)  # Sampling frequency (Hz)

        self.serial_reader = SerialECGReader(port, baudrate)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.fig = Figure(facecolor='black')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('black')
        self.ax.set_ylim(0, self.amplitude)
        self.ax.set_xlim(0, self.buffer_size)
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.line, = self.ax.plot(range(self.buffer_size), self.data_buffer, color='lime', lw=2)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        controls = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.bpm_btn = QPushButton("Show BPM")
        self.bpm_label = QLabel("BPM: --")
        self.bpm_label.setStyleSheet("color: yellow; font-size: 16px; font-weight: bold;")
        self.amp_slider = QSlider(Qt.Horizontal)
        self.amp_slider.setMinimum(200)
        self.amp_slider.setMaximum(2000)
        self.amp_slider.setValue(self.amplitude)
        self.amp_slider.setTickInterval(200)
        self.amp_slider.setToolTip("Amplitude")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.setToolTip("Speed (ms/update)")
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.bpm_btn)
        controls.addWidget(self.bpm_label)
        controls.addWidget(QLabel("Amplitude"))
        controls.addWidget(self.amp_slider)
        controls.addWidget(QLabel("Speed"))
        controls.addWidget(self.speed_slider)
        layout.addLayout(controls)

        self.start_btn.clicked.connect(self.start_ecg)
        self.stop_btn.clicked.connect(self.stop_ecg)
        self.bpm_btn.clicked.connect(self.calculate_bpm)
        self.amp_slider.valueChanged.connect(self.change_amplitude)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

    def start_ecg(self):
        self.serial_reader.start()
        self.timer.start(self.speed)

    def stop_ecg(self):
        self.serial_reader.stop()
        self.timer.stop()

    def update_plot(self):
        value = self.serial_reader.read_value()
        if value is not None:
            self.data_buffer.append(value)
            if len(self.data_buffer) > self.buffer_size:
                self.data_buffer.pop(0)
            self.line.set_ydata(self.data_buffer)
            # Auto-scale Y-axis to fit data
            ymin = min(self.data_buffer) - 10
            ymax = max(self.data_buffer) + 10
            self.ax.set_ylim(ymin, ymax)
            self.canvas.draw_idle()

    def calculate_bpm(self):
        data = np.array(self.data_buffer)
        if len(data) < 10:
            self.bpm_label.setText("BPM: --")
            return
        peaks, _ = find_peaks(data, distance=self.fs/2, height=np.mean(data) + np.std(data)*0.5)
        if len(peaks) > 1:
            rr_intervals = np.diff(peaks) / self.fs
            bpm = 60 / np.mean(rr_intervals)
            self.bpm_label.setText(f"BPM: {int(bpm)}")
            if bpm < 60:
                self.bpm_label.setStyleSheet("color: blue; font-size: 16px; font-weight: bold;")
            elif bpm > 100:
                self.bpm_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
            else:
                self.bpm_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        else:
            self.bpm_label.setText("BPM: --")
            self.bpm_label.setStyleSheet("color: yellow; font-size: 16px; font-weight: bold;")

    def change_amplitude(self, value):
        self.amplitude = value
        self.ax.set_ylim(0, self.amplitude)
        self.canvas.draw_idle()

    def change_speed(self, value):
        self.speed = value
        if self.speed < 1:
            self.speed = 1
        self.fs = int(1000 / self.speed)
        if self.timer.isActive():
            self.timer.setInterval(self.speed)

    def on_scroll(self, event):
        # Vertical zoom in/out
        y_min, y_max = self.ax.get_ylim()
        y_range = y_max - y_min
        center = (y_max + y_min) / 2
        if event.button == 'up':
            # Zoom in
            scale = 0.9
        elif event.button == 'down':
            # Zoom out
            scale = 1.1
        else:
            scale = 1.0
        new_range = y_range * scale
        new_y_min = max(0, center - new_range / 2)
        new_y_max = center + new_range / 2
        self.ax.set_ylim(new_y_min, new_y_max)
        self.canvas.draw_idle()

    def closeEvent(self, event):
        self.serial_reader.close()
        event.accept()

def bandpass_filter(signal, fs, lowcut=0.5, highcut=40, order=2):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
    return filtfilt(b, a, signal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ECGMonitor(port='COM5', baudrate=9600)
    win.show()
    sys.exit(app.exec_())
