#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Deteção Física de Drives Óticas (Windows)
# Versão: 1.1.0
#===============================================================================

import ctypes
import os
from typing import List, Tuple

# Constantes de tipos de discos do Windows API
DRIVE_CDROM: int = 5

def get_logical_drives() -> List[str]:
    """
    Retorna uma lista com todas as letras de drives lógicas ativas no Windows.
    Utiliza GetLogicalDriveStringsW da API kernel32.
    """
    drives: List[str] = []
    try:
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
    Filtra as letras de drive ativas e retorna apenas as do tipo DRIVE_CDROM (Leitores óticos).
    """
    optical_drives: List[str] = []
    try:
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
    try:
        # Tentar abrir e ler uma diretoria para verificar se a média física está legível
        # No Windows, se o leitor estiver vazio, levantar-se-á uma exceção de IO ou permissão imediata
        os.listdir(drive_path)
        return True
    except Exception:
        return False

def check_drive_status() -> Tuple[str, str]:
    """
    Varre dinamicamente todos os leitores óticos no Windows.
    Retorna a letra da drive ótica ativa (com disco) e o estado correspondente.

    Returns:
        Tuple[str, str]: Par contendo (caminho_da_drive, estado) onde estado é 'inserted' ou 'empty'.
    """
    drives = get_optical_drives()

    if not drives:
        return "D:\\", "empty"

    for drive in drives:
        if is_disc_ready(drive):
            return drive, "inserted"

    # Retorna o primeiro leitor detetado como padrão se estiver tudo vazio
    return drives[0], "empty"
