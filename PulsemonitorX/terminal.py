import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
from scipy.signal import find_peaks
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.interpolate import make_interp_spline

# Serial setup: COM5 port pe 9600 baud rate se connect kar rahe hain, 4 second device start hone ka wait, fir '1' bhej ke data receive start karenge
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(4)  # Waiting for the device to start
ser.write(b'1\r\n')
print("Started receiving data...")

# Plot setup
buffer_size = 80
data_buffer = [0] * buffer_size
fig, ax = plt.subplots()
line, = ax.plot(range(buffer_size), data_buffer, color='#888888', lw=2)  # Light gray and thin line
ax.set_title("Real-Time ECG Graph(Lead II)")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.set_xlim(0, buffer_size)
ax.set_ylim(0, 1200)  # Adjust as per your data range

# ECG-style grid
ax.set_facecolor('#f8f8f8')
ax.grid(which='major', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(which='minor', color='lightgray', linestyle=':', linewidth=0.3, alpha=0.3)
ax.minorticks_on()
ax.xaxis.set_major_locator(plt.MultipleLocator(20))
ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
ax.yaxis.set_major_locator(plt.MultipleLocator(200))
ax.yaxis.set_minor_locator(plt.MultipleLocator(50))

bpm_label = ax.text(0.02, 0.95, "BPM: --", transform=ax.transAxes, ha='left', va='top', fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Add this line for your custom label in the upper right
# ax.text(0.98, 0.95, "Deckmount⚡electronics", transform=ax.transAxes, ha='right', va='top', fontsize=12, color='blue', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Load and add logo image to upper right
logo_img = mpimg.imread("Deckmountimg.png")  # Replace with your image filename
imagebox = OffsetImage(logo_img, zoom=0.5)  # Adjust zoom as needed
ab = AnnotationBbox(imagebox, (0.98, 0.95), xycoords='axes fraction',
                    frameon=False, box_alignment=(1,1))
ax.add_artist(ab)

def calculate_bpm(buffer, fs=50):
    # Remove previous P labels
    [child.remove() for child in ax.texts if getattr(child, 'is_p_label', False)]

    if len(buffer) < 10:
        return "--"
    # Find R-peaks
    peaks, _ = find_peaks(buffer, distance=fs/2, height=np.mean(buffer) + np.std(buffer))
    # Plot only P waves (before each R)
    for r in peaks:
        search_start = max(0, r - int(0.2 * fs))  # 200 ms before R
        p_region = buffer[search_start:r]
        if len(p_region) > 0:
            p_peak = np.argmax(p_region) + search_start
            # Annotate "P" at the P wave
            label = ax.text(p_peak, buffer[p_peak]+20, "P", color="green", fontsize=12, ha='center', fontweight='bold')
            label.is_p_label = True  # Mark for removal next time
    # BPM calculation
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / fs
        bpm = 60 / np.mean(rr_intervals)
        return int(bpm)
    else:
        return "--"

def update(frame):
    try:
        line_raw = ser.readline()
        line_data = line_raw.decode('utf-8', errors='replace').strip()
        print("Received:", line_data)
        if line_data.isdigit():
            value = int(line_data[-3:])
            data_buffer.append(value)
            if len(data_buffer) > buffer_size:
                data_buffer.pop(0)
            line.set_ydata(data_buffer)
            ax.set_ylim(min(data_buffer) - 10, max(data_buffer) + 10)
            bpm = calculate_bpm(data_buffer)
            bpm_label.set_text(f"BPM ❤️ : {bpm}")
    except Exception as e:
        print("Error:", e)
    return line, bpm_label




ani = FuncAnimation(fig, update, interval=50, blit=False)
plt.show()

# On close, send '0' to stop and close port
ser.write(b'0\r\n')
ser.close()
print("Serial port closed.") 
