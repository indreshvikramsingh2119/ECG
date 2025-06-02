import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
port = "COM5"  # Replace with the actual port of your device
baud_rate = 9600  # Adjust according to your device's specifications
buffer_size = 100  # Number of data points to display on the graph

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
data_buffer = np.full(buffer_size, np.nan)  # Initialize with NaN for plotting gaps

# Initialize the plot
fig, ax = plt.subplots()
line, = ax.plot([], [], label="ECG Wave", lw=2)
ax.set_title("Real-Time ECG Plot")
ax.set_xlabel("Time")
ax.set_ylabel("Amplitude")
ax.set_ylim(0, 1024)  # Adjust based on your device's data range
ax.legend()

# Function to handle non-numeric data
def handle_non_numeric(data_buffer):
    # Replace NaN with the average of the last valid values
    valid_values = data_buffer[~np.isnan(data_buffer)]
    if valid_values.size > 0:
        return np.mean(valid_values)  # Replace with the mean of valid values
    else:
        return 0  # Default to zero if no valid data is available

# Function to update the graph
def update(frame):
    global data_buffer
    try:
        # Read data from the serial port
        raw_bytes = ser.readline()
        line_data = raw_bytes.decode('utf-8', errors='replace').strip()

        # Display raw bytes and decoded data
        print(f"Raw bytes: {raw_bytes}")
        print(f"Decoded data: '{line_data}'")

        if line_data.isnumeric():
            value = int(line_data)
        else:
            print(f"Non-numeric data received: '{line_data}'")
            value = handle_non_numeric(data_buffer)  # Process non-numeric data

        # Update the buffer
        data_buffer = np.roll(data_buffer, -1)
        data_buffer[-1] = value

    except Exception as e:
        print(f"Error reading data: {e}")

    # Update the plot
    line.set_data(np.arange(len(data_buffer)), data_buffer)
    ax.set_xlim(0, len(data_buffer))
    if not np.all(np.isnan(data_buffer)):  # Adjust y-axis only if there's valid data
        ax.set_ylim(np.nanmin(data_buffer) - 10, np.nanmax(data_buffer) + 10)
    return line,

# Animation setup
ani = FuncAnimation(fig, update, interval=500)

# Display the plot
try:
    plt.show()
except KeyboardInterrupt:
    print("Plotting stopped.")

# Cleanup
ser.close()
print("Serial connection closed.")
