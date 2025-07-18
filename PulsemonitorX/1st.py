
import tkinter as tk
from tkinter import messagebox


root = tk.Tk()
root.title("ECG Setup")
root.geometry("700x600")
root.configure(bg="white")

# --------- Global Containers ---------
mode = {"layout": "alpha", "case": "lower"}
target_entry = None
temp_entry = None

# --------- Main Frame Setup ---------
main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill="both", expand=True)

menu_frame = tk.Frame(main_frame, bg="white")
menu_frame.pack(side="left", fill="y", padx=10, pady=10)

content_frame = tk.Frame(main_frame, bg="white")
content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# --------- Virtual Keyboard ---------
keyboard_frame = tk.Frame(content_frame, bg="lightgray")
temp_entry = tk.Entry(keyboard_frame, font=("Arial", 14), width=60)
temp_entry.pack(pady=5)
key_frame = tk.Frame(keyboard_frame, bg="lightgray")
key_frame.pack(pady=5)



def save_keyboard_input():
    target_entry.delete(0, tk.END)
    target_entry.insert(0, temp_entry.get())
    hide_keyboard()

def hide_keyboard():
    keyboard_frame.pack_forget()

# --------- SAVE ECG Page ---------

def show_save_ecg():
    for widget in content_frame.winfo_children():
        widget.destroy()

    #  Outer Container Frame with border
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(container, text="Save ECG Details", font=("Arial", 14, "bold"), bg="white").pack(pady=(10, 20))

    #  Inner Form Frame
    form_frame = tk.Frame(container, bg="white")
    form_frame.pack(pady=10)

    labels = ["Organisation", "Doctor", "Patient Name"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label, font=("Arial", 12,"bold"), bg="white").grid(row=i, column=0, padx=10, pady=10, sticky="e")
        entry = tk.Entry(form_frame, width=30, font=("Arial", 12))
        entry.grid(row=i, column=1, padx=10, pady=10)
        entries[label] = entry

    # Age
    tk.Label(form_frame, text="Age", font=("Arial", 12,"bold"), bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="e")
    age_entry = tk.Entry(form_frame, width=10, font=("Arial", 12))
    age_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
    entries["Age"] = age_entry

    # Gender
    tk.Label(form_frame, text="Gender", font=("Arial", 12,"bold"), bg="white").grid(row=4, column=0, padx=10, pady=10, sticky="e")
    gender_var = tk.StringVar(value="Select")
    gender_menu = tk.OptionMenu(form_frame, gender_var, "Male", "Female", "Other")
    gender_menu.config(font=("Arial", 12), width=10,bg="skyblue")
    gender_menu.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Submit logic
    def submit_details():
        values = {label: entries[label].get().strip() for label in labels + ["Age"]}
        values["Gender"] = gender_var.get()

        if any(v == "" for v in values.values()) or values["Gender"] == "Select":
            messagebox.showwarning("Missing Data", "Please fill all the fields and select gender.")
            return

        try:
            with open("ecg_data.txt", "a") as file:
                file.write(f"{values['Organisation']}, {values['Doctor']}, {values['Patient Name']}, {values['Age']}, {values['Gender']}\n")
            messagebox.showinfo("Saved", "Details saved to ecg_data.txt successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    # Buttons inside button frame
    button_frame = tk.Frame(container, bg="white")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Save", font=("Arial", 12), width=15, bg="green", fg="white", command=submit_details).pack(side="left", padx=10,)
    tk.Button(button_frame, text="Exit", font=("Arial", 12), width=15, bg="red", fg="white", command=show_main_menu).pack(side="left", padx=10,)

    keyboard_frame.pack_forget()






def open_ecg_window():
    clear_content()

    # Outer container box
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
    container.pack(padx=20, pady=20, fill='both', expand=True)

    # Title
    tk.Label(container, text="Open ECG", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # ---------------------- Top 4 Equal Boxes ----------------------
    top_info_frame = tk.Frame(container, bg="white")
    top_info_frame.pack(pady=5)

# Joint box with 4 fields inside
        # Joint outer box frame
    box_frame = tk.Frame(top_info_frame, bg="white", bd=1, relief="solid", padx=0, pady=0)
    box_frame.pack()

    # Labels with vertical dividers
    def create_cell(text):
        return tk.Label(box_frame, text=text, font=("Arial", 9), bg="white", width=17, anchor="center")
    create_cell("Capacity").pack(side="left", padx=0, pady=5)
    tk.Frame(box_frame, bg="black", width=3, height=30).pack(side="left", fill="y", padx=0)

    create_cell("30000 case").pack(side="left", padx=0, pady=5)
    tk.Frame(box_frame, bg="black", width=3, height=30).pack(side="left", fill="y", padx=0)

    create_cell("Used:").pack(side="left", padx=0, pady=5)
    tk.Frame(box_frame, bg="black", width=3, height=30).pack(side="left", fill="y", padx=0)

    create_cell("0 case").pack(side="left", padx=0, pady=5)
  
        # --------------------------------------------------------------

    # ---------------------- Header Row ----------------------------
    # Outer joint frame for headers
    header_frame = tk.Frame(container, bg="white", bd=1, relief="solid")
    header_frame.pack(pady=10)

    def create_header_cell(text):
        return tk.Label(header_frame, text=text, font=("Arial", 10, "bold"), width=20, bg="white", anchor="center")

    create_header_cell("ID").pack(side='left', pady=5)
    tk.Frame(header_frame, bg="black", width=1, height=30).pack(side="left", fill="y")

    create_header_cell("Gender").pack(side='left', pady=5)
    tk.Frame(header_frame, bg="black", width=1, height=30).pack(side="left", fill="y")

    create_header_cell("Age").pack(side='left', pady=5)

    # ---------------------- Data Rows ----------------------------
    rows_frame = tk.Frame(container, bg="white")
    rows_frame.pack()

    row_widgets = []
    for _ in range(10):
        # Outer frame for the whole row with border
        row_outer = tk.Frame(rows_frame, bg="white", bd=1, relief="solid")
        row_outer.pack(fill='x', padx=20, pady=1)

        # 3 equal parts inside the row
        def create_cell(text):
            return tk.Label(row_outer, text=text, width=20, font=("Arial", 10), bg="white", anchor="center")

        create_cell("-----------").pack(side="left", pady=5)
        tk.Frame(row_outer, bg="black", width=1, height=30).pack(side="left", fill="y")

        create_cell("-----------").pack(side="left", pady=5)
        tk.Frame(row_outer, bg="black", width=1, height=30).pack(side="left", fill="y")

        create_cell("-----------").pack(side="left", pady=5)

        row_widgets.append(row_outer)

    # --------------------------------------------------------------

    # ---------------------- Bottom Buttons ------------------------
        button_frame = tk.Frame(container, bg="white")
    button_frame.pack(pady=20)

    active_button = tk.StringVar(value="")  # Track which button is active

    # Button color update logic
    def update_button_styles():
        for btn_name, btn_obj in buttons_dict.items():
            if active_button.get() == btn_name:
                btn_obj.config(bg="skyblue")
            else:
                btn_obj.config(bg="SystemButtonFace")  # Default system color

    buttons_dict = {}

    # Button text and grid positions
    button_config = [
        ("Up", 0, 0), ("Del This", 0, 1), ("Rec", 0, 2),
        ("Down", 1, 0), ("Del All", 1, 1), ("Exit", 1, 2)
    ]

    for text, r, c in button_config:
        def on_click(name=text):
            if name == "Exit":
                clear_content() 
                show_main_menu()
            else:
                active_button.set(name)
                update_button_styles()

        btn = tk.Button(button_frame, text=text, font=("Arial", 10), width=19, height=1, command=on_click)
        btn.grid(row=r, column=c, padx=5, pady=0.5)
        buttons_dict[text] = btn




    



def show_working_mode():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # --- Outer Container Frame (Box) ---
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(container, text="Working Mode", font=("Arial", 14, "bold"), bg="white").pack(pady=(10, 20))

    def add_section(title, options, variable):
        frame = tk.LabelFrame(container, text=title, font=("Arial", 12, "bold"), bg="white", padx=10, pady=5)
        frame.pack(fill="x", padx=20, pady=5)
        for i, (text, val) in enumerate(options):
            tk.Radiobutton(frame, text=text, variable=variable, value=val, font=("Arial", 11), bg="white",).pack(side="left", padx=10)

    # Variables
    wave_speed = tk.StringVar(value="50")
    wave_gain = tk.StringVar(value="10")
    lead_seq = tk.StringVar(value="Standard")
    sampling = tk.StringVar(value="Simultaneous")
    demo_func = tk.StringVar(value="Off")
    storage = tk.StringVar(value="SD")

    # Add Sections
    add_section("Wave Speed", [("12.5mm/s", "12.5"), ("25.0mm/s", "25"), ("50.0mm/s", "50")], wave_speed)
    add_section("Wave Gain", [("2.5mm/mV", "2.5"), ("5mm/mV", "5"), ("10mm/mV", "10"), ("20mm/mV", "20")], wave_gain)
    add_section("Lead Sequence", [("Standard", "Standard"), ("Cabrera", "Cabrera")], lead_seq)
    add_section("Sampling Mode", [("Simultaneous", "Simultaneous"), ("Sequence", "Sequence")], sampling)
    add_section("Demo Function", [("Off", "Off"), ("On", "On")], demo_func)
    add_section("Priority Storage", [("U Disk", "U"), ("SD Card", "SD")], storage)

    # Button Frame inside container
    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="OK", font=("Arial", 12), width=15,
              command=lambda: messagebox.showinfo("Saved", "Working mode settings saved")).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Exit", font=("Arial", 12), width=15, bg="red", fg="white",
              command=show_main_menu).pack(side="left", padx=10)

    keyboard_frame.pack_forget()






