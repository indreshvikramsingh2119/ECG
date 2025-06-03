import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import re

# Parameters
port = "COM8"
baud_rate = 9600
buffer_size = 1000  # Number of data points to display on the graph
 
# Initialize serial connection
try:
    ser = serial.Serial(
        port, baud_rate,
        bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, timeout=1
    )
    print(f"Connected to {port} at {baud_rate} baud")
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

# Data buffer
data_buffer = [0] * buffer_size  # Start with zeros for smooth scrolling

# Initialize the plot
fig, ax = plt.subplots()
line, = ax.plot(range(buffer_size), data_buffer, label="ECG Wave", lw=2)
ax.set_title("Real-Time ECG Data")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.set_xlim(0, buffer_size)
ax.set_ylim(0, 255)  # Adjust if your ECG values are outside this range
ax.legend()

def handle_non_numeric(data_buffer):
    valid_values = [v for v in data_buffer if not np.isnan(v)]
    return np.mean(valid_values) if valid_values else 0

def update(frame):
    global data_buffer
    try:
        raw_bytes = ser.readline()
        line_data = raw_bytes.decode('utf-8', errors='replace').strip()
        print(f"Raw bytes: {raw_bytes}")
        print(f"Decoded data: '{line_data}'")

        # Extract the number after the colon (e.g., X:43 -> 43)
        match = re.search(r":(\d+)", line_data)
        if match:
            value = int(match.group(1))
            print(f"Plotted value: {value}")
        else:
            print(f"No numeric value found in: '{line_data}'")
            value = handle_non_numeric(data_buffer)

        # Update the buffer (rolling window)
        data_buffer.append(value)
        if len(data_buffer) > buffer_size:
            data_buffer.pop(0)

        # Update plot data
        line.set_data(range(buffer_size), data_buffer)
        # Optionally auto-scale y-axis for ECG-like effect:
        ax.set_ylim(min(data_buffer) - 10, max(data_buffer) + 10)
    except Exception as e:
        print(f"Error reading data: {e}")
    return line,

# Animation setup
ani = FuncAnimation(fig, update, interval=20)  # 20ms = 50Hz update rate

# Display the plot
try:
    plt.show()
except KeyboardInterrupt:
    print("Plotting stopped.")

ser.close()
print("Serial connection closed.")
