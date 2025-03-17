from mss import mss, exception
import numpy as np
import threading
import pyautogui
import keyboard
import time
import sys

class FrameCapture:
    def __init__(self, fps=30):
        self.width, self.height = pyautogui.size()
        self.running = False
        self.fps = fps

    def screen_capture(self):
        try:
            with mss() as sct:
                monitor = {"top": 0, "left": 0, "width": self.width, "height": self.height}
                
                while self.running:
                    last_time = time.time()
                    
                    frame = np.array(sct.grab(monitor))
                    sys.stdout.buffer.write(frame.tobytes())
                    
                    time_diff = time.time() - last_time
                    time.sleep(max(1.0 / self.fps - time_diff, 0))
                    
                sys.stdout.buffer.close()
                
        except exception.ScreenShotError as e:
            print("An error occurred while acquiring screen capture: ", e)

    def start_stream(self):
        self.running = True
        
        capture_thread = threading.Thread(target=self.screen_capture)
        capture_thread.start()
        
        if keyboard.read_key() == "esc":
            self.running = False
            capture_thread.join()

if __name__ == '__main__':
    mss_stream = FrameCapture()
    mss_stream.start_stream()