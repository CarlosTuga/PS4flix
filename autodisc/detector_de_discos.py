#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Deteção Física de Drives Óticas (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
from typing import List, Tuple

# Constantes de tipos de discos do Windows API
DRIVE_CDROM: int = 5

def get_logical_drives() -> List[str]:
    """
    Retorna uma lista com todas as letras de drives lógicas ativas no Windows.
    Utiliza GetLogicalDriveStringsW da API kernel32.
    """
    if os.name != 'nt' and sys.platform != 'win32':
        return get_optical_drives()

    drives: List[str] = []
    try:
        import ctypes
        buffer_len = 512
        buffer = ctypes.create_unicode_buffer(buffer_len)
        result = ctypes.windll.kernel32.GetLogicalDriveStringsW(buffer_len, buffer)

        if result > 0 and result <= buffer_len:
            # As letras das drives vêm separadas por bytes nulos (ex: "C:\x00D:\x00")
            raw_drives = buffer.value
            current = ""
            for char in buffer:
                if char == '\x00':
                    if current:
                        drives.append(current)
                        current = ""
                else:
                    current += char
    except Exception:
        # Fallback genérico caso falhe ctypes
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            if os.path.exists(path):
                drives.append(path)

    return drives

def get_optical_drives() -> List[str]:
    """
    Retorna os leitores óticos físicos do sistema (DRIVE_CDROM no Windows ou /dev/sr* no Linux).
    """
    if os.name != 'nt' and sys.platform != 'win32':
        # Linux
        optical_drives: List[str] = []
        for i in range(4):
            dev_path = f"/dev/sr{i}"
            if os.path.exists(dev_path):
                optical_drives.append(dev_path)
        if not optical_drives and os.path.exists("/dev/cdrom"):
            optical_drives.append("/dev/cdrom")
        return optical_drives

    # Windows
    optical_drives: List[str] = []
    try:
        import ctypes
        for drive in get_logical_drives():
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            if drive_type == DRIVE_CDROM:
                optical_drives.append(drive)
    except Exception:
        pass
    return optical_drives

def is_disc_ready(drive_path: str) -> bool:
    """
    Verifica se existe um disco inserido e pronto para leitura na drive ótica.
    """
    if os.name != 'nt' and sys.platform != 'win32':
        # Linux via ioctl (CDROM_DRIVE_STATUS = 0x5326)
        try:
            import fcntl
            fd = os.open(drive_path, os.O_RDONLY | os.O_NONBLOCK)
            rv = fcntl.ioctl(fd, 0x5326)
            os.close(fd)
            # rv == 4 significa CDS_DISC_OK
            return rv == 4
        except Exception:
            return False

    # Windows
    try:
        os.listdir(drive_path)
        return True
    except Exception:
        return False

def is_mounted(drive_path: str, mount_point: str = "/media/cdrom") -> bool:
    """
    Verifica se o ponto de montagem está ativo no Linux.
    """
    if os.name == 'nt' or sys.platform == 'win32':
        return True
    try:
        with open("/proc/mounts", "r", encoding="utf-8", errors="ignore") as f:
            mounts = f.read()
        return mount_point in mounts or drive_path in mounts
    except Exception:
        return False

def mount_drive_linux(drive_path: str, mount_point: str = "/media/cdrom") -> bool:
    """
    Monta de forma nativa o dispositivo ótico no Linux.
    """
    if os.name == 'nt' or sys.platform == 'win32':
        return True
    try:
        os.makedirs(mount_point, exist_ok=True)
        if is_mounted(drive_path, mount_point):
            return True
        res = subprocess.run(["mount", "-t", "auto", drive_path, mount_point], capture_output=True)
        return res.returncode == 0
    except Exception:
        return False

def umount_drive_linux(mount_point: str = "/media/cdrom") -> bool:
    """
    Desmonta de forma preguiçosa (lazy) e segura o ponto de montagem no Linux.
    """
    if os.name == 'nt' or sys.platform == 'win32':
        return True
    try:
        if os.path.exists(mount_point):
            res = subprocess.run(["umount", "-l", mount_point], capture_output=True)
            return res.returncode == 0
    except Exception:
        pass
    return False

def check_drive_status() -> Tuple[str, str]:
    """
    Varre dinamicamente todos os leitores óticos no sistema.
    Retorna o caminho do leitor ótico ativo (com disco) e o estado correspondente.
    """
    drives = get_optical_drives()

    if not drives:
        default_drive = "D:\\" if (os.name == 'nt' or sys.platform == 'win32') else "/dev/sr0"
        return default_drive, "empty"

    for drive in drives:
        if is_disc_ready(drive):
            return drive, "inserted"

    return drives[0], "empty"
