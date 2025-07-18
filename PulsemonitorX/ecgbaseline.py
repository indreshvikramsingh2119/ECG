import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np
import time
from scipy.signal import find_peaks, butter, lfilter
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Serial setup
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(4)
ser.write(b'1\r\n')
print("Started receiving data...")

buffer_size = 100
data_buffer = [0] * buffer_size

fig, ax = plt.subplots()
line, = ax.plot(range(buffer_size), data_buffer, color='#555555', lw=2)
ax.set_title("Real-Time ECG Graph (Lead II)")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.set_xlim(0, buffer_size)
ax.set_ylim(-400, 400)  # Fixed, symmetric y-limits for all leads
ax.set_facecolor('#f8f8f8')
ax.grid(which='major', color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(which='minor', color='lightgray', linestyle=':', linewidth=0.3, alpha=0.3)
ax.minorticks_on()
ax.xaxis.set_major_locator(plt.MultipleLocator(20))
ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
ax.yaxis.set_major_locator(plt.MultipleLocator(200))
ax.yaxis.set_minor_locator(plt.MultipleLocator(50))

bpm_label = ax.text(0.02, 0.95, "BPM: --", transform=ax.transAxes, ha='left', va='top',
                    fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

try:
    logo_img = mpimg.imread("Deckmountimg.png")
    imagebox = OffsetImage(logo_img, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.98, 0.95), xycoords='axes fraction', frameon=False, box_alignment=(1, 1))
    ax.add_artist(ab)
except FileNotFoundError:
    print("Logo image not found. Continuing without logo.")

def clear_wave_labels():
    # Remove previous wave labels
    for child in ax.texts[:]:
        if getattr(child, 'is_wave_label', False):
            child.remove()

def annotate_wave(x, y, label, color):
    # Clamp y within axis limits
    y_min, y_max = ax.get_ylim()
    y = max(y_min + 10, min(y_max - 10, y)) # Ensure y is within limits
    txt = ax.text(x, y, label, color=color, fontsize=12, ha='center', fontweight='bold')
    txt.is_wave_label = True

def calculate_bpm_and_label_waves(buffer, fs=50):
    clear_wave_labels()

    if len(buffer) < 10:
        return "--"

    # Find R peaks (R is the tallest peak)
    r_peaks, _ = find_peaks(buffer, distance=fs/2, height=np.mean(buffer) + np.std(buffer)*0.5)

    for r in r_peaks:
        # Find Q: min between r-5 to r (5 samples = ~100ms)
        q_search_start = max(r - 10, 0)
        q_search_end = r
        if q_search_end > q_search_start:
            q_point = np.argmin(buffer[q_search_start:q_search_end]) + q_search_start
        else:
            q_point = None

        # Find S: min between r to r+5
        s_search_start = r
        s_search_end = min(r + 10, len(buffer))
        if s_search_end > s_search_start:
            s_point = np.argmin(buffer[s_search_start:s_search_end]) + s_search_start
        else:
            s_point = None

        # Find P wave: max in window 100-200 ms before Q (if Q found)
        p_point = None
        if q_point:
            p_search_start = max(q_point - int(0.2 * fs), 0)
            p_search_end = max(q_point - int(0.1 * fs), 0)
            if p_search_end > p_search_start:
                p_point = np.argmax(buffer[p_search_start:p_search_end]) + p_search_start

        # Find T wave: max in window 150-350 ms after S (if S found)
        t_point = None
        if s_point:
            t_search_start = s_point + int(0.15 * fs)
            t_search_end = min(s_point + int(0.35 * fs), len(buffer))
            if t_search_end > t_search_start:
                t_point = np.argmax(buffer[t_search_start:t_search_end]) + t_search_start

        # Annotate detected waves
        if p_point and 0 <= p_point < len(buffer):
            annotate_wave(p_point, buffer[p_point] + 20, 'P', 'green')

        if q_point and 0 <= q_point < len(buffer):
            annotate_wave(q_point, buffer[q_point] - 20, 'Q', 'purple')

        annotate_wave(r, buffer[r] + 20, 'R', 'red')

        if s_point and 0 <= s_point < len(buffer):
            annotate_wave(s_point, buffer[s_point] - 20, 'S', 'purple')

        if t_point and 0 <= t_point < len(buffer):
            annotate_wave(t_point, buffer[t_point] + 20, 'T', 'orange')

    # BPM calculation from R peaks
    if len(r_peaks) > 1:
        rr_intervals = np.diff(r_peaks) / fs
        bpm = 60 / np.mean(rr_intervals)
        return int(bpm)
    else:
        return "--"
# --- Button logic ---
is_running = [False]  # Use list for mutability in closures

def start_clicked(event):
    if not is_running[0]:
        ser.write(b'1\r\n')
        is_running[0] = True
        print("Started receiving data...")

def stop_clicked(event):
    if is_running[0]:
        ser.write(b'0\r\n')
        is_running[0] = False
        print("Stopped receiving data.")

# Add Start and Stop buttons
ax_start = plt.axes([0.3, 0.05, 0.15, 0.075])
ax_stop = plt.axes([0.55, 0.05, 0.15, 0.075])
btn_start = Button(ax_start, 'Start')
btn_stop = Button(ax_stop, 'Stop')
btn_start.on_clicked(start_clicked)
btn_stop.on_clicked(stop_clicked)

def butter_highpass(cutoff, fs, order=2): # High-pass filter design
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff=0.5, fs=50, order=2):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut=0.5, highcut=40, fs=50, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def update(frame):
    if is_running[0]:
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
                bpm = calculate_bpm_and_label_waves(data_buffer)
                bpm_label.set_text(f"BPM ❤️ : {bpm}")
        except Exception as e:
            print("Error:", e)
    return line, bpm_label

ani = FuncAnimation(fig, update, interval=10, blit=False)
plt.show()

# Cleanup
ser.write(b'0\r\n')
ser.close()
print("Serial port closed.")
def update(frame):
    try:
        line_raw = ser.readline()
        line_data = line_raw.decode('utf-8', errors='replace').strip()
        print("Received:", line_data)
        if line_data.isdigit():
            value = int(line_data[-3:])  # Last 3 digits as sample
            data_buffer.append(value)
            if len(data_buffer) > buffer_size:
                data_buffer.pop(0)

            # After appending new value to data_buffer:
            if len(data_buffer) >= 10:
                # Remove DC offset (mean)
                centered = np.array(data_buffer) - np.mean(data_buffer)
                # Apply high-pass filter to remove baseline wander
                filtered = highpass_filter(centered, cutoff=0.5, fs=50, order=2)
                line.set_ydata(filtered)
            else:
                line.set_ydata(data_buffer)

            # Keep y-limits fixed for strict vertical alignment
            ax.set_ylim(-500, 500)  # Adjust as needed for your signal amplitude

            bpm = calculate_bpm_and_label_waves(filtered)
            bpm_label.set_text(f"BPM ❤️ : {bpm}")

    except Exception as e:
        print("Error:", e)

    return line, bpm_label

ani = FuncAnimation(fig, update, interval=10, blit=False)
plt.show()

# Cleanup
ser.write(b'0\r\n')
ser.close()
print("Serial port closed.")
