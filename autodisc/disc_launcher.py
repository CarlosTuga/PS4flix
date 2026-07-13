#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Lançador de Emuladores (Nativa Linux)
# Versão: 2.0.0
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
    Coordena o lançamento de emuladores e cores no Batocera Linux passando
    os caminhos dos dispositivos óticos físicos (/dev/sr*) ou pontos de montagem.
    """

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        """Inicializa o logger."""
        self.logger = setup_logger("disc_launcher", log_dir)
        self.config = get_main_config()

    def build_command_linux(self, console_type: str, emulator_name: str, exec_path: Path, drive_path: str, profile: Dict[str, Any]) -> List[str]:
        """
        Formata os argumentos de linha de comando corretos para emuladores Linux standalone.
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
                # Caminhos de cores padrão no Batocera
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
        Valida o estado da drive e executa o emulador utilizando o launcher nativo do Batocera
        ou executando diretamente os binários standalone em /usr/bin.
        """
        # 1. Validar a existência do dispositivo ótico físico
        if not os.path.exists(drive_path):
            self.logger.error(f"Dispositivo ótico '{drive_path}' não está acessível no sistema.")
            return False

        # 2. Se o gestor de lançamentos do Batocera existir, priorizamos a sua utilização
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
                self.logger.info(f"Sessão de jogo ativa via emulatorlauncher (PID: {process.pid}). Aguardando conclusão...")
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    self.logger.info("Sessão de jogo concluída com sucesso via emulatorlauncher.")
                    return True
                else:
                    self.logger.error(f"O emulatorlauncher terminou com erro: {stderr}")
                    return False
            except Exception as e:
                self.logger.error(f"Falha crítica ao executar emulatorlauncher: {e}")
                return False

        # 3. Caso contrário, fazemos a execução direta do binário standalone mapeado no perfil YAML
        profile = get_profile_config(console_type)
        if not profile:
            self.logger.error(f"Perfil de configuração para {console_type} não foi encontrado.")
            return False

        emulator_name = profile.get("emulator")
        if not emulator_name:
            self.logger.error(f"Emulador não especificado no perfil para {console_type}.")
            return False

        # Resolver o caminho do binário nativo no Batocera
        exec_name = emulator_name
        if emulator_name == "pcsx2":
            exec_name = "pcsx2-qt" if os.path.exists("/usr/bin/pcsx2-qt") else "pcsx2"
        elif emulator_name == "dolphin":
            exec_name = "dolphin-emu"

        exec_path = Path(f"/usr/bin/{exec_name}")

        # Validar executável standalone
        if not exec_path.exists():
            self.logger.error(f"Executável do emulador não encontrado em: {exec_path}")
            return False

        # Construir comando
        cmd = self.build_command_linux(console_type, emulator_name, exec_path, drive_path, profile)
        self.logger.info(f"Iniciando emulador standalone {exec_name} para {console_type} via comando: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
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
            self.logger.error(f"Erro inesperado ao instanciar o processo do emulador: {e}")
            return False
