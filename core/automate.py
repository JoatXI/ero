from linux_recorder import LinuxEncoder
import platform, json, time, sys, os
from plyer import notification
from recorder import Encoder
import psutil

CONFIG_FILE = "config.json"

def load_config_apps():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
        return [value for key, value in config.items() if value and key != "automate"]

def running_procresses():
    tracked_apps = load_config_apps()
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in (app.lower() for app in tracked_apps):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False
            
def system_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon='assets/icon.ico',
        timeout=5
    )

def automate_recoder():
    recording_started = False
    try:
        while True:
            app_running = running_procresses()
            
            if app_running and not recording_started:
                if platform.system() == 'Windows':
                    windows_rocorder = Encoder()
                    windows_rocorder.start_windows_recording()
                    recording_started = True
                elif platform.system() == 'Linux':
                    linux_recorder = LinuxEncoder()
                    linux_recorder.start_linux_recording()
                    recording_started = True
                system_notification('Ẹro', 'Application started screen and audio recording')

            elif not app_running and recording_started:
                if platform.system() == "Windows":
                    windows_rocorder.stop_windows_recording()
                    recording_started = False
                elif platform.system() == "Linux":
                    linux_recorder.stop_linux_recording()
                    recording_started = False
                system_notification('Ẹro', 'Application recording stopped')

            time.sleep(2)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    automate_recoder()