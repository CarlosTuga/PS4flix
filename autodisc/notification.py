#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===============================================================================
# Batocera/RetroBat AutoDisc - Sistema de Notificações (Redirecionamento)
# Versão: 2.0.0
#===============================================================================

import sys
from pathlib import Path

# Ensure the parent directory of autodisc is in sys.path so that absolute imports of autodisc.* work
_parent_dir = str(Path(__file__).resolve().parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from autodisc.notificacion import *
