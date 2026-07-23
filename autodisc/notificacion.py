#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Sistema de Notificações (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
import shutil

def show_osd_notification(title: str, message: str) -> None:
    """
    Envia uma notificação Toast no Windows via PowerShell ou OSD no Linux via osd_cat.
    """
    if os.name != 'nt' and sys.platform != 'win32':
        # Linux / Batocera OSD via osd_cat
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
                print(f"[OSD NOTIFICATION] {title} - {message}")
        except Exception:
            pass
        return

    # Windows PowerShell Toast / BalloonTip
    try:
        # Escapar aspas simples duplicando-as no PowerShell para evitar erros de interpolação
        escaped_title = title.replace("'", "''")
        escaped_message = message.replace("'", "''")

        ps_script = f"""
        [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms');
        $notification = New-Object System.Windows.Forms.NotifyIcon;
        $notification.Icon = [System.Drawing.SystemIcons]::Information;
        $notification.BalloonTipIcon = 'Info';
        $notification.BalloonTipTitle = '{escaped_title}';
        $notification.BalloonTipText = '{escaped_message}';
        $notification.Visible = $true;
        $notification.ShowBalloonTip(6000);
        Start-Sleep -Seconds 1;
        $notification.Dispose();
        """

        # Executar PowerShell de forma oculta/silenciosa sem console CMD visível
        subprocess.run(
            ['powershell.exe', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', ps_script],
            capture_output=True,
            creationflags=0x08000000  # CREATE_NO_WINDOW flag
        )
    except Exception:
        pass

def send_windows_toast(title: str, message: str) -> None:
    """
    Mantém compatibilidade com o nome de função anterior.
    """
    show_osd_notification(title, message)