def open_keypad(entry_widget):

    global keypad_frame
    try:
        keypad_frame.destroy()
    except((NameError, tk.TclError)):
        pass

    keypad_frame = tk.Frame(entry_widget.master, bg="lightgray", bd=2, relief="ridge")
    keypad_frame.pack(pady=5, padx=10, anchor="w")

    input_var = tk.StringVar()
    input_var.set(entry_widget.get())

    # Display field inside keypad
    display = tk.Entry(keypad_frame, textvariable=input_var, font=("Arial", 12), justify="right", state="readonly", width=10)
    display.grid(row=0, column=0, columnspan=3, pady=5)
    
    
    
    
    
    def update_display(val):
        current = input_var.get()
        input_var.set(current + val)

    def backspace():
        current = input_var.get()
        input_var.set(current[:-1])

    def clear():
        input_var.set("")

    # def apply_value():
    #     entry_widget.config(state='normal')
    #     entry_widget.delete(0, tk.END)
    #     entry_widget.insert(0, input_var.get())
    #     entry_widget.config(state='readonly')
    #     keypad_frame.destroy()

    def apply_value():
        try:
            val = int(input_var.get())
            if 3 <= val <= 20:
                entry_widget.config(state='normal')
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, str(val))
                entry_widget.config(state='readonly')
                keypad_frame.destroy()
            else:
                messagebox.showwarning("Invalid", "Please enter a value between 3 and 20.")
        except ValueError:
            messagebox.showwarning("Invalid", "Please enter a numeric value.")




    buttons = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        ('0', 4, 1)
    ]

    for (text, row, col) in buttons:
        tk.Button(keypad_frame, text=text, font=("Arial", 10), width=4,
                  command=lambda t=text: update_display(t)).grid(row=row, column=col, padx=2, pady=2)

    # Back, Clear, OK buttons
    tk.Button(keypad_frame, text="←", font=("Arial", 10), width=4, command=backspace).grid(row=4, column=0, padx=2, pady=2)
    tk.Button(keypad_frame, text="C", font=("Arial", 10), width=4, command=clear).grid(row=4, column=2, padx=2, pady=2)
    tk.Button(keypad_frame, text="OK", font=("Arial", 10, "bold"), width=12, bg="green", fg="white", command=apply_value).grid(row=5, column=0, columnspan=3, pady=5)







