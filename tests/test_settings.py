import json, sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest import mock
from core.settings import FFmpegSettings, load_config_path  

def test_load_config_path_existing():
    """Test that load_config_path returns the correct directory when the config file exists."""
    tmp_path = "/tmp/path"
    tmp_config = {"chosen_dir": tmp_path}
    
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(tmp_config))), \
         mock.patch("os.path.exists", return_value=True):
        result = load_config_path()
        assert result == tmp_path

def test_load_config_path_missing():
    """Test that load_config_path defaults to a Videos directory when the config file is missing."""
    with mock.patch("os.path.exists", return_value=False):
        result = load_config_path()
        assert result.endswith("/Videos")

def test_get_operating_system():
    """Test that get_operating_system returns a valid OS name (Windows, Linux, or Darwin)."""
    os_name = FFmpegSettings.get_operating_system()
    assert os_name in ["Windows", "Linux", "Darwin"]

def test_set_audio_inputs_windows():
    """Test that set_audio_inputs returns the correct device and format for Windows."""
    with mock.patch.object(FFmpegSettings, "operating_sys", "Windows"):
        device, fmt = FFmpegSettings.set_audio_inputs()
        assert device == "Stereo Mix (Realtek(R) Audio)"
        assert fmt == "dshow"

def test_set_audio_inputs_linux():
    """Test that set_audio_inputs returns the correct device and format for Linux."""
    with mock.patch.object(FFmpegSettings, "operating_sys", "Linux"):
        device, fmt = FFmpegSettings.set_audio_inputs()
        assert device.endswith(".monitor")
        assert fmt == "pulse"

def test_set_video_inputs_windows():
    """Test that set_video_inputs returns the correct video input and format for Windows."""
    with mock.patch.object(FFmpegSettings, "operating_sys", "Windows"):
        video_input, f_video = FFmpegSettings.set_video_inputs()
        assert video_input == "desktop"
        assert f_video == "gdigrab"

def test_set_video_inputs_linux():
    """Test that set_video_inputs returns the correct video input and format for Linux."""
    with mock.patch.object(FFmpegSettings, "operating_sys", "Linux"):
        video_input, f_video = FFmpegSettings.set_video_inputs()
        assert video_input == ":0.0"
        assert f_video == "x11grab"

def test_set_valid_fps():
    """Test that set_fps correctly sets valid FPS values (30 or 60)."""
    FFmpegSettings.set_fps(30)
    assert FFmpegSettings.fps == 30
    FFmpegSettings.set_fps(60)
    assert FFmpegSettings.fps == 60

def test_set_invalid_fps():
    """Test that set_fps raises a ValueError for invalid FPS values (e.g., 45)."""
    with pytest.raises(ValueError):
        FFmpegSettings.set_fps(45)

def test_set_output_valid_dir():
    """Test that set_output generates a valid output filename and FPS in a valid directory."""
    tmp_dir = "/tmp/output/dir"
    with mock.patch.object(FFmpegSettings, "get_output_directory", return_value=tmp_dir), \
         mock.patch("os.path.isdir", return_value=True):
        filename, fps = FFmpegSettings.set_output()
        assert filename.startswith(tmp_dir)
        assert filename.endswith(".mp4")
        assert fps in (30, 60)