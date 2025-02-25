from mss import mss
from ffmpeg import FFmpeg
import numpy as np
import time
import cv2
import threading

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
    video_writer = cv2.VideoWriter('default_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (width, height))
    
    for img in frames:
        video_writer.write(cv2.cvtColor(img, cv2.COLOR_RGBA2RGB))
    video_writer.release()
    
    
def main():
    global running
    threading.Thread(target=screen_capture).start()
    
    time.sleep(10) # Sets recording duration
    running = False
    
    print('Saving video...')
    save_recording()
    print('Video saved.')
    
main()