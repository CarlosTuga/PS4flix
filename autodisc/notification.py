#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Sistema de Notificações nativas do Windows
# Versão: 1.1.0
#===============================================================================

import subprocess

def send_windows_toast(title: str, message: str) -> None:
    """
    Envia uma notificação Toast (balão de alerta) nativa do Windows 10/11
    utilizando um script PowerShell inline rápido e sem dependências externas.
    Evita interpolação indesejada de variáveis escapando aspas simples.
    """
    try:
        # Escapar aspas simples duplicando-as no PowerShell para evitar injeções ou erros de interpolação
        escaped_title = title.replace("'", "''")
        escaped_message = message.replace("'", "''")

        # Script PowerShell para criar ícone de notificação e disparar BalloonTip
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
