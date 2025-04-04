from pynput.keyboard import Key, Controller
from settings import FFmpegSettings
from plyer import notification
import subprocess
import psutil
import time

track_apps_process = ['chrome', 'chrome.exe', 'winword.exe', 'notepad', 'notepad.exe']
os = FFmpegSettings().get_operating_system()
keyboard = Controller()

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
        app_icon='core/icon.ico',
        timeout=5
    )

def automate_recoder():
    recording_process = None
    recording_started = False

    print('\nMonitoring for Tracked Applications launch...')
    try:
        while True:
            app_running = running_procresses()
            
            if app_running and not recording_started:
                print('\nTracked app detected. Starting recording...')
                
                if os == 'Windows':
                    recording_process = subprocess.Popen(['python', 'core/recorder.py'])
                    recording_started = True
                    system_notification('Ẹro', 'Application started screen and audio recording')
                elif os == 'Linux':
                    recording_process = subprocess.Popen(['python3', 'core/linux_recorder.py'])
                    recording_started = True
                    system_notification('Ẹro', 'Application started screen and audio recording')

            elif not app_running and recording_started:
                print('\nTracked app closed. Stopping recording...')
                
                keyboard.press(key=Key.esc)
                keyboard.release(key=Key.esc)

                if recording_process:
                    recording_process.wait()
                recording_started = False
                
                system_notification('Ẹro', 'Application recording stopped')
                automate_recoder()

            time.sleep(2)
    except KeyboardInterrupt:
        print('\nAutomation script interrupted. Exiting...')
        SystemExit

if __name__ == '__main__':
    automate_recoder()