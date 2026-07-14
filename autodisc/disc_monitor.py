#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Daemon de Monitorização (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import time
from threading import Thread
from typing import Optional

from autodisc.registrador import setup_logger
from autodisc.config import get_main_config
from autodisc.detector_de_discos import check_drive_status, umount_drive_linux
from autodisc.detector_de_consola import identify_console_and_game
from autodisc.notificacion import show_osd_notification
from autodisc.disc_launcher import DiscLauncher
from autodisc.utils import is_process_running

class DiscMonitor:
    """
    Serviço daemon em segundo plano que monitoriza inserção de mídias em leitores óticos.
    No Windows, utiliza eventos WMI (Win32_VolumeChangeEvent) para CPU zero em idle.
    No Linux/Batocera, utiliza polling de CPU otimizado de 2 segundos.
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

    def handle_device_event(self, drive_path: str, event_type: int) -> None:
        """
        Callback de manipulação de eventos do Windows (WMI).
        - event_type: 2 = Arrival (Inserção), 3 = Removal (Remoção)
        """
        self.logger.info(f"Evento WMI recebido para '{drive_path}': tipo {event_type}")

        if event_type == 2:  # Inserção
            self.logger.info(f"Estabilizando a leitura física da drive {drive_path} por {self.stabilization_delay}s...")
            time.sleep(self.stabilization_delay)

            console_type, game_label = identify_console_and_game(drive_path)
            if console_type != "unknown":
                self.logger.info(f"Disco físico identificado via WMI: [{console_type}] - [{game_label}]")

                friendly_consoles = {
                    'psx': 'PlayStation 1', 'ps2': 'PlayStation 2', 'ps3': 'PlayStation 3',
                    'segacd': 'Sega CD', 'saturn': 'Sega Saturn', 'dreamcast': 'Sega Dreamcast',
                    'gamecube': 'Nintendo GameCube', 'wii': 'Nintendo Wii',
                    'xbox': 'Xbox Original', 'xbox360': 'Xbox 360', 'psp': 'PSP',
                    'neogeocd': 'NeoGeo CD', 'pcecd': 'PC Engine CD', '3do': '3DO', 'cdi': 'CD-i'
                }
                console_name = friendly_consoles.get(console_type, console_type.upper())
                show_osd_notification(
                    f"🎮 Disco {console_name} Detetado",
                    f"Jogo: {game_label or 'Título Desconhecido'}\nA iniciar emulador..."
                )

                # Chamar lançador de emulador de forma bloqueante
                self.launcher.validate_and_launch(console_type, drive_path)
            else:
                self.logger.warning(f"Disco inserido em {drive_path} não foi identificado via WMI.")
                show_osd_notification("AutoDisc", "Formato de disco inserido não suportado.")

        elif event_type == 3:  # Remoção/Ejeção
            self.logger.info(f"A drive {drive_path} foi ejetada/removida.")

    def monitor_loop_linux(self) -> None:
        """Ciclo principal de monitorização por polling para o Linux/Batocera."""
        self.logger.info("Ciclo de monitorização de mídias por polling ativado (Linux).")

        # 1. Aguardar até que o EmulationStation esteja ativo no Batocera
        es_processes = ["emulationstation", "batocera-es"]
        es_active: bool = False

        while self.running and not es_active:
            if any(is_process_running(p) for p in es_processes):
                es_active = True
                self.logger.info("Interface de jogos detetada como ativa. Iniciando monitorização ótica.")
                break
            else:
                self.logger.info("Aguardando arranque do EmulationStation / Batocera-ES...")
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

                            friendly_consoles = {
                                'psx': 'PlayStation 1', 'ps2': 'PlayStation 2', 'ps3': 'PlayStation 3',
                                'segacd': 'Sega CD', 'saturn': 'Sega Saturn', 'dreamcast': 'Sega Dreamcast',
                                'gamecube': 'Nintendo GameCube', 'wii': 'Nintendo Wii',
                                'xbox': 'Xbox Original', 'xbox360': 'Xbox 360', 'psp': 'PSP',
                                'neogeocd': 'NeoGeo CD', 'pcecd': 'PC Engine CD', '3do': '3DO', 'cdi': 'CD-i'
                            }
                            console_name = friendly_consoles.get(console_type, console_type.upper())
                            show_osd_notification(
                                f"🎮 Disco {console_name} Detetado",
                                f"Jogo: {game_label or 'Título Desconhecido'}\nA iniciar emulador..."
                            )

                            # Chamar lançador de emulador de forma bloqueante
                            self.launcher.validate_and_launch(console_type, drive_path)
                        else:
                            self.logger.warning(f"Disco inserido em {drive_path} não foi identificado.")
                            show_osd_notification("AutoDisc", "Formato de disco inserido não suportado.")

                    elif status == "empty":
                        self.logger.info(f"A drive {drive_path} encontra-se agora vazia.")
                        umount_drive_linux()

                    self.last_status = status

                time.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Erro inesperado no loop de deteção: {e}")
                time.sleep(5)

    def run(self) -> None:
        """Inicia a execução do daemon em background."""
        if os.name == 'nt' or sys.platform == 'win32':
            # Windows: iniciar listener baseado em eventos WMI (CPU zero em idle!)
            self.logger.info("Iniciando monitorização de eventos WMI do Windows (CPU zero em idle)...")
            from autodisc.windows_events import start_wmi_listener

            # Aguardar arranque seguro do RetroBat/EmulationStation no Windows
            es_processes = ["emulationstation.exe", "retrobat.exe"]
            es_active = False
            while self.running and not es_active:
                if any(is_process_running(p) for p in es_processes):
                    es_active = True
                    self.logger.info("RetroBat / EmulationStation detetado como ativo. Ativando escuta WMI.")
                    break
                else:
                    self.logger.info("Aguardando arranque do RetroBat / EmulationStation no Windows...")
                    time.sleep(3)

            start_wmi_listener(self.handle_device_event)
            while self.running:
                time.sleep(1)
        else:
            # Linux/Batocera: iniciar ciclo de polling otimizado
            self.monitor_thread = Thread(target=self.monitor_loop_linux)
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
