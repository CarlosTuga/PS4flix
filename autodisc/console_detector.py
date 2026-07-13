#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Identificação de Consolas e Discos (Windows)
# Versão: 1.1.0
#===============================================================================

import ctypes
import os
import re
import struct
from pathlib import Path
from typing import Optional, Tuple

def read_raw_sectors_win32(drive_letter: str) -> bytes:
    """
    Efetua a leitura de baixo nível (RAW) diretamente do dispositivo de blocos
    no Windows utilizando a API Win32 CreateFileW/ReadFile.
    Permite ler assinaturas físicas de Saturn, Sega CD e Dreamcast.
    """
    # Converter "D:\" em "\\.\D:"
    clean_letter = drive_letter.rstrip('\\')
    device_name = f"\\\\.\\{clean_letter}"

    # Constantes Win32
    GENERIC_READ: int = 0x80000000
    FILE_SHARE_READ: int = 1
    FILE_SHARE_WRITE: int = 2
    OPEN_EXISTING: int = 3
    INVALID_HANDLE_VALUE: int = -1

    handle = ctypes.windll.kernel32.CreateFileW(
        device_name,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if handle == INVALID_HANDLE_VALUE:
        return b""

    try:
        buffer_size = 36864  # Ler os primeiros 36KB
        buffer = ctypes.create_string_buffer(buffer_size)
        bytes_read = ctypes.c_ulong(0)

        res = ctypes.windll.kernel32.ReadFile(
            handle,
            buffer,
            buffer_size,
            ctypes.byref(bytes_read),
            None
        )
        if res:
            return buffer.raw[:bytes_read.value]
    except Exception:
        pass
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)

    return b""

def read_raw_signatures(drive_letter: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Analisa assinaturas físicas cruas do disco no Windows.
    """
    header = read_raw_sectors_win32(drive_letter)
    if not header:
        return None, None

    # Sega Saturn
    if b"SEGA SEGASATURN" in header:
        return 'saturn', "Jogo de Sega Saturn"

    # Sega CD / Mega CD
    if b"SEGA MEGA_CD" in header or b"SEGA MEGADRIVE" in header:
        return 'segacd', "Jogo de Sega CD"

    # Sega Dreamcast
    if b"SEGA SECURED" in header or b"SEGA ENTERPRISES" in header or b"1ST_READ.BIN" in header:
        return 'dreamcast', "Jogo de Sega Dreamcast"

    return None, None

def extract_ps3_title(sfo_path: Path) -> str:
    """
    Parser de ficheiros PARAM.SFO (Sony Index File) do PS3.
    """
    try:
        if sfo_path.exists():
            with open(sfo_path, 'rb') as f:
                data = f.read()

            if data[:4] == b'\x00PSF':
                key_table_start, data_table_start, index_count = struct.unpack('<III', data[8:20])
                for i in range(index_count):
                    offset = 20 + i * 16
                    key_offset, _, _, _, data_offset = struct.unpack('<HHIII', data[offset:offset+16])

                    key_pos = key_table_start + key_offset
                    key_end = data.find(b'\x00', key_pos)
                    key = data[key_pos:key_end].decode('utf-8', errors='ignore')

                    if key == 'TITLE':
                        val_pos = data_table_start + data_offset
                        val_end = data.find(b'\x00', val_pos)
                        val = data[val_pos:val_end].decode('utf-8', errors='ignore')
                        return val.replace('\n', ' ').strip()
    except Exception:
        pass
    return "Jogo de PlayStation 3"

def identify_console_and_game(drive_path: str) -> Tuple[str, Optional[str]]:
    """
    Identifica de forma precisa o tipo de consola do disco inserido na drive Windows.
    """
    # 1. Tentar leitura de assinaturas de baixo nível via Win32 API
    console, game_title = read_raw_signatures(drive_path)
    if console:
        return console, game_title

    # 2. Tentar leitura lógica de ficheiros no sistema de ficheiros montado pelo Windows
    try:
        drive_root = Path(drive_path)

        # A) PlayStation 3
        ps3_dir = drive_root / "PS3_GAME"
        if ps3_dir.exists():
            title = "Jogo de PlayStation 3"
            sfo_file = ps3_dir / "PARAM.SFO"
            if sfo_file.exists():
                title = extract_ps3_title(sfo_file)
            return "ps3", title

        # B) PlayStation 1 / PlayStation 2 (SYSTEM.CNF)
        for cnf_name in ["SYSTEM.CNF", "system.cnf", "System.cnf"]:
            cnf_file = drive_root / cnf_name
            if cnf_file.exists():
                with open(cnf_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                is_ps2 = False
                boot_line = None
                for line in content.split('\n'):
                    if 'BOOT2' in line.upper():
                        is_ps2 = True
                        boot_line = line
                        break
                    elif 'BOOT' in line.upper() and not boot_line:
                        boot_line = line

                game_id = "Jogo Desconhecido"
                if boot_line:
                    match = re.search(r'([A-Z]{3,4})_([0-9]{3})\.([0-9]{2})', boot_line.upper())
                    if match:
                        game_id = f"{match.group(1)}-{match.group(2)}{match.group(3)}"

                if is_ps2:
                    return "ps2", f"PS2 ID: {game_id}"
                else:
                    return "psx", f"PSX ID: {game_id}"

        # C) Xbox Original (default.xbe)
        for xbe in ["default.xbe", "DEFAULT.XBE", "Default.xbe"]:
            if (drive_root / xbe).exists():
                return "xbox", "Jogo de Xbox Clássica"

        # D) Xbox 360 (default.xex)
        for xex in ["default.xex", "DEFAULT.XEX", "Default.xex"]:
            if (drive_root / xex).exists():
                return "xbox360", "Jogo de Xbox 360"

        # E) GameCube / Wii (opening.bnr ou sys/boot.bin)
        if (drive_root / "sys" / "boot.bin").exists() or (drive_root / "opening.bnr").exists():
            is_wii = (drive_root / "sys" / "main.dol").exists() or (drive_root / "ticket").exists()
            if is_wii:
                return "wii", "Jogo de Nintendo Wii"
            else:
                return "gamecube", "Jogo de Nintendo GameCube"

    except Exception:
        pass

    return "unknown", None
