from linux_recorder import LinuxEncoder
from plyer import notification
from recorder import Encoder
import platform, time, sys
import psutil

track_apps_process = ['chrome', 'chrome.exe', 'winword.exe', 'notepad', 'notepad.exe']
os = platform.system()

def running_procresses():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in track_apps_process:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
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

    print('\nMonitoring for Tracked Applications launch...')
    try:
        while True:
            app_running = running_procresses()
            
            if app_running and not recording_started:
                print('\nTracked app detected. Starting recording...')
                
                if os == 'Windows':
                    windows_rocorder = Encoder()
                    windows_rocorder.start_windows_recording()
                    recording_started = True
                    system_notification('Ẹro', 'Application started screen and audio recording')
                elif os == 'Linux':
                    linux_recorder = LinuxEncoder()
                    linux_recorder.start_linux_recording()
                    recording_started = True
                    system_notification('Ẹro', 'Application started screen and audio recording')

            elif not app_running and recording_started:
                print('\nTracked app closed. Stopping recording...')

                if os == "Windows":
                    windows_rocorder.stop_windows_recording()
                    recording_started = False
                if os == "Linux":
                    linux_recorder.stop_linux_recording()
                    recording_started = False
                
                system_notification('Ẹro', 'Application recording stopped')
                automate_recoder()

            time.sleep(2)
    except KeyboardInterrupt:
        print('\nAutomation script interrupted. Exiting...')
        sys.exit(1)

if __name__ == '__main__':
    automate_recoder()