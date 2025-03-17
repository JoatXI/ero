from ffmpeg import FFmpeg, Progress, FFmpegError
import subprocess
import threading
import pyautogui
import keyboard
import datetime
import platform
import cpuinfo
import GPUtil

class Encoder:
    def __init__(self):
        self.nvidia_gpu = GPUtil.getGPUs()
        self.info = cpuinfo.get_cpu_info()
        self.os = platform.system()
        self.amd_gpu = False
    
    def set_encoder(self):
        print(self.os)
        
        if self.os == "Windows":
            process = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"]).decode()
            self.amd_gpu = any(keyword in process for keyword in ["AMD", "Radeon"])
        elif self.os == "Linux":
            output = subprocess.check_output("lspci", shell=True).decode()
            self.amd_gpu = any("AMD" in line or "Radeon" in line for line in output.splitlines())

        try:
            if "Intel" in self.info.get("brand_raw", "") and self.nvidia_gpu:
                return "h264_nvenc"
            elif "Intel" in self.info.get("brand_raw", "") and not self.nvidia_gpu:
                return "h264_qsv"
            elif "AMD" in self.info.get("brand_raw", "") and self.nvidia_gpu:
                return "h264_nvenc"
            elif "AMD" in self.info.get("brand_raw", "") or self.amd_gpu:
                return "h264_amf"
            else:
                return "libx264"
        except Exception as e:
            print("Error setting encoder:", e)
            return "libx264"

class ScreenRecorder:
    def __init__(self, encoder, fps=30, audio_device="Stereo Mix (Realtek(R) Audio)"):
        self.file_name = f"{datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')}.mkv"
        self.width, self.height = pyautogui.size()
        self.audio_device = audio_device
        self.encoder = encoder
        self.running = False
        self.fps = fps
        
    def ffmpeg_encoder(self):
        try:
            mss_stream = subprocess.Popen(
                'python screen_capture.py',
                stdout=subprocess.PIPE
            )
            
            ffmpeg = (
                FFmpeg()
                .option("y")
                .input("pipe:0", f="rawvideo", s=f"{self.width}x{self.height}", pix_fmt="bgra", r=self.fps)
                .input(f"audio={self.audio_device}", rtbufsize="1024M", f="dshow", ac=2, ar=44100, channel_layout="stereo", audio_buffer_size="80m")
                .output(self.file_name, acodec="copy", vcodec=self.encoder, pix_fmt="yuv420p", preset="slow", crf=22, shortest=None)
            )
            
            @ffmpeg.on("progress")
            def time_to_terminate(progress: Progress):
                print(progress)
                if not self.running:
                    print('\nterminating recording...')
                    ffmpeg.terminate()
                    
            print('\nencoding video...\n')
            ffmpeg.execute(mss_stream.stdout)
        
        except FFmpegError as exception:
            print("An exception has occurred!")
            print("- Message from ffmpeg:", exception.message)
            print("- Arguments to execute ffmpeg:", exception.arguments)

    def start_recording(self):
        self.running = True
        
        encoding_thread = threading.Thread(target=self.ffmpeg_encoder)
        encoding_thread.start()
        
        if keyboard.read_key() == "esc":
            print("\nStopping Recording...")
            self.running = False
            
            encoding_thread.join()
            print('\nVideo saved.')

if __name__ == '__main__':
    encoder = Encoder()
    selected_encoder = encoder.set_encoder()
    
    recorder = ScreenRecorder(selected_encoder)
    recorder.start_recording()