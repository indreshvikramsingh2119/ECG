import serial
import threading
import time

# Parameters
PORT = "COM5"  # Replace with your device's port
BAUD_RATE =9600 #eplace with your device's baud rate
RUNNING = False  # Global flag to control data reception


def detect_data_type(data):
    """
    Detect the type of the data.
    """
    try:
        int(data)
        return "Integer"
    except ValueError:
        pass

    try:
        int(data, 16)
        return "Hexadecimal"
    except ValueError:
        pass

    if data.isalpha():
        return "Alphabetic Text"

    if data.isalnum():
        return "Alphanumeric Text"

    return "Unknown/Other"


def read_from_device(ser):
    """
    Function to continuously read data from the device when RUNNING is True.
    """
    global RUNNING
    while True:
        if RUNNING:
            try:
                # Read data from the device
                raw_data = ser.readline().decode('utf-8', errors='replace').strip()

                if raw_data:
                    # Determine the type of data
                    data_type = detect_data_type(raw_data)

                    # Print raw data and its type
                    print(f"Received: {raw_data} | Type: {data_type}")

            except Exception as e:
                print(f"Error reading data: {e}")

        else:
            time.sleep(0.1)  # Reduce CPU usage when not receiving data


def main():
    global RUNNING
    try:
        # Open serial connection
        with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
            print(f"Connected to {PORT} at {BAUD_RATE} baud.")
            print("Press '1' to start receiving data and '0' to stop.")

            # Start a thread to read data from the device
            reader_thread = threading.Thread(target=read_from_device, args=(ser,))
            reader_thread.daemon = True
            reader_thread.start()

            while True:
                # Take user input to control data reception
                command = input("Enter command (1 to start, 0 to stop, q to quit): ").strip()

                if command == "1":
                    RUNNING = True
                    print("Started receiving data.")
                elif command == "0":
                    RUNNING = False
                    print("Stopped receiving data.")
                elif command.lower() == "q":
                    print("Exiting.")
                    RUNNING = False
                    break
                else:
                    print("Invalid command. Use '1', '0', or 'q'.")

    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nStopped listening.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
