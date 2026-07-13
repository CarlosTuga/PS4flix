#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Identificação de Consolas e Discos (Nativa Linux)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import re
import struct
from pathlib import Path
from typing import Optional, Tuple

def read_raw_sectors_linux(drive_path: str) -> bytes:
    """
    Efetua a leitura de baixo nível (RAW) diretamente do dispositivo de blocos
    no Linux, abrindo o dispositivo (/dev/sr0) em modo binário de leitura.
    Garante ler as assinaturas físicas dos primeiros 36KB do disco.
    """
    try:
        with open(drive_path, 'rb') as f:
            return f.read(36864)  # Ler os primeiros 36KB
    except Exception:
        return b""

def read_raw_signatures(drive_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Analisa assinaturas físicas e cruas do disco no Linux para sistemas clássicos
    que usam formatos híbridos ou proprietários de faixas de dados/áudio.
    """
    header = read_raw_sectors_linux(drive_path)
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

    # 3DO Interactive Multiplayer
    if b"3DO" in header or b"OPERATOR" in header:
        return '3do', "Jogo de 3DO"

    # CD-i (Philips)
    if b"CD-RTOS" in header:
        return 'cdi', "Jogo de CD-i"

    # NeoGeo CD
    if b"NEO-GEO" in header or b"SNK" in header:
        return 'neogeocd', "Jogo de NeoGeo CD"

    # PC Engine CD / TurboGrafx CD
    if b"PC Engine" in header or b"PC-Engine" in header or b"HUDSON" in header:
        return 'pcecd', "Jogo de PC Engine CD"

    return None, None

def extract_ps3_title(sfo_path: Path) -> str:
    """
    Parser robusto de ficheiros PARAM.SFO (Sony Index File) do PS3.
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
    Identifica com precisão de baixo nível e lógica a consola correspondente ao disco.
    """
    # 1. Tentar leitura física de assinaturas cruas do sector de arranque
    console, game_title = read_raw_signatures(drive_path)
    if console:
        return console, game_title

    # 2. Tentar leitura lógica de ficheiros montados
    try:
        # Garantir montagem ativa no Linux antes de ler o sistema de ficheiros
        from autodisc.disc_detector import mount_drive_linux
        mount_point = "/media/cdrom"
        mount_drive_linux(drive_path, mount_point)
        drive_root = Path(mount_point)

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

        # F) NeoGeo CD (IPL.TXT)
        for ipl in ["IPL.TXT", "ipl.txt", "Ipl.txt"]:
            if (drive_root / ipl).exists():
                return "neogeocd", "Jogo de NeoGeo CD"

    except Exception:
        pass

    return "unknown", None
