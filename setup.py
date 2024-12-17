# setup.py
import os
import json
from tkinter import Tk, filedialog

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {"log_directory": "C:\\KeyLogs"}

def setup_log_directory():
    """
    Setup the log directory by allowing the owner to choose a folder via a GUI menu.
    """
    if not os.path.exists(CONFIG_FILE):
        print("Welcome to the Keylogger Setup!")

        # Create a Tkinter root window and hide it
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        # Open a folder selection dialog
        print("Please select a folder to store the log files.")
        log_directory = filedialog.askdirectory(title="Select Log Directory")

        # If no folder is selected, default to the preset directory
        if not log_directory:
            print("No folder selected. Defaulting to 'C:\\KeyLogs'.")
            log_directory = DEFAULT_CONFIG["log_directory"]

        # Create the directory if it doesn't exist
        os.makedirs(log_directory, exist_ok=True)

        # Set permissions to restrict access (Windows)
        try:
            # Remove inheritance
            os.system(f'icacls "{log_directory}" /inheritance:r')
            # Grant full control to administrators
            os.system(f'icacls "{log_directory}" /grant:r "Administrators:(OI)(CI)F" /T')
            print(f"Permissions set: Only the Administrators can access {log_directory}")
        except Exception as e:
            print(f"Could not set permissions: {e}")

        # Save configuration
        with open(CONFIG_FILE, "w") as file:
            json.dump({"log_directory": log_directory}, file)

        print(f"Log directory configured: {log_directory}")
    else:
        print("Configuration file found. Proceeding with the keylogger setup.")

    # Load and return the log directory from the configuration
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config["log_directory"]

if __name__ == "__main__":
    setup_log_directory()