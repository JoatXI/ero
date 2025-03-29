import time
import psutil
import subprocess
import keyboard

track_apps_process = ['chrome.exe', 'winword.exe', 'notepad.exe']

def running_programs():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in track_apps_process:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

def main():
    recording_process = None
    recording_started = False

    print("\nMonitoring for Chrome launch...")
    try:
        while True:
            app_running = running_programs()
            
            if app_running and not recording_started:
                print("\nTracked app detected. Starting recording...")
                recording_process = subprocess.Popen(["python", "core/recorder.py"])
                recording_started = True

            elif not app_running and recording_started:
                print("\nTracked app closed. Stopping recording...")
                
                keyboard.press_and_release('esc')
                if recording_process:
                    recording_process.wait()
                recording_started = False

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nAutomation script interrupted. Exiting...")
        return None

if __name__ == "__main__":
    main()