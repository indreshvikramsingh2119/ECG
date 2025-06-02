import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import re

# List available COM ports
ports = list(serial.tools.list_ports.comports())
if not ports:
    print("No COM ports found. Please connect your device and try again.")
    exit()

print("Available COM ports:")
for port in ports:
    print(f"  {port.device}")

# Configure your port (update if needed)
port_name = input("Enter the COM port to use (e.g., COM5): ").strip()
baud_rate = 9600

# Initialize serial connection
try:
    ser = serial.Serial(port_name, baud_rate, timeout=1)
    print(f"Serial port {port_name} opened successfully.")
except serial.SerialException as e:
    print(f"Error opening {port_name}: {e}")
    exit()

# Data buffer
ecg_data = []

# Plot setup
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2, label="ECG Wave")
ax.set_xlim(0, 100)  # Show last 100 samples
ax.set_ylim(-500, 500)  # Adjust based on expected data range
ax.set_title("Live ECG Plot")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.legend()

# Update function for animation
def update(frame):
    global ecg_data
    if ser.in_waiting > 0:
        try:
            raw_line = ser.readline().decode(errors="ignore").strip()
            print(f"Raw data received: '{raw_line}'")  # Debugging log

            # Find all numbers in the line
            numbers = re.findall(r"\d+", raw_line)
            print(f"Numbers found: {numbers}")  # Add this line
            if numbers:
                value = int(max(numbers, key=len))
                print(f"Value used for plot: {value}")  # Add this line
                ecg_data.append(value)
                if len(ecg_data) > 100:
                    ecg_data.pop(0)
                line.set_data(range(len(ecg_data)), ecg_data)
                ax.set_xlim(0, max(100, len(ecg_data)))
                ax.set_ylim(min(ecg_data) - 20, max(ecg_data) + 20)
        except Exception as e:
            print(f"Error reading or processing data: {e}")
    else:
        print("No data available in serial buffer.")
    return line,

# Animation setup
ani = FuncAnimation(fig, update, blit=True, interval=20)

try:
    plt.show()
finally:
    # Clean up
    ser.close()
    print(f"Serial port {port_name} closed.")

import serial

ser = serial.Serial('COM5', 9600, timeout=2)
while True:
    print(ser.readline().decode(errors="ignore").strip())
