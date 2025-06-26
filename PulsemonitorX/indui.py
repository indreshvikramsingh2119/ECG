from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
    QMessageBox, QFrame
)
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QRadioButton


app = QApplication(sys.argv)

root = QWidget()
root.setWindowTitle("ECG Setup")
root.setGeometry(100, 100, 700, 600)
root.setStyleSheet("background-color: white;")

# --------- Global Containers ---------
mode = {"layout": "alpha", "case": "lower"}
target_entry = None
temp_entry = None

# --------- Main Frame Setup ---------
main_layout = QHBoxLayout(root)

menu_frame = QFrame()
menu_frame.setStyleSheet("background-color: white;")
menu_frame.setFixedWidth(150)
main_layout.addWidget(menu_frame)

menu_layout = QVBoxLayout(menu_frame)
menu_frame.setLayout(menu_layout)  # optional if passed directly above

content_frame = QFrame()
content_frame.setStyleSheet("background-color: white;")
main_layout.addWidget(content_frame)

content_layout = QVBoxLayout()                  # ✅ Added this line
content_frame.setLayout(content_layout)         # ✅ Added this line

# --------- Virtual Keyboard ---------
keyboard_frame = QFrame(content_frame)
keyboard_frame.setStyleSheet("background-color: lightgray;")
keyboard_layout = QVBoxLayout(keyboard_frame)

temp_entry = QLineEdit()
temp_entry.setStyleSheet("font: 14pt Arial;")
temp_entry.setFixedWidth(500)
keyboard_layout.addWidget(temp_entry)

key_frame = QFrame()
key_frame.setStyleSheet("background-color: lightgray;")
keyboard_layout.addWidget(key_frame)


def save_keyboard_input():
    if target_entry:
        target_entry.setText(temp_entry.text())
        hide_keyboard()


def hide_keyboard():
    keyboard_frame.hide()



# --------- SAVE ECG Page ---------

