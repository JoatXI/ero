import wave
from mss import mss
import numpy as np
import time
import threading
import subprocess
from ffmpeg import FFmpeg, Progress
import pyaudio

WIDTH, HEIGHT = 1920, 1080
running = True
FPS = 30
# Audio recording settings
RATE, CHUNK = 44100, 1024
CHANNELS, OUTPUT_AUDIO = 2, "output.wav"
FORMAT = pyaudio.paInt16

def ffmpeg_encoder():
    # Can we tell ffmpeg to read in from memory (i.e. your frames) as an input source, rather than standard input?
    ffmpeg = (
        FFmpeg()
        .option("y")  # Overwrite existing file
        .input("pipe:0", f="rawvideo", s=f"{WIDTH}x{HEIGHT}", pix_fmt="bgra", r=FPS)
        .output("default.mp4", vcodec="libx264", pix_fmt="yuv420p")
    )

    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        print(progress)

    # Start FFmpeg process using stdin for real-time frame input
    return subprocess.Popen(ffmpeg.arguments, stdin=subprocess.PIPE)

def screen_capture():
    with mss() as sct:
        # Define screen capture settings
        monitor = {"top": 0, "left": 0, "width": WIDTH, "height": HEIGHT}
        
        process = ffmpeg_encoder()
        while running:
            last_time = time.time()
            
            # Capture screen frame
            frame = np.array(sct.grab(monitor))
            process.stdin.write(frame.tobytes()) # write raw bytes to standard input?
            
            time_diff = time.time() - last_time
            time.sleep(max(1.0 / FPS - time_diff, 0))
        
        process.stdin.close()
        process.wait()

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=2,
                    frames_per_buffer=CHUNK)

    audio_frames = []

    while running:
        data = stream.read(CHUNK)
        audio_frames.append(data)

    # Stop & save audio
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(OUTPUT_AUDIO, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(audio_frames))
        wf.close()

def main():
    global running
    capture_thread = threading.Thread(target=screen_capture, daemon=True)
    audio_thread = threading.Thread(target=record_audio, daemon=True)
    
    capture_thread.start()
    audio_thread.start()
    
    time.sleep(10)
    running = False
    
    capture_thread.join()
    audio_thread.join()
    
    print('Video saved.')
    
if __name__ == '__main__':
    main()