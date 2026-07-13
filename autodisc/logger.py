#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Módulo de Logging Centralizado (Nativa Linux)
# Versão: 2.0.0
#===============================================================================

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

# Definir o caminho de destino oficial especificado no Batocera
BATOCERA_LOG_DIR: Path = Path("/userdata/system/autodisc/logs")
LOCAL_LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
MAX_LOG_SIZE: int = 10485760  # 10 MB
BACKUP_COUNT: int = 3

def setup_logger(
    name: str,
    log_dir: Optional[Union[str, Path]] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configura e retorna uma instância do logger rotativo do sistema.
    """
    # 1. Definir o diretório de destino prioritário
    if log_dir:
        target_dir = Path(log_dir)
    else:
        target_dir = BATOCERA_LOG_DIR

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        try:
            # Fallback 1: Diretório de logs local
            target_dir = LOCAL_LOG_DIR
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback 2: Diretório temporário do sistema
            target_dir = Path("/tmp/autodisc_logs")
            target_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    log_file = target_dir / f"{name}.log"

    try:
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    except Exception:
        pass

    try:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
    except Exception:
        pass

    return logger
