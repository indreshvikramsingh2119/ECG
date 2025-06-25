import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class ECGPlotter:
    def __init__(self, buffer_size=100):
        self.buffer_size = buffer_size
        self.data_buffer = [0] * buffer_size

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(range(buffer_size), self.data_buffer, color='#00ff99', lw=1.5)
        self.ax.set_title("Real-Time ECG Graph (Lead II)")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlim(0, buffer_size)
        self.ax.set_ylim(0, 1200)
        self.ax.set_facecolor('#000')
        self.ax.grid(which='major', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
        self.ax.grid(which='minor', color='lightgray', linestyle=':', linewidth=0.3, alpha=0.3)
        self.ax.minorticks_on()
        self.ax.xaxis.set_major_locator(plt.MultipleLocator(20))
        self.ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
        self.ax.yaxis.set_major_locator(plt.MultipleLocator(200))
        self.ax.yaxis.set_minor_locator(plt.MultipleLocator(50))

    def update_wave(self, value):
        self.data_buffer.append(value)
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)
        self.line.set_ydata(self.data_buffer)
        self.ax.set_ylim(min(self.data_buffer) - 10, max(self.data_buffer) + 10)
        plt.pause(0.001)  # For interactive update

    def show(self):
        plt.show()