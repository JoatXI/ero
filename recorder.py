from mss import mss
from ffmpeg import FFmpeg, Progress
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
    print("shape set")
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
        .output("default.mp4", vcodec='libx264', pix_fmt='yuv420p', r=FPS)
    )
    print("executing...")
    process = ffmpeg.execute()
    
    print("Write frames to FFmpeg stdin")
    for frame in frames:
        print("in frame loop")
        process.stdin.write(frame.tobytes())
    
    print("closing...")
    process.stdin.close()
    process.wait()
    
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