import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
from scipy.signal import find_peaks
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.signal import butter, filtfilt
from matplotlib.widgets import Button


# Serial setup
ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(4)

time.sleep(4)
print("Ready to receive data...")

buffer_size = 80
data_buffer = [0] * buffer_size

is_running = False # Controls whether data is sent/read

fig, ax = plt.subplots()
line, = ax.plot(range(buffer_size), data_buffer, color='#555555', lw=2)
ax.set_title("Real-Time ECG Graph (Lead II)")
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude")
ax.set_xlim(0, buffer_size)
ax.set_ylim(0, 1200)
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
 txt = ax.text(x, y, label, color=color, fontsize=12, ha='center', fontweight='bold')
 txt.is_wave_label = True


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
def high_pass_filter(data, cutoff=0.5, fs=50, order=4):
 """
 Apply a high-pass filter to remove baseline wander.
 :param data: The input signal.
 :param cutoff: The cutoff frequency for the filter in Hz.
 :param fs: The sampling frequency in Hz.
 :param order: The order of the filter.
 :return: Filtered signal.
 """
 nyquist = 0.5 * fs
 normal_cutoff = cutoff / nyquist
 b, a = butter(order, normal_cutoff, btype='high', analog=False)
 return filtfilt(b, a, data)

def bandpass_filter(data, lowcut=0.5, highcut=40, fs=50, order=4):
	nyquist = 0.5 * fs
	low = lowcut / nyquist
	high = highcut / nyquist
	# Ensure critical frequencies are valid
	if low <= 0 or high >= 1 or low >= high:
		raise ValueError("Invalid bandpass filter frequencies.")
	b, a = butter(order, [low, high], btype='band')
	return filtfilt(b, a, data)








# Add buttons below the plot
ax_start = plt.axes([0.7, 0.01, 0.1, 0.06])
ax_stop = plt.axes([0.81, 0.01, 0.1, 0.06])
btn_start = Button(ax_start, 'Start')
btn_stop = Button(ax_stop, 'Stop')
btn_start.on_clicked(start_callback)
btn_stop.on_clicked(stop_callback)

ani = FuncAnimation(fig, update, interval=10, blit=False)
plt.show()

# Cleanup
ser.write(b'0\r\n')
ser.close()
print("Serial port closed.")