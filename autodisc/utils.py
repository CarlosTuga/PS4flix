#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Utilitários do Sistema
# Versão: 1.1.0
#===============================================================================

import os
import subprocess
from typing import List

def is_process_running(process_name: str) -> bool:
    """
    Verifica se um determinado processo está ativo no Windows utilizando tasklist.
    """
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

def sanitize_args(args: List[str]) -> List[str]:
    """
    Remove ou escapa argumentos maliciosos para segurança contra injeções.
    """
    return [str(arg).replace('"', '') for arg in args]