def show_printer_setup():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Outer Container
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(container, text="Rec Setup", font=("Arial", 12,"bold"), bg="white").pack(pady=(10, 20))

    auto_format = tk.StringVar(value="3x4")
    analysis_result = tk.StringVar(value="on")
    avg_wave = tk.StringVar(value="on")
    selected_rhythm_lead = tk.StringVar(value="off")
    sensitivity = tk.StringVar(value="High")


    def add_radiobutton_group(frame, title, options, variable):
        box = tk.LabelFrame(frame, text=title, bg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
        box.pack(fill='x', padx=20, pady=(3, 0))
        btn_row = tk.Frame(box, bg="white")
        btn_row.pack(anchor='w')  # Horizontal button row
        for text in options:
            tk.Radiobutton(btn_row, text=text, variable=variable, value=text, bg="white", font=("Arial", 10)).pack(side='left', padx=10, pady=2)

    # Horizontal Radio Groups
    add_radiobutton_group(container, "Auto Rec Format", ["3x4", "3x2+2x3"], auto_format)
    add_radiobutton_group(container, "Analysis Result", ["on", "off"], analysis_result)
    add_radiobutton_group(container, "Avg Wave", ["on", "off"], avg_wave)

    # Rhythm Lead
    rhythm_leads_frame = tk.LabelFrame(container, text="Rhythm Lead", bg="white", font=("Arial", 12, "bold"), padx=10, pady=10)
    rhythm_leads_frame.pack(fill='x', padx=20, pady=(3, 0))

    lead_options = ["off", "I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    first_row = tk.Frame(rhythm_leads_frame, bg="white")
    first_row.pack(anchor='w')
    second_row = tk.Frame(rhythm_leads_frame, bg="white")
    second_row.pack(anchor='w')

    for i, lead in enumerate(lead_options):
        row = first_row if i < 7 else second_row
        tk.Radiobutton(row, text=lead, variable=selected_rhythm_lead, value=lead, bg="white", font=("Arial", 10)).pack(side='left', padx=5, pady=2)

    # Automatic Time
    time_frame = tk.LabelFrame(container, text="Automatic Time (sec/Lead)", bg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
    time_frame.pack(fill='x', padx=20, pady=(5, 0))

  

    time_entry = tk.Entry(time_frame, state='readonly', font=("Arial", 10))
    time_entry.insert(0, "3")
    time_entry.pack(anchor='w', padx=10, pady=2)

    time_entry.bind("<Button-1>", lambda event: open_keypad(time_entry))




    # Analysis Sensitivity - Horizontal Layout
    sens_frame = tk.LabelFrame(container, text="Analysis Sensitivity", bg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
    sens_frame.pack(fill='x', padx=20, pady=(5, 0))

    for text in ["Low", "Med", "High"]:
        tk.Radiobutton(sens_frame, text=text, variable=sensitivity, value=text, bg="white", font=("Arial", 10)).pack(side='left', padx=15, pady=2)

    # OK and Exit Buttons
    button_frame = tk.Frame(container, bg="white")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="OK", font=("Arial", 12), width=15,
            command=lambda: messagebox.showinfo("Saved", "Printer setup saved")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Exit", font=("Arial", 12), width=15, bg="red", fg="white",
            command=show_main_menu).pack(side="left", padx=10)

    keyboard_frame.pack_forget()





def open_filter_settings():
    clear_content()  

    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(container, text="Set Filter", font=("Arial", 14, "bold"), bg="white").pack(pady=(10, 20))

    # --- AC Filter Box ---
    ac_var = tk.StringVar(value="50Hz")
    ac_options = [("off", "off"), ("50Hz", "50Hz"), ("60Hz", "60Hz")]
    ac_frame = tk.LabelFrame(container, text="AC Filter", font=("Arial", 12, "bold"), bg="white", padx=10, pady=5)
    ac_frame.pack(fill="x", padx=20, pady=10)
    for text, val in ac_options:
        tk.Radiobutton(ac_frame, text=text, variable=ac_var, value=val, font=("Arial", 11), bg="white").pack(side="left", padx=10)

    
    # --- EMG Filter Box ---
    emg_var = tk.StringVar(value="35Hz")
    emg_options = [("25Hz", "25Hz"), ("35Hz", "35Hz"), ("45Hz", "45Hz"),
                ("75Hz", "75Hz"), ("100Hz", "100Hz"), ("150Hz", "150Hz")]
    emg_frame = tk.LabelFrame(container, text="EMG Filter", font=("Arial", 12, "bold"), bg="white", padx=10, pady=5)
    emg_frame.pack(fill="x", padx=20, pady=10)
    for text, val in emg_options:
        tk.Radiobutton(emg_frame, text=text, variable=emg_var, value=val, font=("Arial", 11), bg="white").pack(side="left", padx=10)

    # --- DFT Filter Box ---
    dft_var = tk.StringVar(value="0.5Hz")
    dft_options = [("off", "off"), ("0.05Hz", "0.05Hz"), ("0.5Hz", "0.5Hz")]
    dft_frame = tk.LabelFrame(container, text="DFT Filter", font=("Arial", 12, "bold"), bg="white", padx=10, pady=5)
    dft_frame.pack(fill="x", padx=20, pady=10)
    for text, val in dft_options:
        tk.Radiobutton(dft_frame, text=text, variable=dft_var, value=val, font=("Arial", 11), bg="white").pack(side="left", padx=10)

    # --- Buttons ---
    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="OK", width=10, font=("Arial", 11),
              command=lambda: print("Saved")).pack(side='left', padx=10)
    tk.Button(btn_frame, text="Cancel", width=10, font=("Arial", 11),
              command=clear_content, bg="red", fg="white").pack(side='left', padx=10)




def validate_factory_key(new_value):
    if new_value in ("", "0-999999"):
        return True
    if new_value.isdigit() and 0 <= int(new_value) <= 999999:
        return True
    return False

def show_maintain_password():
    for widget in content_frame.winfo_children():
        widget.destroy()

    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=50, pady=50, fill='both', expand=True)

    tk.Label(container, text="Enter Maintain Password", font=("Arial", 14, "bold"), bg="gray", fg="white").pack(fill='x')

    form_frame = tk.Frame(container, bg="white")
    form_frame.pack(pady=40)

    tk.Label(form_frame, text="Factory Key:", font=("Arial", 12, "bold"), bg="white", anchor="w").grid(row=0, column=0, padx=10, pady=10)

    key_var = tk.StringVar(value="0-999999")

    def on_entry_click(event):
        if key_var.get() == "0-999999":
            key_var.set("")
            key_entry.config(fg="black")

    def on_focus_out(event):
        if key_var.get() == "":
            key_var.set("0-999999")
            key_entry.config(fg="gray")

    # Validation setup
    vcmd = (root.register(validate_factory_key), '%P')

    key_entry = tk.Entry(form_frame, textvariable=key_var, font=("Arial", 12), width=15, justify='center',
                         validate="key", validatecommand=vcmd, fg="gray")
    key_entry.grid(row=0, column=1, padx=10, pady=10)

    key_entry.bind("<FocusIn>", on_entry_click)
    key_entry.bind("<FocusOut>", on_focus_out)
    # key_entry.bind("<Button-1>", lambda e: [on_entry_click(e), open_keypad(key_entry)])  # optional keypad

    # Buttons
    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=10)

    def on_confirm():
        key = key_var.get()
        if key.isdigit() and 0 <= int(key) <= 999999:
            messagebox.showinfo("Confirmed", f"Key Accepted: {key}")
        else:
            messagebox.showerror("Invalid", "Please enter a valid number between 0 and 999999.")

    tk.Button(btn_frame, text="Confirm", font=("Arial", 12), width=25, height=2, command=on_confirm).pack(pady=10)
    tk.Button(btn_frame, text="Exit", font=("Arial", 12), width=25, height=2, bg="red", fg="white", command=show_main_menu).pack(pady=10)

    keyboard_frame.pack_forget()







