#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Lançador de Emuladores (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from autodisc.registrador import setup_logger
from autodisc.config import get_main_config, get_profile_config

class DiscLauncher:
    """
    Coordena o lançamento de emuladores e cores no Windows (RetroBat) e Linux (Batocera)
    passando os caminhos dos dispositivos óticos físicos ou letras de drive.
    """

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        """Inicializa o logger."""
        self.logger = setup_logger("disc_launcher", log_dir)
        self.config = get_main_config()
        self.retrobat_path = Path(self.config.get("retrobat_path", "C:\\RetroBat"))

    def build_command(self, console_type: str, emulator_name: str, exec_path: Path, drive_path: str, profile: Dict[str, Any]) -> List[str]:
        """
        Formata os argumentos de linha de comando corretos para cada emulador em Windows.
        """
        exec_str = str(exec_path)

        # PlayStation 1 (DuckStation)
        if emulator_name == "duckstation":
            return [exec_str, "-fullscreen", "-batch", "-fastboot", "-disc", drive_path]

        # PlayStation 2 (PCSX2)
        if emulator_name == "pcsx2":
            cmd = [exec_str, "--nogui", "--fullscreen"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("renderer", "vulkan") == "vulkan":
                cmd.extend(["--renderer", "vulkan"])
            cmd.extend(["--disc", drive_path])
            return cmd

        # GameCube / Wii (Dolphin)
        if emulator_name == "dolphin":
            cmd = [exec_str, "-e", drive_path, "-f"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("backend", "vulkan") == "vulkan":
                cmd.extend(["-v", "vulkan"])
            return cmd

        # Sega Dreamcast (Flycast / Redream)
        if emulator_name in ["flycast", "redream"]:
            return [exec_str, "--fullscreen", "--disc", drive_path]

        # PlayStation 3 (RPCS3)
        if emulator_name == "rpcs3":
            return [exec_str, "--no-gui", "--fullscreen", "--play", drive_path]

        # Xbox Original (Xemu)
        if emulator_name == "xemu":
            return [exec_str, "-full-screen", "-dvd_path", drive_path]

        # RetroArch (Sega CD / Saturn / PCE-CD / NeoGeo CD)
        if emulator_name == "retroarch":
            cmd = [exec_str, "-F"]  # Fullscreen
            core_name = profile.get("core")
            if core_name:
                core_path = self.retrobat_path / "cores" / core_name
                cmd.extend(["-L", str(core_path)])
            cmd.append(drive_path)
            return cmd

        # Fallback padrão
        return [exec_str, drive_path]

    def build_command_linux(self, console_type: str, emulator_name: str, exec_path: Path, drive_path: str, profile: Dict[str, Any]) -> List[str]:
        """
        Formata os argumentos de linha de comando corretos para cada emulador em Linux.
        """
        exec_str = str(exec_path)

        # PlayStation 1 (DuckStation)
        if emulator_name == "duckstation":
            return [exec_str, "-fullscreen", "-batch", "-fastboot", "-disc", drive_path]

        # PlayStation 2 (PCSX2)
        if emulator_name == "pcsx2":
            cmd = [exec_str, "--nogui", "--fullscreen"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("renderer", "vulkan") == "vulkan":
                cmd.extend(["--renderer", "vulkan"])
            cmd.extend(["--disc", drive_path])
            return cmd

        # GameCube / Wii (Dolphin)
        if emulator_name == "dolphin":
            cmd = [exec_str, "-e", drive_path, "-f"]
            video_cfg = profile.get("video", {})
            if video_cfg.get("backend", "vulkan") == "vulkan":
                cmd.extend(["-v", "vulkan"])
            return cmd

        # Sega Dreamcast (Flycast / Redream)
        if emulator_name in ["flycast", "redream"]:
            return [exec_str, "--fullscreen", "--disc", drive_path]

        # PlayStation 3 (RPCS3)
        if emulator_name == "rpcs3":
            return [exec_str, "--no-gui", "--fullscreen", "--play", drive_path]

        # Xbox Original (Xemu)
        if emulator_name == "xemu":
            return [exec_str, "-full-screen", "-dvd_path", drive_path]

        # RetroArch (Sega CD / Saturn / PCE-CD / NeoGeo CD)
        if emulator_name == "retroarch":
            cmd = [exec_str, "-F"]  # Fullscreen
            core_name = profile.get("core")
            if core_name:
                core_name_linux = core_name.replace(".dll", ".so")
                possible_paths = [
                    Path("/usr/lib/libretro") / core_name_linux,
                    Path("/usr/lib/retroarch/cores") / core_name_linux,
                ]
                core_path = possible_paths[0]
                for p in possible_paths:
                    if p.exists():
                        core_path = p
                        break
                cmd.extend(["-L", str(core_path)])
            cmd.append(drive_path)
            return cmd

        # Fallback padrão
        return [exec_str, drive_path]

    def validate_and_launch(self, console_type: str, drive_path: str) -> bool:
        """
        Valida o estado da drive e executa o emulador utilizando caminhos dinâmicos de SO.
        """
        if not os.path.exists(drive_path):
            self.logger.error(f"Drive ou leitor ótico '{drive_path}' não está acessível.")
            return False

        # 1. Se estivermos no Linux e o emulatorlauncher oficial do Batocera existir, damos-lhe prioridade
        if os.name != 'nt' and sys.platform != 'win32':
            if os.path.exists("/usr/bin/emulatorlauncher"):
                cmd = ["/usr/bin/emulatorlauncher", "-system", console_type, "-rom", drive_path]
                self.logger.info(f"Iniciando emulador via Batocera emulatorlauncher: {' '.join(cmd)}")
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    self.logger.info(f"Sessão de jogo activa via emulatorlauncher (PID: {process.pid}). Aguardando...")
                    stdout, stderr = process.communicate()
                    return process.returncode == 0
                except Exception as e:
                    self.logger.error(f"Falha ao executar emulatorlauncher no Batocera: {e}")
                    return False

        # 2. Carregar as configurações de perfil específicas da consola
        profile = get_profile_config(console_type)
        if not profile:
            self.logger.error(f"Perfil de configuração para {console_type} não foi encontrado.")
            return False

        emulator_name = profile.get("emulator")
        relative_exec = profile.get("executable")

        if not emulator_name or not relative_exec:
            self.logger.error(f"Propriedades de emulador/executável incompletas para {console_type}.")
            return False

        # Resolver o caminho do binário baseado no Sistema Operativo
        if os.name == 'nt' or sys.platform == 'win32':
            exec_path = self.retrobat_path / relative_exec
            cmd = self.build_command(console_type, emulator_name, exec_path, drive_path, profile)
            creation_flags = 0x08000000  # CREATE_NO_WINDOW
        else:
            exec_name = emulator_name
            if emulator_name == "pcsx2":
                exec_name = "pcsx2-qt" if os.path.exists("/usr/bin/pcsx2-qt") else "pcsx2"
            elif emulator_name == "dolphin":
                exec_name = "dolphin-emu"
            exec_path = Path(f"/usr/bin/{exec_name}")
            cmd = self.build_command_linux(console_type, emulator_name, exec_path, drive_path, profile)
            creation_flags = 0

        # Validar existência do emulador
        if not exec_path.exists():
            self.logger.error(f"Executável do emulador não encontrado em: {exec_path}")
            return False

        self.logger.info(f"Iniciando emulador {emulator_name} para {console_type} via comando: {' '.join(cmd)}")

        try:
            # Executar de forma síncrona/bloqueante
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )

            self.logger.info(f"Sessão de jogo activa (PID: {process.pid}). Aguardando conclusão...")
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
