from settings import FFmpegSettings
import subprocess
from pynput.keyboard import Key, Controller
import psutil
import time

track_apps_process = ['chrome', 'chrome.exe', 'winword.exe', 'notepad', 'notepad.exe']
os = FFmpegSettings().get_operating_system()
keyboard = Controller()

def running_programs():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in track_apps_process:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
        
def program_listener():
    recording_process = None
    recording_started = False

    print("\nMonitoring for Tracked Applications launch...")
    try:
        while True:
            app_running = running_programs()
            
            if app_running and not recording_started:
                print("\nTracked app detected. Starting recording...")
                if os == "Windows":
                    recording_process = subprocess.Popen(["python", "core/recorder.py"])
                    recording_started = True
                elif os == "Linux":
                    recording_process = subprocess.Popen(["python3", "core/linux_recorder.py"])
                    recording_started = True

            elif not app_running and recording_started:
                print("\nTracked app closed. Stopping recording...")
                
                keyboard.press(key=Key.esc)
                keyboard.release(key=Key.esc)
                if recording_process:
                    recording_process.wait()
                recording_started = False
                program_listener()

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nAutomation script interrupted. Exiting...")
        return None

if __name__ == "__main__":
    program_listener()