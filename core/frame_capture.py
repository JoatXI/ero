from mss import mss, exception
import numpy as np
import threading
import pyautogui
import keyboard
import time
import sys

WIDTH, HEIGHT = pyautogui.size()
running = True
FPS = 30

def send_frames():
    try:
        with mss() as sct:
            monitor = {"top": 0, "left": 0, "width": WIDTH, "height": HEIGHT}
            
            while running:
                last_time = time.time()
                
                frame = np.array(sct.grab(monitor))
                sys.stdout.buffer.write(frame.tobytes())
                
                time_diff = time.time() - last_time
                time.sleep(max(1.0 / FPS - time_diff, 0))
                
            sys.stdout.buffer.close()
            
    except exception.ScreenShotError as e:
        print("An error occurred while acquiring screen capture: ", e)

def main():
    global running
    
    capture_thread = threading.Thread(target=send_frames)
    capture_thread.start()
    
    if keyboard.read_key() == "esc":
        running = False
        capture_thread.join()

if __name__ == '__main__':
    main()