def show_save_ecg():
    clear_content()

    container = QFrame()
    container.setStyleSheet("background-color: white; border: 1px solid black;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(30, 30, 30, 30)

    title = QLabel("Save ECG Details")
    title.setStyleSheet("font: bold 14pt Arial;")
    container_layout.addWidget(title)

    form_frame = QFrame()
    form_layout = QGridLayout(form_frame)
    labels = ["Organisation", "Doctor", "Patient Name"]
    entries = {}

    for i, label in enumerate(labels):
        lbl = QLabel(label)
        lbl.setStyleSheet("font: bold 12pt Arial;")
        form_layout.addWidget(lbl, i, 0)

        entry = QLineEdit()
        entry.setStyleSheet("font: 12pt Arial;")
        entry.setFixedWidth(250)
        form_layout.addWidget(entry, i, 1)
        entries[label] = entry

    # Age
    lbl_age = QLabel("Age")
    lbl_age.setStyleSheet("font: bold 12pt Arial;")
    form_layout.addWidget(lbl_age, 3, 0)

    age_entry = QLineEdit()
    age_entry.setStyleSheet("font: 12pt Arial;")
    age_entry.setFixedWidth(100)
    form_layout.addWidget(age_entry, 3, 1)
    entries["Age"] = age_entry

    # Gender
    lbl_gender = QLabel("Gender")
    lbl_gender.setStyleSheet("font: bold 12pt Arial;")
    form_layout.addWidget(lbl_gender, 4, 0)

    gender_menu = QComboBox()
    gender_menu.addItems(["Select", "Male", "Female", "Other"])
    gender_menu.setStyleSheet("font: 12pt Arial; background-color: skyblue;")
    gender_menu.setFixedWidth(120)
    form_layout.addWidget(gender_menu, 4, 1)

    container_layout.addWidget(form_frame)

    # Submit logic
    def submit_details():
        values = {label: entries[label].text().strip() for label in labels + ["Age"]}
        values["Gender"] = gender_menu.currentText()

        if any(v == "" for v in values.values()) or values["Gender"] == "Select":
            QMessageBox.warning(root, "Missing Data", "Please fill all the fields and select gender.")
            return

        try:
            with open("ecg_data.txt", "a") as file:
                file.write(f"{values['Organisation']}, {values['Doctor']}, {values['Patient Name']}, {values['Age']}, {values['Gender']}\n")
            QMessageBox.information(root, "Saved", "Details saved to ecg_data.txt successfully.")
        except Exception as e:
            QMessageBox.critical(root, "Error", f"Failed to save: {e}")

    # Buttons inside button frame
    button_frame = QFrame()
    button_layout = QHBoxLayout(button_frame)

    save_btn = QPushButton("Save")
    save_btn.setStyleSheet("font: 12pt Arial; background-color: green; color: white;")
    save_btn.setFixedWidth(150)
    save_btn.clicked.connect(submit_details)
    button_layout.addWidget(save_btn)

    exit_btn = QPushButton("Exit")
    exit_btn.setStyleSheet("font: 12pt Arial; background-color: red; color: white;")
    exit_btn.setFixedWidth(150)
    exit_btn.clicked.connect(lambda: None)  # Placeholder for show_main_menu
    button_layout.addWidget(exit_btn)

    container_layout.addWidget(button_frame)
    content_frame.setLayout(QVBoxLayout())
    content_frame.layout().addWidget(container)

    keyboard_frame.hide()





def open_ecg_window():
    clear_content()

    container = QFrame()
    container.setStyleSheet("background-color: white; border: 1px solid gray;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("Open ECG")
    title.setStyleSheet("font: bold 16pt Arial; background-color: white;")
    title.setAlignment(Qt.AlignCenter)
    container_layout.addWidget(title)

    # ---------------------- Top 4 Equal Boxes ----------------------
    top_info_frame = QFrame()
    top_info_frame.setStyleSheet("background-color: white;")
    container_layout.addWidget(top_info_frame)

    box_frame = QFrame()
    box_frame.setStyleSheet("background-color: white; border: 1px solid black;")
    box_layout = QHBoxLayout(box_frame)
    box_layout.setContentsMargins(0, 0, 0, 0)
    top_info_frame.setLayout(QVBoxLayout())
    top_info_frame.layout().addWidget(box_frame)

    def create_cell(text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font: 9pt Arial; background-color: white;")
        lbl.setFixedWidth(130)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    box_layout.addWidget(create_cell("Capacity"))
    box_layout.addWidget(vertical_divider())

    box_layout.addWidget(create_cell("30000 case"))
    box_layout.addWidget(vertical_divider())

    box_layout.addWidget(create_cell("Used:"))
    box_layout.addWidget(vertical_divider())

    box_layout.addWidget(create_cell("0 case"))

    # ---------------------- Header Row ----------------------------
    header_frame = QFrame()
    header_frame.setStyleSheet("background-color: white; border: 1px solid black;")
    header_layout = QHBoxLayout(header_frame)
    header_layout.setContentsMargins(5, 5, 5, 5)

    def create_header_cell(text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font: bold 10pt Arial; background-color: white;")
        lbl.setFixedWidth(150)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    header_layout.addWidget(create_header_cell("ID"))
    header_layout.addWidget(vertical_divider(1))

    header_layout.addWidget(create_header_cell("Gender"))
    header_layout.addWidget(vertical_divider(1))

    header_layout.addWidget(create_header_cell("Age"))
    container_layout.addWidget(header_frame)

    # ---------------------- Data Rows ----------------------------
    rows_frame = QFrame()
    rows_frame.setStyleSheet("background-color: white;")
    rows_layout = QVBoxLayout(rows_frame)

    def create_row_cell(text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font: 10pt Arial; background-color: white;")
        lbl.setFixedWidth(150)
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    for _ in range(10):
        row_outer = QFrame()
        row_outer.setStyleSheet("background-color: white; border: 1px solid gray;")
        row_layout = QHBoxLayout(row_outer)
        row_layout.setContentsMargins(5, 5, 5, 5)

        row_layout.addWidget(create_row_cell("-----------"))
        row_layout.addWidget(vertical_divider(1))

        row_layout.addWidget(create_row_cell("-----------"))
        row_layout.addWidget(vertical_divider(1))

        row_layout.addWidget(create_row_cell("-----------"))
        rows_layout.addWidget(row_outer)

    container_layout.addWidget(rows_frame)

    # ---------------------- Bottom Buttons ------------------------
    button_frame = QFrame()
    button_frame.setStyleSheet("background-color: white;")
    button_layout = QGridLayout(button_frame)
    container_layout.addWidget(button_frame)

    active_button = {"value": ""}

    buttons_dict = {}

    def update_button_styles():
        for name, btn in buttons_dict.items():
            if active_button["value"] == name:
                btn.setStyleSheet("background-color: skyblue; font: 10pt Arial;")
            else:
                btn.setStyleSheet("")

    button_config = [
        ("Up", 0, 0), ("Del This", 0, 1), ("Rec", 0, 2),
        ("Down", 1, 0), ("Del All", 1, 1), ("Exit", 1, 2)
    ]

    for text, r, c in button_config:
        def make_handler(name=text):
            def handler():
                if name == "Exit":
                    clear_content()
                    show_main_menu()
                else:
                    active_button["value"] = name
                    update_button_styles()
            return handler

        btn = QPushButton(text)
        btn.setFixedWidth(150)
        btn.setFixedHeight(30)
        btn.setStyleSheet("font: 10pt Arial;")
        btn.clicked.connect(make_handler())
        button_layout.addWidget(btn, r, c)
        buttons_dict[text] = btn

    content_frame.setLayout(QVBoxLayout())
    content_frame.layout().addWidget(container)

# -------- Vertical divider helper (like Tkinter tk.Frame) --------
def vertical_divider(width=3):
    frame = QFrame()
    frame.setFixedWidth(width)
    frame.setStyleSheet("background-color: black;")
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame








def show_working_mode():
    layout = content_frame.layout()
    if layout:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    container = QFrame()
    container.setStyleSheet("background-color: white; border: 1px solid black;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(30, 30, 30, 30)

    title = QLabel("Working Mode")
    title.setStyleSheet("font: bold 14pt Arial; background-color: white;")
    container_layout.addWidget(title)

    def add_section(title, options, variable):
        group_box = QGroupBox(title)
        group_box.setStyleSheet("font: bold 12pt Arial; background-color: white;")
        hbox = QHBoxLayout(group_box)
        for text, val in options:
            btn = QRadioButton(text)
            btn.setStyleSheet("font: 11pt Arial; background-color: white;")
            btn.setChecked(variable['value'] == val)
            btn.toggled.connect(lambda checked, v=val: variable.update({'value': v}) if checked else None)
            hbox.addWidget(btn)
        container_layout.addWidget(group_box)

    # Variables (dict-based because PyQt doesn't have tk.StringVar)
    wave_speed = {"value": "50"}
    wave_gain = {"value": "10"}
    lead_seq = {"value": "Standard"}
    sampling = {"value": "Simultaneous"}
    demo_func = {"value": "Off"}
    storage = {"value": "SD"}

    add_section("Wave Speed", [("12.5mm/s", "12.5"), ("25.0mm/s", "25"), ("50.0mm/s", "50")], wave_speed)
    add_section("Wave Gain", [("2.5mm/mV", "2.5"), ("5mm/mV", "5"), ("10mm/mV", "10"), ("20mm/mV", "20")], wave_gain)
    add_section("Lead Sequence", [("Standard", "Standard"), ("Cabrera", "Cabrera")], lead_seq)
    add_section("Sampling Mode", [("Simultaneous", "Simultaneous"), ("Sequence", "Sequence")], sampling)
    add_section("Demo Function", [("Off", "Off"), ("On", "On")], demo_func)
    add_section("Priority Storage", [("U Disk", "U"), ("SD Card", "SD")], storage)

    # Buttons
    btn_frame = QFrame()
    btn_layout = QHBoxLayout(btn_frame)

    ok_btn = QPushButton("OK")
    ok_btn.setFixedWidth(150)
    ok_btn.setStyleSheet("font: 12pt Arial;")
    ok_btn.clicked.connect(lambda: QMessageBox.information(root, "Saved", "Working mode settings saved"))
    btn_layout.addWidget(ok_btn)

    exit_btn = QPushButton("Exit")
    exit_btn.setFixedWidth(150)
    exit_btn.setStyleSheet("font: 12pt Arial; background-color: red; color: white;")
    exit_btn.clicked.connect(show_main_menu)
    btn_layout.addWidget(exit_btn)

    container_layout.addWidget(btn_frame)

    if content_frame.layout() is None:
        content_frame.setLayout(QVBoxLayout())
    content_frame.layout().addWidget(container)

    keyboard_frame.hide()






def open_keypad(entry_widget):
    global keypad_frame
    try:
        keypad_frame.deleteLater()
    except (NameError, RuntimeError):
        pass

    keypad_frame = QFrame(entry_widget.parent())
    keypad_frame.setStyleSheet("background-color: lightgray; border: 1px solid black;")
    keypad_layout = QGridLayout(keypad_frame)
    keypad_layout.setSpacing(4)

    input_var = QLineEdit()
    input_var.setText(entry_widget.text())
    input_var.setReadOnly(True)
    input_var.setStyleSheet("font: 12pt Arial; background-color: white;")
    input_var.setAlignment(Qt.AlignRight)
    input_var.setFixedWidth(100)
    keypad_layout.addWidget(input_var, 0, 0, 1, 3)

    def update_display(val):
        input_var.setText(input_var.text() + val)

    def backspace():
        input_var.setText(input_var.text()[:-1])

    def clear():
        input_var.setText("")

    def apply_value():
        try:
            val = int(input_var.text())
            if 3 <= val <= 20:
                entry_widget.setText(str(val))
                keypad_frame.deleteLater()
            else:
                QMessageBox.warning(root, "Invalid", "Please enter a value between 3 and 20.")
        except ValueError:
            QMessageBox.warning(root, "Invalid", "Please enter a numeric value.")

    # Digit buttons
    positions = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        ('0', 4, 1)
    ]
    for (text, row, col) in positions:
        btn = QPushButton(text)
        btn.setFixedWidth(40)
        btn.setStyleSheet("font: 10pt Arial;")
        btn.clicked.connect(lambda _, t=text: update_display(t))
        keypad_layout.addWidget(btn, row, col)

    # ← Back
    btn_back = QPushButton("←")
    btn_back.setFixedWidth(40)
    btn_back.setStyleSheet("font: 10pt Arial;")
    btn_back.clicked.connect(backspace)
    keypad_layout.addWidget(btn_back, 4, 0)

    # Clear
    btn_clear = QPushButton("C")
    btn_clear.setFixedWidth(40)
    btn_clear.setStyleSheet("font: 10pt Arial;")
    btn_clear.clicked.connect(clear)
    keypad_layout.addWidget(btn_clear, 4, 2)

    # OK
    btn_ok = QPushButton("OK")
    btn_ok.setStyleSheet("font: bold 10pt Arial; background-color: green; color: white;")
    btn_ok.setFixedWidth(120)
    btn_ok.clicked.connect(apply_value)
    keypad_layout.addWidget(btn_ok, 5, 0, 1, 3)

    parent_layout = entry_widget.parent().layout()
    if parent_layout:
        parent_layout.addWidget(keypad_frame)





def show_printer_setup():
    layout = content_frame.layout()
    if layout:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    container = QFrame()
    container.setStyleSheet("background-color: white; border: 1px solid black;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(30, 30, 30, 30)

    title = QLabel("Rec Setup")
    title.setStyleSheet("font: bold 12pt Arial; background-color: white;")
    container_layout.addWidget(title)

    # Variables (dicts to mimic StringVar)
    auto_format = {"value": "3x4"}
    analysis_result = {"value": "on"}
    avg_wave = {"value": "on"}
    selected_rhythm_lead = {"value": "off"}
    sensitivity = {"value": "High"}

    def add_radiobutton_group(title, options, variable):
        group = QGroupBox(title)
        group.setStyleSheet("font: bold 12pt Arial; background-color: white;")
        layout = QHBoxLayout(group)
        for opt in options:
            btn = QRadioButton(opt)
            btn.setStyleSheet("font: 10pt Arial; background-color: white;")
            btn.setChecked(variable["value"] == opt)
            btn.toggled.connect(lambda checked, val=opt: variable.update({"value": val}) if checked else None)
            layout.addWidget(btn)
        container_layout.addWidget(group)

    add_radiobutton_group("Auto Rec Format", ["3x4", "3x2+2x3"], auto_format)
    add_radiobutton_group("Analysis Result", ["on", "off"], analysis_result)
    add_radiobutton_group("Avg Wave", ["on", "off"], avg_wave)

    # Rhythm Lead Group
    rhythm_group = QGroupBox("Rhythm Lead")
    rhythm_group.setStyleSheet("font: bold 12pt Arial; background-color: white;")
    rhythm_layout = QVBoxLayout(rhythm_group)
    row1 = QHBoxLayout()
    row2 = QHBoxLayout()
    lead_options = ["off", "I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    for i, lead in enumerate(lead_options):
        btn = QRadioButton(lead)
        btn.setStyleSheet("font: 10pt Arial; background-color: white;")
        btn.setChecked(selected_rhythm_lead["value"] == lead)
        btn.toggled.connect(lambda checked, val=lead: selected_rhythm_lead.update({"value": val}) if checked else None)
        if i < 7:
            row1.addWidget(btn)
        else:
            row2.addWidget(btn)
    rhythm_layout.addLayout(row1)
    rhythm_layout.addLayout(row2)
    container_layout.addWidget(rhythm_group)

    # Auto Time
    time_group = QGroupBox("Automatic Time (sec/Lead)")
    time_group.setStyleSheet("font: bold 12pt Arial; background-color: white;")
    time_layout = QVBoxLayout(time_group)

    time_entry = QLineEdit()
    time_entry.setReadOnly(True)
    time_entry.setText("3")
    time_entry.setStyleSheet("font: 10pt Arial; background-color: white;")
    time_entry.mousePressEvent = lambda event: open_keypad(time_entry)
    time_layout.addWidget(time_entry)
    container_layout.addWidget(time_group)

    # Sensitivity Group
    sens_group = QGroupBox("Analysis Sensitivity")
    sens_group.setStyleSheet("font: bold 12pt Arial; background-color: white;")
    sens_layout = QHBoxLayout(sens_group)
    for val in ["Low", "Med", "High"]:
        btn = QRadioButton(val)
        btn.setStyleSheet("font: 10pt Arial; background-color: white;")
        btn.setChecked(sensitivity["value"] == val)
        btn.toggled.connect(lambda checked, v=val: sensitivity.update({"value": v}) if checked else None)
        sens_layout.addWidget(btn)
    container_layout.addWidget(sens_group)

    # Buttons
    btn_frame = QFrame()
    btn_layout = QHBoxLayout(btn_frame)

    ok_btn = QPushButton("OK")
    ok_btn.setFixedWidth(150)
    ok_btn.setStyleSheet("font: 12pt Arial;")
    ok_btn.clicked.connect(lambda: QMessageBox.information(root, "Saved", "Printer setup saved"))
    btn_layout.addWidget(ok_btn)

    exit_btn = QPushButton("Exit")
    exit_btn.setFixedWidth(150)
    exit_btn.setStyleSheet("font: 12pt Arial; background-color: red; color: white;")
    exit_btn.clicked.connect(show_main_menu)
    btn_layout.addWidget(exit_btn)

    container_layout.addWidget(btn_frame)

    if content_frame.layout() is None:
        content_frame.setLayout(QVBoxLayout())
    content_frame.layout().addWidget(container)

def clear_content():
    layout = content_frame.layout()
    if layout:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

def show_main_menu():
    clear_content()
    menu_label = QLabel("Main Menu")
    menu_label.setStyleSheet("font: bold 18pt Arial; color: #00a;")
    menu_label.setAlignment(Qt.AlignCenter)
    content_frame.layout().addWidget(menu_label)

# --- Add menu buttons ---
menu_buttons = [
    ("SAVE ECG", show_save_ecg),
    ("OPEN ECG", open_ecg_window),
    ("WORKING MODE", show_working_mode),
    ("PRINTER SETUP", show_printer_setup),
    # Add more as needed...
    ("Exit", lambda: app.quit())
]

for text, handler in menu_buttons:
    btn = QPushButton(text)
    btn.setStyleSheet("font: 12pt Arial; background-color: #eee;")
    btn.setFixedHeight(40)
    btn.clicked.connect(handler)
    menu_layout.addWidget(btn)

menu_layout.addStretch(1)

# --- At the end of your file ---
if __name__ == "__main__":
    show_main_menu()
    root.show()
    sys.exit(app.exec_())