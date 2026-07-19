#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# RetroBat AutoDisc - Definição de Emuladores
# Versão: 1.1.0
#===============================================================================

from typing import Dict

# Mapeamento padrão de consolas para os emuladores suportados
DEFAULT_EMULATOR_MAP: Dict[str, str] = {
    'psx': 'ps1',
    'ps2': 'ps2',
    'segacd': 'segacd',
    'saturn': 'saturn',
    'dreamcast': 'dreamcast',
    'gamecube': 'gamecube',
    'wii': 'wii',
    'xbox': 'xbox',
    'xbox360': 'xbox360',
    'ps3': 'ps3',
    'psp': 'ppsspp'
}
