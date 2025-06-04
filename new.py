import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import re

# Serial config
port = "COM5"
baud_rate = 9600
timeout = 1

# Open serial port
ser = serial.Serial(port, baud_rate, timeout=timeout, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS)
print(f"Connected to {port} at {baud_rate} baud.")

# Send '1' to start data transmission
ser.write(b'1\r\n')
print("Sent start command ('1') to device.")

# Data buffer for plotting
buffer_size = 200
data_buffer = [0] * buffer_size

# Plot setup
fig, ax = plt.subplots()
line, = ax.plot(data_buffer, color='r', lw=2)
ax.set_title("Real-Time ECG")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.set_xlim(0, buffer_size)
ax.set_ylim(0, 1200000)  # Adjust if needed

# ECG-style grid
ax.set_facecolor('#fff0f5')
ax.grid(which='major', color='r', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(which='minor', color='k', linestyle=':', linewidth=0.3, alpha=0.3)
ax.minorticks_on()
ax.xaxis.set_major_locator(plt.MultipleLocator(50))
ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
ax.yaxis.set_major_locator(plt.MultipleLocator(200000))
ax.yaxis.set_minor_locator(plt.MultipleLocator(50000))

def update(frame):
    try:
        raw = ser.readline()
        line_data = raw.decode(errors='replace').strip()
        print(f"Received: {line_data}")  # <-- Show every line on terminal
        # Only plot lines that are all digits (ignore RH:... lines)
        if line_data.isdigit():
            value = int(line_data)
            data_buffer.append(value)
            if len(data_buffer) > buffer_size:
                data_buffer.pop(0)
            line.set_data(range(buffer_size), data_buffer)
            ax.set_ylim(min(data_buffer) - 10000, max(data_buffer) + 10000)
    except Exception as e:
        print(f"Error: {e}")
    return line,

ani = FuncAnimation(fig, update, interval=20)
plt.show()

# On close, send '0' to stop and close port
ser.write(b'0\r\n')
ser.close()
print("Serial port closed.")
