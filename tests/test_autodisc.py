#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Test Suite
# Versão: 2.0.0
#===============================================================================

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Ensure autodisc package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from autodisc.config import load_yaml, get_main_config, get_profile_config
from autodisc.utils import sanitize_args, is_process_running
from autodisc.notificacion import show_osd_notification
from autodisc.detector_de_consola import identify_console_and_game, read_raw_signatures, read_raw_sectors_linux
from autodisc.detector_de_discos import get_optical_drives, is_disc_ready, is_mounted, mount_drive_linux, umount_drive_linux

# 1. Test Configurations
def test_load_yaml_nonexistent():
    assert load_yaml(Path("nonexistent_file.yaml")) == {}

@patch("autodisc.config.CONFIG_DIR")
def test_get_main_config(mock_config_dir, tmp_path):
    mock_config_dir.return_value = tmp_path
    config_file = tmp_path / "config.yaml"
    config_file.write_text("polling_interval: 5\n", encoding="utf-8")

    with patch("autodisc.config.load_yaml", return_value={"polling_interval": 5}):
        config = get_main_config()
        assert config.get("polling_interval") == 5

# 2. Test Utilities
def test_sanitize_args():
    args = ['--param', 'value"with"quotes', 'safe_val']
    sanitized = sanitize_args(args)
    assert sanitized == ['--param', 'valuewithquotes', 'safe_val']

@patch("subprocess.run")
def test_is_process_running_linux(mock_run):
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_run.return_value = mock_proc

    assert is_process_running("emulationstation") is True
    mock_run.assert_called_with(
        ['pgrep', '-f', 'emulationstation'],
        capture_output=True,
        text=True
    )

# 3. Test Physical & Logic Signatures / Console Detector
@patch("autodisc.detector_de_consola.read_raw_sectors_linux")
def test_read_raw_signatures_saturn(mock_read_linux):
    # Mock Sega Saturn signature in sectors
    mock_read_linux.return_value = b"some prefix SEGA SEGASATURN other data"

    console, label = read_raw_signatures("/dev/sr0")
    assert console == 'saturn'
    assert "Saturn" in label

@patch("autodisc.detector_de_consola.read_raw_sectors_linux")
def test_read_raw_signatures_segacd(mock_read_linux):
    mock_read_linux.return_value = b"some prefix SEGA MEGA_CD other data"

    console, label = read_raw_signatures("/dev/sr0")
    assert console == 'segacd'
    assert "Sega CD" in label

@patch("autodisc.detector_de_consola.read_raw_signatures")
@patch("autodisc.detector_de_discos.mount_drive_linux")
def test_identify_console_and_game_logic_ps2(mock_mount, mock_signatures, tmp_path):
    mock_signatures.return_value = (None, None)
    mock_mount.return_value = True

    # We patch Path internally inside console_detector so it reads from tmp_path instead of /media/cdrom
    with patch("autodisc.detector_de_consola.Path") as mock_path:
        # Create mock SYSTEM.CNF with BOOT2 line
        cnf_file = tmp_path / "SYSTEM.CNF"
        cnf_file.write_text("BOOT2 = cdrom0:\\SLUS_201.23;1", encoding="utf-8")

        mock_path.return_value = tmp_path

        console, label = identify_console_and_game("/dev/sr0")
        assert console == "ps2"
        assert "SLUS-20123" in label

@patch("autodisc.detector_de_consola.read_raw_signatures")
@patch("autodisc.detector_de_discos.mount_drive_linux")
def test_identify_console_and_game_logic_ps1(mock_mount, mock_signatures, tmp_path):
    mock_signatures.return_value = (None, None)
    mock_mount.return_value = True

    with patch("autodisc.detector_de_consola.Path") as mock_path:
        cnf_file = tmp_path / "SYSTEM.CNF"
        cnf_file.write_text("BOOT = cdrom0:\\SCUS_944.44;1", encoding="utf-8")

        mock_path.return_value = tmp_path

        console, label = identify_console_and_game("/dev/sr0")
        assert console == "psx"
        assert "SCUS-94444" in label

# 4. Test Disc Detector
@patch("os.path.exists")
def test_get_optical_drives(mock_exists):
    # Simulate that only /dev/sr0 exists
    mock_exists.side_effect = lambda path: path == "/dev/sr0"

    drives = get_optical_drives()
    assert drives == ["/dev/sr0"]

@patch("fcntl.ioctl")
@patch("os.open")
@patch("os.close")
def test_is_disc_ready(mock_close, mock_open, mock_ioctl):
    mock_open.return_value = 10
    mock_ioctl.return_value = 4  # CDS_DISC_OK

    assert is_disc_ready("/dev/sr0") is True
    mock_ioctl.assert_called_with(10, 0x5326)

@patch("builtins.open", new_callable=mock_open, read_data="/dev/sr0 /media/cdrom iso9660 ro 0 0\n")
def test_is_mounted(mock_file):
    assert is_mounted("/dev/sr0", "/media/cdrom") is True

@patch("subprocess.run")
@patch("os.makedirs")
@patch("autodisc.detector_de_discos.is_mounted")
def test_mount_drive_linux(mock_is_mounted, mock_makedirs, mock_run):
    mock_is_mounted.return_value = False
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_run.return_value = mock_proc

    assert mount_drive_linux("/dev/sr0", "/media/cdrom") is True
    mock_run.assert_called_with(["mount", "-t", "auto", "/dev/sr0", "/media/cdrom"], capture_output=True)

# 5. Test OSD Notifications
@patch("subprocess.Popen")
@patch("shutil.which")
def test_show_osd_notification(mock_which, mock_popen):
    mock_which.return_value = "/usr/bin/osd_cat"
    mock_proc = MagicMock()
    mock_popen.return_value = mock_proc

    show_osd_notification("Hello", "World")
    assert mock_popen.called
