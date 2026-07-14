#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Módulo de Configuração (Multiplataforma)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import yaml
from pathlib import Path
from typing import Any, Dict

# Se for Windows, usa configs/. Se for Linux, usa configuraciones/.
if os.name == 'nt' or sys.platform == 'win32':
    CONFIG_DIR: Path = Path(__file__).resolve().parent.parent / "configs"
else:
    CONFIG_DIR: Path = Path(__file__).resolve().parent.parent / "configuraciones"

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """
    Carrega um ficheiro de configuração em formato YAML de forma segura.
    """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}

def get_main_config() -> Dict[str, Any]:
    """
    Retorna a configuração principal do ficheiro config.yaml.
    """
    return load_yaml(CONFIG_DIR / "config.yaml")

def get_profile_config(console_name: str) -> Dict[str, Any]:
    """
    Retorna o perfil YAML correspondente para uma determinada consola.
    """
    return load_yaml(CONFIG_DIR / f"{console_name}.yaml")
