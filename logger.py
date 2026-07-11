#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera AutoDisc - Módulo de Logging Centralizado
# Versão: 1.0.0
# Descrição: Configuração profissional e centralizada de logs com rotação automática
#===============================================================================

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name, log_dir, level=logging.INFO):
    """
    Configura um Logger com rotação de ficheiros automática para evitar sobrecarga de disco.

    Args:
        name (str): Nome identificador do logger.
        log_dir (str): Diretório onde os ficheiros de log serão salvos.
        level (int): Nível de severidade do logging (ex: logging.INFO).

    Returns:
        logging.Logger: Instância do logger configurado.
    """
    # Garantir que o diretório de logs existe no sistema de ficheiros
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        # Fallback silencioso caso não seja possível criar no diretório padrão
        log_dir = "/tmp/autodisc_logs"
        os.makedirs(log_dir, exist_ok=True)

    # Obter ou criar o logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar adicionar múltiplos handlers redundantes se o logger já estiver configurado
    if logger.handlers:
        return logger

    # Definir formato padrão das mensagens de log (Estampa temporal - Nome - Severidade - Mensagem)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para ficheiro físico de log com rotação automática de 10MB e limite de 5 cópias de segurança
    log_file = os.path.join(log_dir, f'{name}.log')
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Se falhar ao abrir o ficheiro, escreve apenas na consola
        print(f"Erro ao inicializar o logger de ficheiro em {log_file}: {e}")

    # Handler de consola/fluxo padrão para fins de debugging em tempo real
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Apenas avisos e erros na consola de saída padrão
    logger.addHandler(console_handler)

    return logger

class LoggerMixin:
    """
    Mixin utilitário para adicionar capacidades de logging automático a classes.
    Simplifica o acesso ao logger local utilizando 'self.logger'.
    """
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(
                self.__class__.__name__,
                '/userdata/system/logs/autodisc'
            )
        return self._logger

# Funções utilitárias globais para logging rápido sem necessidade de instanciar classes
def log_info(message):
    """Regista uma mensagem de informação geral."""
    logger = setup_logger('autodisc', '/userdata/system/logs/autodisc')
    logger.info(message)

def log_error(message):
    """Regista uma mensagem de erro crítico."""
    logger = setup_logger('autodisc', '/userdata/system/logs/autodisc')
    logger.error(message)

def log_warning(message):
    """Regista um aviso ou ocorrência não-crítica."""
    logger = setup_logger('autodisc', '/userdata/system/logs/autodisc')
    logger.warning(message)

def log_debug(message):
    """Regista mensagens de depuração fina de código (apenas visível em modo debug)."""
    logger = setup_logger('autodisc', '/userdata/system/logs/autodisc')
    logger.debug(message)
