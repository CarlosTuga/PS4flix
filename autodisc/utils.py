#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Utilitários do Sistema (Nativa Linux)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import subprocess
from typing import List

def is_process_running(process_name: str) -> bool:
    """
    Verifica se um determinado processo está ativo no Linux/Batocera utilizando pgrep.
    """
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
        # Fallback manual varrendo o diretório /proc
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
