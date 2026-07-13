#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Daemon de Monitorização (Windows)
# Versão: 1.1.0
#===============================================================================

import time
import sys
from threading import Thread
from typing import Optional

from autodisc.logger import setup_logger
from autodisc.config import get_main_config
from autodisc.disc_detector import check_drive_status
from autodisc.console_detector import identify_console_and_game
from autodisc.notification import send_windows_toast
from autodisc.disc_launcher import DiscLauncher
from autodisc.utils import is_process_running

class DiscMonitor:
    """
    Serviço daemon em segundo plano que monitoriza inserção de mídias em leitores óticos no Windows,
    aguarda a inicialização do RetroBat/EmulationStation e executa os jogos.
    """

    def __init__(self) -> None:
        """Inicializa as estruturas de dados e configurações."""
        self.logger = setup_logger("disc_monitor")
        self.config = get_main_config()
        self.running: bool = True
        self.last_status: Optional[str] = None
        self.polling_interval: float = float(self.config.get("polling_interval", 2.0))
        self.stabilization_delay: float = float(self.config.get("timing", {}).get("disc_stabilization", 3.0))
        self.launcher = DiscLauncher()
        self.monitor_thread: Optional[Thread] = None

    def monitor_loop(self) -> None:
        """Ciclo principal de monitorização com polling otimizado de CPU."""
        self.logger.info("Ciclo de monitorização de mídias ativado.")

        # 1. Aguardar até que o RetroBat/EmulationStation esteja ativo no Windows
        es_process: str = "emulationstation.exe"
        es_active: bool = False

        while self.running and not es_active:
            if is_process_running(es_process) or is_process_running("retrobat.exe"):
                es_active = True
                self.logger.info("RetroBat / EmulationStation detetado como ativo. Iniciando monitorização ótica.")
                break
            else:
                self.logger.info("Aguardando arranque do RetroBat / EmulationStation no Windows...")
                time.sleep(3)

        # 2. Loop de deteção e processamento de mídias
        while self.running:
            try:
                drive_path, status = check_drive_status()

                if status != self.last_status:
                    self.logger.info(f"Alteração de estado detetada em '{drive_path}': {self.last_status} -> {status}")

                    if status == "inserted":
                        self.logger.info(f"Estabilizando a leitura física da drive {drive_path} por {self.stabilization_delay}s...")
                        time.sleep(self.stabilization_delay)

                        console_type, game_label = identify_console_and_game(drive_path)
                        if console_type != "unknown":
                            self.logger.info(f"Disco físico identificado: [{console_type}] - [{game_label}]")

                            # Disparar notificação amigável nativa do Windows
                            friendly_consoles = {
                                'psx': 'PlayStation 1', 'ps2': 'PlayStation 2', 'ps3': 'PlayStation 3',
                                'segacd': 'Sega CD', 'saturn': 'Sega Saturn', 'dreamcast': 'Sega Dreamcast',
                                'gamecube': 'Nintendo GameCube', 'wii': 'Nintendo Wii',
                                'xbox': 'Xbox Original', 'xbox360': 'Xbox 360', 'psp': 'PSP'
                            }
                            console_name = friendly_consoles.get(console_type, console_type.upper())
                            send_windows_toast(
                                f"🎮 Disco {console_name} Detetado",
                                f"Jogo: {game_label or 'Título Desconhecido'}\nA iniciar emulador..."
                            )

                            # Chamar lançador de emulador de forma bloqueante
                            self.launcher.validate_and_launch(console_type, drive_path)
                        else:
                            self.logger.warning(f"Disco inserido em {drive_path} não foi identificado.")
                            send_windows_toast("AutoDisc", "Formato de disco inserido não suportado.")

                    elif status == "empty":
                        self.logger.info(f"A drive {drive_path} encontra-se agora vazia.")

                    self.last_status = status

                time.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Erro inesperado no loop de deteção: {e}")
                time.sleep(5)

    def run(self) -> None:
        """Inicia a execução em background do daemon."""
        self.monitor_thread = Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        while self.running:
            time.sleep(1)

def main() -> None:
    """Ponto de entrada do serviço."""
    try:
        monitor = DiscMonitor()
        monitor.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erro Fatal no Daemon: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
