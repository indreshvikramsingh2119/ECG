import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Mock data generator: simulate ECG-like signal
def mock_ecg_generator():
    t = 0
    while True:
        try:
            # Generate synthetic ECG-like waveform (sin + noise)
            ecg_value = 100 * np.sin(2 * np.pi * 1 * t) + 20 * np.random.randn()
            t += 0.02  # Simulate ~50Hz sampling rate (20ms interval)
            yield int(ecg_value)
        except Exception as e:
            print(f"Error in mock data generator: {e}")
            yield 0

# Data buffer
ecg_data = []

# Plot setup
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2, label="Mock ECG Wave")
ax.set_xlim(0, 100)  # Keep the last 100 samples visible
ax.set_ylim(-200, 200)  # Adjust based on the expected range of ECG data
ax.set_title("Live ECG Plot (Mock Data)")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.legend()

# Create generator instance
mock_data_gen = mock_ecg_generator()

# Update function for animation
def update(frame):
    global ecg_data
    try:
        # Get next mock data point
        value = next(mock_data_gen)
        ecg_data.append(value)
        if len(ecg_data) > 100:  # Keep last 100 samples
            ecg_data.pop(0)

        # Update plot data
        line.set_data(range(len(ecg_data)), ecg_data)
        ax.set_xlim(0, max(100, len(ecg_data)))
        ax.set_ylim(min(ecg_data) - 20, max(ecg_data) + 20)
    except Exception as e:
        print(f"Error during update: {e}")
    return line,

# Animation setup
ani = FuncAnimation(fig, update, blit=True, interval=20, save_count=50)

plt.show()
