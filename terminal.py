import serial
import time

# Configuration
USB_PORT = "COM5"  # Change this to your USB port (e.g., "/dev/ttyUSB0" for Linux/Mac, "COMx" for Windows)
BAUD_RATE = 9600   # Match the baud rate of your USB device

try:
    # Open the serial connection
    with serial.Serial(USB_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Connected to {USB_PORT} at {BAUD_RATE} baud.")
        
        while True:
            # Read data from the USB device
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                print(f"Received: {data}")
            time.sleep(0.1)  # Adjust the polling rate if necessary
except serial.SerialException as e:
    print(f"Error: {e}")
except KeyboardInterrupt:
    print("\nExiting.")