def show_time_setup_inside(container):
    for widget in container.winfo_children()[1:]:  
        widget.destroy()

    fields = [("Year", "2025"), ("Month", "06"), ("Day", "17"),
              ("Hour", "12"), ("Minute", "00"), ("Second", "00")]

    entries = {}

    time_frame = tk.Frame(container, bg="white")
    time_frame.pack(pady=20)

    for label, default in fields:
        block = tk.Frame(time_frame, bg="white")
        block.pack(fill="x", pady=5)

        tk.Label(block, text=label, font=("Arial", 11, "bold"), width=10, anchor="w", bg="white").pack(side="left", padx=10)

        entry = tk.Entry(block, font=("Arial", 11), width=10)
        entry.insert(0, default)
        entry.pack(side="left", padx=10)

        # Enable keypad on click

        entries[label] = entry

    # OK and Cancel Buttons
    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=20)

    def lock_data():
        for entry in entries.values():
            entry.config(state="disabled")


    def cancel_action():
        show_system_setup()

    tk.Button(btn_frame, text="OK", width=20, height=2, font=("Arial", 11), command=lock_data).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", width=20, height=2, font=("Arial", 11), command=cancel_action).pack(side="left", padx=10)





def show_system_setup():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Outer Container
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill="both", expand=True)

    tk.Label(container, text="System Setup", font=("Arial", 14, "bold"), bg="gray", fg="white").pack(fill="x")

    inner_frame = tk.Frame(container, bg="white")
    inner_frame.pack(pady=20)

    BOX_WIDTH = 350

    
    
    # --- BEAT VOL Block ---
    beat_vol_block = tk.Frame(inner_frame, bg="white", bd=2, relief="groove", width=BOX_WIDTH, height=80)
    beat_vol_block.pack(pady=10)
    beat_vol_block.pack_propagate(False)

    # Title
    tk.Label(beat_vol_block, text="BEAT VOL", font=("Arial", 11, "bold"), bg="lightgray", fg="black").pack(fill="x")

    # Radio Buttons
    beat_vol_var = tk.StringVar(value="on")
    beat_row = tk.Frame(beat_vol_block, bg="white")
    beat_row.pack(pady=10)

    tk.Radiobutton(beat_row, text="Off", variable=beat_vol_var, value="off", bg="white", font=("Arial", 10)).pack(side="left", padx=15)
    tk.Radiobutton(beat_row, text="On", variable=beat_vol_var, value="on", bg="white", font=("Arial", 10)).pack(side="left", padx=15)

    
    


    # --- LANGUAGE Block ---
    language_block = tk.Frame(inner_frame, bg="white", bd=2, relief="groove", width=BOX_WIDTH, height=80)
    language_block.pack(pady=10)
    language_block.pack_propagate(False)

    tk.Label(language_block, text="LANGUAGE", font=("Arial", 11, "bold"), bg="lightgray", fg="black").pack(fill="x")

    language_var = tk.StringVar(value="English")
    lang_row = tk.Frame(language_block, bg="white")
    lang_row.pack(pady=10)

    tk.Radiobutton(lang_row, text="English", variable=language_var, value="English", bg="white", font=("Arial", 10)).pack(side="left", padx=15)
    tk.Radiobutton(lang_row, text="Hindi", variable=language_var, value="Hindi", bg="white", font=("Arial", 10)).pack(side="left", padx=15)





    # --- Time Setup Button ---
    tk.Button(container, text="Time Setup >>", bg="navy", fg="white", font=("Arial", 12), width=30, height=2,
              command=lambda: show_time_setup_inside(container)).pack(pady=20)

    # --- OK and Cancel Buttons ---
    def save_settings():
        selected_beat = beat_vol_var.get()
        selected_lang = language_var.get()
        # Here, you can add your logic to store the values or display
        print(f"Saved: BEAT VOL = {selected_beat}, Language = {selected_lang}")
        messagebox.showinfo("Saved", "Settings saved successfully!")

    def cancel_action():
        show_main_menu()

    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="OK", width=20, height=2, font=("Arial", 11), command=save_settings).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", width=20, height=2, font=("Arial", 11), command=cancel_action).pack(side="left", padx=10)







