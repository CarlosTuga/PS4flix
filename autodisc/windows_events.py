#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Monitorização de Eventos WMI (Windows)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import threading
from typing import Callable

# Apenas importar e utilizar win32com no Windows
HAS_WIN32: bool = False
if os.name == 'nt' or sys.platform == 'win32':
    try:
        import pythoncom
        import win32com.client
        HAS_WIN32 = True
    except ImportError:
        pass

def start_wmi_listener(callback: Callable[[str, int], None]) -> None:
    """
    Inicia o escutador de eventos WMI do Windows em segundo plano.
    Chama callback(drive_letter, event_type) quando ocorre inserção ou remoção.
    - event_type: 2 = Arrival (Inserção), 3 = Removal (Ejeção/Remoção)
    """
    if not HAS_WIN32:
        return

    def run_listener():
        # Inicializar COM para a thread de segundo plano
        pythoncom.CoInitialize()
        try:
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            server = wmi.ConnectServer(".", "root\\cimv2")

            # Win32_VolumeChangeEvent capta inserções e rejeições instantaneamente com zero de CPU idle!
            watcher = server.ExecNotificationQuery(
                "SELECT * FROM Win32_VolumeChangeEvent"
            )

            while True:
                # Bloqueia até que ocorra um evento de hardware no Windows
                event = watcher.NextEvent()
                drive_name = getattr(event, "DriveName", "")
                event_type = getattr(event, "EventType", 0)

                # EventType: 2 = Arrival, 3 = Removal
                if drive_name and event_type in [2, 3]:
                    # Adicionar contrabarra para ficar no formato de caminho (ex: "D:\")
                    drive_path = f"{drive_name}\\"
                    callback(drive_path, event_type)
        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()

    thread = threading.Thread(target=run_listener, daemon=True)
    thread.start()
