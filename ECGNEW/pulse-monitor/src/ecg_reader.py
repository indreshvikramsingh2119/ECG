class SerialECGReader:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False

    def start(self):
        import serial
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.ser.reset_input_buffer()
        self.running = True

    def stop(self):
        if self.ser:
            self.running = False

    def read_value(self):
        if not self.running or self.ser is None:
            return None
        try:
            line_raw = self.ser.readline()
            line_data = line_raw.decode('utf-8', errors='replace').strip()
            if line_data.isdigit():
                return int(line_data)
        except Exception as e:
            print("Error reading from serial:", e)
        return None

    def close(self):
        if self.ser:
            self.ser.close()