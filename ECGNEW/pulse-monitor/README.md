# Pulse Monitor Application

## Overview
The Pulse Monitor application is designed to acquire and display ECG data in real-time using a graphical user interface built with PyQt5. The application communicates with ECG hardware via serial communication to read and process ECG signals.

## Features
- User authentication for secure access.
- Real-time ECG data acquisition and visualization.
- Multiple ECG test modes (e.g., 12 Lead ECG Test, Live Monitoring).
- Data export functionality (PDF and CSV).
- Splash screen during application startup.

## Project Structure
```
pulse-monitor
├── src
│   ├── main.py                # Entry point of the application
│   ├── ecg_reader.py          # Handles serial communication for ECG data
│   ├── gui                     # Contains GUI components
│   │   ├── __init__.py        # Marks the gui directory as a package
│   │   ├── main_window.py      # Main interface of the application
│   │   ├── auth_dialog.py      # User authentication dialog
│   │   ├── ecg_test_page.py    # ECG testing interface
│   │   └── splash_screen.py     # Splash screen during startup
│   ├── utils                   # Contains utility functions
│   │   ├── __init__.py        # Marks the utils directory as a package
│   │   ├── db_data.py         # Database initialization and user management
│   │   └── firebase_auth.py    # User authentication with Firebase
│   └── resources               # Contains resource files
│       └── README.md          # Documentation for resources
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd pulse-monitor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/main.py
   ```

2. Follow the on-screen instructions to log in or register a new user.

3. Select the desired ECG test mode and start data acquisition.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.