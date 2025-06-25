from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from ecg.ui.live_lead_window import LiveLeadWindow

class ECGTestPage(QWidget):
    LEAD_COLORS = {
        "I": "#00ff99", "II": "#ff0055", "III": "#0099ff",
        "aVR": "#ff9900", "aVL": "#cc00ff", "aVF": "#00ccff",
        "V1": "#ffcc00", "V2": "#00ffcc", "V3": "#ff6600",
        "V4": "#6600ff", "V5": "#00b894", "V6": "#ff0066"
    }
    def __init__(self, test_name, stacked_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(f"ECG Test: {test_name}")
        layout.addWidget(label)
        # ... rest of your plotting and logic ...

    def expand_lead(self, idx):
        lead = self.leads[idx]
        def get_lead_data():
            return self.data[lead]
        color = self.LEAD_COLORS.get(lead, "#00ff99")
        win = LiveLeadWindow(lead, get_lead_data, buffer_size=self.buffer_size, color=color)
        win.show()
        if not hasattr(self, "_live_windows"):
            self._live_windows = []
        self._live_windows.append(win)