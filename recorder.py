from ffmpeg import FFmpeg, Progress, FFmpegError
from win32api import GetSystemMetrics
from mss import mss, exception
import numpy as np
import subprocess
import threading
import keyboard
import datetime
import time

WIDTH, HEIGHT = GetSystemMetrics(0), GetSystemMetrics(1) # Gets monitor dimensions
running = True
FPS = 30
OUTPUT_FILE = f"{datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")}.mkv"

def ffmpeg_encoder():
    # Can we tell ffmpeg to read in from memory (i.e. your frames) as an input source, rather than standard input?
    AUDIO_DEVICE = "Stereo Mix (Realtek(R) Audio)"
    
    try:
        ffmpeg = (
            FFmpeg()
            .option("y")  # Overwrite existing file
            .input(f"audio={AUDIO_DEVICE}", f="dshow", ac=2, ar=44100, audio_buffer_size="80m", t=10)
            .input("pipe:0", f="rawvideo", s=f"{WIDTH}x{HEIGHT}", pix_fmt="bgra", r=FPS)
            .output(OUTPUT_FILE, vcodec="libx264", pix_fmt="yuv420p")
        )
        
        # Start FFmpeg process using stdin for real-time frame input
        return subprocess.Popen(ffmpeg.arguments, stdin=subprocess.PIPE)
    
    except FFmpegError as exception:
        print("An exception has occurred!")
        print("- Message from ffmpeg:", exception.message)
        print("- Arguments to execute ffmpeg:", exception.arguments)

def screen_capture():
    try:
        with mss() as sct:
            # Define screen monitor capture settings
            monitor = {"top": 0, "left": 0, "width": WIDTH, "height": HEIGHT}
            
            process = ffmpeg_encoder()
            while running:
                # Capture screen frame
                frame = np.array(sct.grab(monitor))
                process.stdin.write(frame.tobytes()) # write raw bytes to standard input?
                
                time.sleep(1.0 / FPS)
            
            process.stdin.close()
            process.wait()
            
    except exception.ScreenShotError as e:
        print("An error occurred while acquiring screen capture: ", e)

def end_recording():
    global running
    print("\n",keyboard.read_key())
    
    if keyboard.read_key() == "esc":
        print("\nStopping Recording...")
        running = False

def main():
    global running
    
    stopper = threading.Thread(target=end_recording, daemon=True)
    stopper.start()
    
    capture_thread = threading.Thread(target=screen_capture, daemon=True)
    capture_thread.start()
    
    capture_thread.join()
    
    print('Video saved.')
    
if __name__ == '__main__':
    main()