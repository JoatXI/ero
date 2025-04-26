import json, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest import mock
from core import automate
import psutil

def test_load_config_apps_file_exists():
    """Test that load_config_apps returns app names from config file when it exists."""
    mock_config = {
        "app1": "notepad",
        "app2": "firefox",
        "automate": "some_value"
    }
    with mock.patch("os.path.exists", return_value=True), \
         mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_config))):
        result = automate.load_config_apps()
        assert result == ["notepad", "firefox"]

def test_load_config_apps_file_missing():
    """Test that load_config_apps returns an empty list when config file is missing."""
    with mock.patch("os.path.exists", return_value=False):
        result = automate.load_config_apps()
        assert result == []

def test_running_procresses_app_found():
    """Test that running_procresses returns True when a tracked app is running."""
    mock_apps = ["firefox.exe"]
    mock_process_iter = [
        mock.Mock(info={"name": "firefox.exe"}),
        mock.Mock(info={"name": "chrome.exe"})
    ]
    with mock.patch("core.automate.load_config_apps", return_value=mock_apps), \
         mock.patch("psutil.process_iter", return_value=mock_process_iter):
        result = automate.running_procresses()
        assert result is True

def test_running_procresses_app_not_found():
    """Test that running_procresses returns False when no tracked app is running."""
    mock_apps = ["firefox.exe"]
    mock_process_iter = [
        mock.Mock(info={"name": "chrome.exe"}),
        mock.Mock(info={"name": "notepad.exe"})
    ]
    with mock.patch("core.automate.load_config_apps", return_value=mock_apps), \
         mock.patch("psutil.process_iter", return_value=mock_process_iter):
        result = automate.running_procresses()
        assert result is False

def test_running_procresses_access_denied():
    """Test that running_procresses handles AccessDenied exceptions gracefully."""
    mock_apps = ["firefox"]
    mock_process_iter = [
        mock.Mock(info={"name": "firefox.exe"})
    ]
    with mock.patch("core.automate.load_config_apps", return_value=mock_apps), \
         mock.patch("psutil.process_iter", return_value=mock_process_iter), \
         mock.patch.object(mock_process_iter[0], "info", side_effect=psutil.AccessDenied):
        result = automate.running_procresses()
        assert result is False

def test_system_notification():
    """Test that system_notification calls notification.notify with correct arguments."""
    with mock.patch("plyer.notification.notify") as mock_notify:
        automate.system_notification("Test Title", "Test Message")
        mock_notify.assert_called_once_with(
            title="Test Title",
            message="Test Message",
            app_icon="assets/icon.ico",
            timeout=5
        )