import serial
import threading

class SerialECGReader(threading.Thread):
    def __init__(self, port, baudrate):
        super().__init__()
        self.ser = serial.Serial(port, baudrate, timeout=0.01)
        self.running = True

    def run(self):
        while self.running:
            line = self.ser.readline()
            # Process line as needed

    def stop(self):
        self.running = False
        self.ser.close()