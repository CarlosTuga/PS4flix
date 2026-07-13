#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Deteção Física de Drives Óticas (Nativa Linux)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import fcntl
import subprocess
from typing import List, Tuple

def get_optical_drives() -> List[str]:
    """
    Retorna uma lista com os caminhos dos leitores óticos físicos ativos no Linux.
    Normalmente, detecta /dev/sr0, /dev/sr1, etc.
    """
    optical_drives: List[str] = []
    # Procurar por /dev/sr0 até /dev/sr3
    for i in range(4):
        dev_path = f"/dev/sr{i}"
        if os.path.exists(dev_path):
            optical_drives.append(dev_path)

    # Adicionar o link simbólico padrão caso exista e não esteja listado
    if not optical_drives and os.path.exists("/dev/cdrom"):
        optical_drives.append("/dev/cdrom")

    return optical_drives

def is_disc_ready(drive_path: str) -> bool:
    """
    Verifica se existe um disco inserido e pronto para leitura na drive ótica.
    Utiliza ioctl com o código CDROM_DRIVE_STATUS (0x5326) do Linux.
    """
    try:
        fd = os.open(drive_path, os.O_RDONLY | os.O_NONBLOCK)
        # 0x5326 é CDROM_DRIVE_STATUS na API de cdrom do Linux
        rv = fcntl.ioctl(fd, 0x5326)
        os.close(fd)
        # rv == 4 significa CDS_DISC_OK (disco pronto para leitura na drive)
        return rv == 4
    except Exception:
        return False

def is_mounted(drive_path: str, mount_point: str = "/media/cdrom") -> bool:
    """
    Verifica se o leitor ótico ou o ponto de montagem já constam como montados no Linux.
    """
    try:
        with open("/proc/mounts", "r", encoding="utf-8", errors="ignore") as f:
            mounts = f.read()
        return mount_point in mounts or drive_path in mounts
    except Exception:
        return False

def mount_drive_linux(drive_path: str, mount_point: str = "/media/cdrom") -> bool:
    """
    Monta de forma nativa o dispositivo ótico no ponto de montagem pretendido.
    """
    try:
        os.makedirs(mount_point, exist_ok=True)
        if is_mounted(drive_path, mount_point):
            return True
        # Executar mount com deteção automática do sistema de ficheiros (-t auto)
        res = subprocess.run(["mount", "-t", "auto", drive_path, mount_point], capture_output=True)
        return res.returncode == 0
    except Exception:
        return False

def umount_drive_linux(mount_point: str = "/media/cdrom") -> bool:
    """
    Desmonta de forma preguiçosa (lazy) e segura o ponto de montagem.
    """
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

    Returns:
        Tuple[str, str]: Par contendo (caminho_da_drive, estado) onde estado é 'inserted' o 'empty'.
    """
    drives = get_optical_drives()

    if not drives:
        return "/dev/sr0", "empty"

    for drive in drives:
        if is_disc_ready(drive):
            return drive, "inserted"

    return drives[0], "empty"