def show_version_info():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Outer Container
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill="both", expand=True)

    # Header
    tk.Label(container, text="Version Info", font=("Arial", 14, "bold"), bg="gray", fg="white").pack(fill="x", pady=(0, 20))

    # Inner Frame using grid layout for neat column alignment
    inner_frame = tk.Frame(container, bg="white")
    inner_frame.pack(pady=10)

    versions = [
        ("1. System Version:", "VER 1.6"),
        ("2. PM Version:", "VER 1.2"),
        ("3. KB Version:", "VER 3.22")
    ]

    for i, (label_text, version_text) in enumerate(versions):
        tk.Label(inner_frame, text=label_text, font=("Arial", 11, "bold"), bg="white", anchor="w", width=20).grid(row=i, column=0, padx=(30,10), pady=10, sticky="w")
        tk.Label(inner_frame, text=version_text, font=("Arial", 11), bg="white", anchor="w", width=15).grid(row=i, column=1, padx=10, pady=10, sticky="w")
        
    # Exit Button
    def exit_to_main():
        show_main_menu()

    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=30)

    tk.Button(btn_frame, text="Exit", width=30, height=2, font=("Arial", 11),
              bg="skyblue", command=exit_to_main).pack()


def show_factory_default_config():
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Outer Container
    container = tk.Frame(content_frame, bg="white", bd=2, relief="solid")
    container.pack(padx=30, pady=30, fill="both", expand=True)

    # Header
    tk.Label(container, text="HINT", font=("Arial", 14, "bold"), bg="gray", fg="white").pack(fill="x", pady=(0, 20))

    # Message
    tk.Label(container, text="Adopt Factory Default Config?", font=("Arial", 12, "bold"), bg="white").pack(pady=(30, 10))
    tk.Label(container, text="The Previous Configure Will Be Lost!", font=("Arial", 10), bg="white", fg="red").pack(pady=(0, 20))

    # Button Actions
    def apply_default_config():
        
        print("Factory Defaults Applied")
        messagebox.showinfo("Done", "Factory defaults applied successfully.")
        show_main_menu()  

    def cancel_action():
        show_main_menu()

    # Buttons
    btn_frame = tk.Frame(container, bg="white")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="No", width=10, bg="navy", fg="white", font=("Arial", 11), command=cancel_action).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Yes", width=10, font=("Arial", 11), command=apply_default_config).pack(side="left", padx=10)





