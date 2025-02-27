from pathlib import Path
from mss import mss
from ffmpeg import FFmpeg, Progress
import numpy as np
import time
import cv2
import threading
import sys

running = True
frames = []
FPS = 30

def screen_capture():
    with mss() as sct:
        # Define screen capture settings
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        
        while running:
            last_time = time.time()
            
            # Capture screen frame
            img = np.array(sct.grab(monitor))
            
            # cv2.imshow("OpenCV/Numpy normal", img)
            
            frames.append(img)
            time_diff = time.time() - last_time
            time.sleep(max(1.0 / FPS - time_diff, 0))
        
def save_recording():
    height, width, _ = frames[0].shape
    # Can we tell ffmpeg to read in from memory (i.e. your frames) as an input source, rather than standard input?
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input('pipe:0')
        .output("default.mp4", codec='copy')
    )
    print("executing...")
    try:
        
        #print(f"process is {process}")
    
        print("Write frames to FFmpeg stdin")
        # writes the frames to standard input
        
        # Is there an alternative way to access standard input other than sys.stdin, wher write(frame.tobytes()) works?
        # is process.stdin a Python library feature?
        for frame in frames:
            print("in frame loop")
            sys.stdin.write(frame)
            # How can we write raw bytes to standard input?
            sys.stdin.write(frame.tobytes())
        
        ffmpeg.execute(Path("input.ts").read_bytes()) # reads in the frames from standard input
        
    except Exception as e:
        print(e)
    
        
def main():
    global running
    capture_thread = threading.Thread(target=screen_capture, daemon=True)
    capture_thread.start()
    
    time.sleep(10) # Sets recording duration
    running = False
    capture_thread.join()
    
    print('Saving video...')
    save_recording()
    print('Video saved.')
    
if __name__ == '__main__':
    main()