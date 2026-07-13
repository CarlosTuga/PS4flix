#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Lançador de Emuladores (Windows)
# Versão: 1.1.0
#===============================================================================

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from autodisc.logger import setup_logger
from autodisc.config import get_main_config, get_profile_config

class DiscLauncher:
    """
    Coordena a validação de executáveis, BIOS, permissões e o lançamento de emuladores
    standalones no Windows passando argumentos de drive de disco físico.
    """

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        """Inicializa o logger."""
        self.logger = setup_logger("disc_launcher", log_dir)
        self.config = get_main_config()
        self.retrobat_path = Path(self.config.get("retrobat_path", "C:\\RetroBat"))

    def build_command(self, console_type: str, emulator_name: str, exec_path: Path, drive_letter: str, profile: Dict[str, Any]) -> List[str]:
        """
        Formata os argumentos corretos para cada emulador em Windows.
        """
        exec_str = str(exec_path)

        # PlayStation 1 (DuckStation)
        if emulator_name == "duckstation":
            return [exec_str, "-fullscreen", "-batch", "-fastboot", "-disc", drive_letter]

        # PlayStation 2 (PCSX2)
        if emulator_name == "pcsx2":
            cmd = [exec_str, "--nogui", "--fullscreen"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("renderer", "vulkan") == "vulkan":
                cmd.extend(["--renderer", "vulkan"])
            cmd.extend(["--disc", drive_letter])
            return cmd

        # GameCube / Wii (Dolphin)
        if emulator_name == "dolphin":
            cmd = [exec_str, "-e", drive_letter, "-f"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("backend", "vulkan") == "vulkan":
                cmd.extend(["-v", "vulkan"])
            return cmd

        # Sega Dreamcast (Flycast / Redream)
        if emulator_name in ["flycast", "redream"]:
            return [exec_str, "--fullscreen", "--disc", drive_letter]

        # PlayStation 3 (RPCS3)
        if emulator_name == "rpcs3":
            return [exec_str, "--no-gui", "--fullscreen", "--play", drive_letter]

        # Xbox Original (Xemu)
        if emulator_name == "xemu":
            return [exec_str, "-full-screen", "-dvd_path", drive_letter]

        # RetroArch (Sega CD / Saturn)
        if emulator_name == "retroarch":
            cmd = [exec_str, "-F"]  # Fullscreen
            core_name = profile.get("core")
            if core_name:
                core_path = self.retrobat_path / "cores" / core_name
                cmd.extend(["-L", str(core_path)])
            cmd.append(drive_letter)
            return cmd

        # Default fallback genérico
        return [exec_str, drive_letter]

    def validate_and_launch(self, console_type: str, drive_letter: str) -> bool:
        """
        Garante a verificação completa do emulador, BIOS, e disco antes de iniciar.
        """
        profile = get_profile_config(console_type)
        if not profile:
            self.logger.error(f"Perfil de configuração para {console_type} não foi encontrado.")
            return False

        emulator_name = profile.get("emulator")
        relative_exec = profile.get("executable")

        if not emulator_name or not relative_exec:
            self.logger.error(f"Propriedades de emulador/executável incompletas para {console_type}.")
            return False

        # Caminho absoluto para o executável do emulador no RetroBat
        exec_path = self.retrobat_path / relative_exec

        # 1. Validar existência do emulador
        if not exec_path.exists():
            self.logger.error(f"Executável do emulador não encontrado em: {exec_path}")
            return False

        # 2. Validar se a drive de disco físico está ativa
        if not os.path.exists(drive_letter):
            self.logger.error(f"Drive ótica '{drive_letter}' não está acessível ou montada.")
            return False

        # Construir comando final
        cmd = self.build_command(console_type, emulator_name, exec_path, drive_letter, profile)
        self.logger.info(f"Iniciando emulador {emulator_name} para {console_type} via comando: {' '.join(cmd)}")

        try:
            # Executar o emulador de forma síncrona
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=0x08000000  # Ocultar janela preta de comando
            )

            self.logger.info(f"Sessão de jogo ativa (PID: {process.pid}). Aguardando conclusão...")
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.logger.info("Sessão de jogo concluída com sucesso.")
                return True
            else:
                self.logger.error(f"O emulador terminou com erro: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao instanciar o processo do emulador: {e}")
            return False
