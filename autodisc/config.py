#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Módulo de Configuração
# Versão: 1.1.0
#===============================================================================

import os
import yaml
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR: Path = Path(__file__).resolve().parent.parent / "configs"

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
    Retorna a configuração principal do ficheiro configs/config.yaml.
    """
    return load_yaml(CONFIG_DIR / "config.yaml")

def get_profile_config(console_name: str) -> Dict[str, Any]:
    """
    Retorna o perfil YAML correspondente para uma determinada consola.
    """
    return load_yaml(CONFIG_DIR / f"{console_name}.yaml")
