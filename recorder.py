from ffmpeg import FFmpeg, Progress, FFmpegError
from win32api import GetSystemMetrics
import subprocess
import threading
import keyboard
import datetime
import time

WIDTH, HEIGHT = GetSystemMetrics(0), GetSystemMetrics(1) # Gets monitor dimensions
running = True
FPS = 30
OUTPUT_FILE = f"{datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')}.mkv"

def ffmpeg_encoder():
    # Can we tell ffmpeg to read in from memory (i.e. your frames) as an input source, rather than standard input?
    AUDIO_DEVICE = "Stereo Mix (Realtek(R) Audio)"
    
    try:
        mss_stream = subprocess.Popen(
            'python screen_capture.py',
            stdout=subprocess.PIPE
        )
        
        ffmpeg = (
            FFmpeg()
            .option("y")  # Overwrite existing file
            .input(f"audio={AUDIO_DEVICE}", f="dshow", ac=2, ar=44100, audio_buffer_size="80m")
            .input("pipe:0", f="rawvideo", s=f"{WIDTH}x{HEIGHT}", pix_fmt="bgra", r=FPS)
            .output(OUTPUT_FILE, vcodec="libx264", pix_fmt="yuv420p")
        )
        
        @ffmpeg.on("progress")
        def time_to_terminate(progress: Progress):
            # If you have recorded more than 200 frames, stop recording
            print(progress)
            if not running:
                print('\nterminating recording...')
                ffmpeg.terminate()
                
        # Start FFmpeg process using stdin for real-time frame input
        print('\nencoding video...\n')
        ffmpeg.execute(mss_stream.stdout)
    
    except FFmpegError as exception:
        print("An exception has occurred!")
        print("- Message from ffmpeg:", exception.message)
        print("- Arguments to execute ffmpeg:", exception.arguments)

def main():
    global running
    
    capture_thread = threading.Thread(target=ffmpeg_encoder)
    capture_thread.start()
    
    if keyboard.read_key() == "esc":
        print("\nStopping Recording...")
        running = False
        capture_thread.join()
        
        print('\nVideo saved.')

if __name__ == '__main__':
    main()