# --------- EXIT Page ---------
def show_exit_page():
    for widget in content_frame.winfo_children():
        widget.destroy()

    exit_frame = tk.Frame(content_frame, bg="white")
    exit_frame.pack(pady=50)

    tk.Label(exit_frame, text="Do you really want to exit?", font=("Arial", 16), bg="white", fg="black").pack(pady=20)

    tk.Button(exit_frame, text="Yes - Exit", font=("Arial", 12), bg="red", fg="white", width=15,
              command=root.destroy).pack(pady=5)

    tk.Button(exit_frame, text="No - Back", font=("Arial", 12), bg="green", fg="white", width=15,
              command=show_main_menu).pack(pady=5)

    keyboard_frame.pack_forget()
    
    
    
    # --------- Button Handler ---------
    
    
    
menu_buttons = {}



def button_clicked(name):
    
    
    for btn in menu_buttons.values():
        btn.config(bg="SystemButtonFace")

    # Highlight the clicked button
    if name in menu_buttons:
        menu_buttons[name].config(bg="skyblue")
    
    
    if name == "Exit":
        show_exit_page()
    elif name == "SAVE ECG >>":
        show_save_ecg()
    elif name == "WORKING MODE >>":
        show_working_mode()    
    elif name == "PRINTER SETUP >>":
        show_printer_setup()
    elif name =="SET FILTER >>":    
        open_filter_settings()
    elif name ==  "SYSTEM SETUP >>" :
        show_system_setup()
    elif name == "FACTORY MAINTAIN >>":
        show_maintain_password()
    elif name == "VERSION >>":
        show_version_info() 
    elif name == "LOAD DEFAULT >>" :
        show_factory_default_config()    
    elif name == "OPEN ECG >>":
        open_ecg_window()
         
    else:
        messagebox.showinfo("Clicked", f"{name} button clicked!")
        
def show_main_menu():
    for widget in content_frame.winfo_children():
        widget.destroy()
    keyboard_frame.pack_forget()
    
    tk.Label(content_frame, text="Deck⚡︎mount", font=("Arial", 40, "bold"), fg="black", bg="white").pack(pady=(10, 5))
    
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()
    
        

# --------- Main Menu Buttons ---------
buttons = [
    "SAVE ECG >>", "OPEN ECG >>", "WORKING MODE >>", "PRINTER SETUP >>",
    "SET FILTER >>", "SYSTEM SETUP >>", "LOAD DEFAULT >>", "VERSION >>",
    "FACTORY MAINTAIN >>", "Exit"
]



for text in buttons:
    btn = tk.Button(menu_frame, text=text, font=("Arial", 14), width=25, height=2,
                    command=lambda t=text: button_clicked(t))
    btn.pack(pady=3)
    menu_buttons[text] = btn  

root.mainloop()



