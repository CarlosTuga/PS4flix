#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Utilitários do Sistema (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
from typing import List

def is_process_running(process_name: str) -> bool:
    """
    Verifica se um determinado processo está ativo no Windows ou Linux.
    """
    if os.name == 'nt' or sys.platform == 'win32':
        try:
            # Chamar tasklist.exe diretamente sem shell=True por motivos de segurança
            result = subprocess.run(
                ['tasklist.exe', '/FI', f'IMAGENAME eq {process_name}'],
                capture_output=True,
                text=True
            )
            return process_name.lower() in result.stdout.lower()
        except Exception:
            return False
    else:
        try:
            base_name = process_name.lower().replace(".exe", "")
            # Usar pgrep no Linux para verificar processo ativo
            result = subprocess.run(
                ['pgrep', '-f', base_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            # Fallback manual em diretórios /proc
            try:
                for pid in os.listdir('/proc'):
                    if pid.isdigit():
                        with open(os.path.join('/proc', pid, 'comm'), 'r', encoding='utf-8', errors='ignore') as f:
                            comm = f.read().strip().lower()
                        if base_name in comm:
                            return True
            except Exception:
                pass
            return False

def sanitize_args(args: List[str]) -> List[str]:
    """
    Remove ou escapa argumentos maliciosos para segurança contra injeções.
    """
    return [str(arg).replace('"', '') for arg in args]
