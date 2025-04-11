from ffmpeg import FFmpeg, Progress, FFmpegError
from settings import FFmpegSettings
import threading, sys
import pyautogui

class LinuxEncoder:
    def __init__(self):
        self.audio_device, self.input_format = FFmpegSettings().set_audio_inputs()
        self.video_input, self.f_video = FFmpegSettings().set_video_inputs()
        self.file_name, self.fps = FFmpegSettings().set_output()
        self.width, self.height = pyautogui.size()
        self.encoding_thread = None
        self.running = False
        
    def ffmpeg_encoder(self):
        try:
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input(self.video_input, video_size=f"{self.width}x{self.height}", framerate=self.fps, f=self.f_video)
                .input(self.audio_device, f=self.input_format, ac=2, sample_rate=44100, channels=2, itsoffset=0.5)
                .output(self.file_name, acodec="libmp3lame", vcodec="libx264", crf=28, preset="ultrafast")
            )
            
            @ffmpeg.on("progress")
            def time_to_terminate(progress: Progress):
                print(progress)
                if not self.running:
                    print('\nterminating recording...')
                    ffmpeg.terminate()
                    
            print('\nencoding video...\n')
            ffmpeg.execute()
        
        except FFmpegError as exception:
            print("An exception has occurred!")
            print("- Message from ffmpeg:", exception.message)
            print("- Arguments to execute ffmpeg:", exception.arguments)
            sys.exit(1)

    def start_linux_recording(self):
        self.running = True
        
        self.encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        self.encoding_thread.start()

    def stop_linux_recording(self):
        print("\nStopping Recording...")
        self.running = False
        if self.encoding_thread:
            self.encoding_thread.join()
            print('\nVideo saved.')

if __name__ == '__main__':
    recorder = LinuxEncoder()
    recorder.start_linux_recording()