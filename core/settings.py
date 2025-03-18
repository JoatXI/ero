import subprocess
import platform
import cpuinfo
import GPUtil

class FFmpegSettings:
    def __init__(self):
        self.nvidia_gpu = GPUtil.getGPUs()
        self.info = cpuinfo.get_cpu_info()
        self.os = platform.system()
        self.amd_gpu = False
        
    def __repr__(self):
        return f"\nSettings(os={self.os}, CPU={self.info}, Nvidia GPU={self.nvidia_gpu}, AMD GPU?={self.amd_gpu})"
    
    def set_audio_inputs(self):
        if self.os == "Windows":
            audio_device = "Stereo Mix (Realtek(R) Audio)"
            input_format = "dshow"
            return audio_device, input_format
        elif self.os == "Linux":
            audio_device = "alsa_output.pci-0000_00_1b.0.analog-stereo.monitor"
            input_format = "pulse"
            return audio_device, input_format
        raise Exception("Unknown Operating System")

    def set_encoder(self):
        print(self.os)
        
        if self.os == "Windows":
            process = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"]).decode()
            self.amd_gpu = any(keyword in process for keyword in ["AMD", "Radeon"])
        elif self.os == "Linux":
            output = subprocess.check_output("lspci", shell=True).decode()
            self.amd_gpu = any("AMD" in line or "Radeon" in line for line in output.splitlines())

        try:
            if self.nvidia_gpu:
                return "h264_nvenc"
            elif "Intel" in self.info.get("brand_raw", "") and not self.nvidia_gpu:
                return "h264_qsv"
            elif "AMD" in self.info.get("brand_raw", "") or self.amd_gpu:
                return "h264_amf"
            else:
                return "libx264"
        except Exception as e:
            print("Error setting encoder:", e)
            return "libx264"