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
    AUDIO_DEVICE = "Stereo Mix (Realtek(R) Audio)"
    
    try:
        mss_stream = subprocess.Popen(
            'python screen_capture.py',
            stdout=subprocess.PIPE
        )
        
        ffmpeg = (
            FFmpeg()
            .option("y")
            .input("pipe:0", f="rawvideo", s=f"{WIDTH}x{HEIGHT}", pix_fmt="bgra", r=FPS)
            .input(f"audio={AUDIO_DEVICE}", rtbufsize="1024M", f="dshow", ac=2, ar=44100, channel_layout="stereo", audio_buffer_size="80m")
            .output(OUTPUT_FILE, vcodec="libx264", pix_fmt="yuv420p", preset="slow", crf=22, shortest=None)
        )
        
        @ffmpeg.on("progress")
        def time_to_terminate(progress: Progress):
            print(progress)
            if not running:
                print('\nterminating recording...')
                ffmpeg.terminate()
                
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