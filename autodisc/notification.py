#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Sistema de Notificações OSD (Nativa Linux)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
import shutil

def show_osd_notification(title: str, message: str) -> None:
    """
    Envia uma notificação On-Screen Display (OSD) no Batocera Linux via osd_cat.
    Se a ferramenta osd_cat não estiver disponível, faz log/print normal.
    """
    try:
        text = f"{title}\n{message}"
        if shutil.which("osd_cat"):
            cmd = [
                "osd_cat",
                "-f", "-*-*-bold-*-*-*-38-120-*-*-*-*-*-*",
                "-c", "red",
                "-s", "3",
                "-d", "5",
                "-p", "bottom",
                "-A", "center"
            ]
            env = os.environ.copy()
            env["DISPLAY"] = ":0.0"
            env["XAUTHORITY"] = "/var/lib/.Xauthority"
            env["HOME"] = "/userdata/system"

            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, env=env, text=True)
            proc.communicate(input=text)
        else:
            # Fallback para console log
            print(f"[OSD NOTIFICATION] {title} - {message}")
    except Exception:
        pass
