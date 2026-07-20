#!/usr/bin/env bash
#===============================================================================
# Batocera AutoDisc - Script de Desinstalação (Nativa Linux/Batocera)
# Versão: 2.0.0
#===============================================================================

echo "==================================================================="
echo "            BATOCERA AUTODISC - DESINSTALADOR"
echo "==================================================================="

# 1. Parar e desativar o serviço no Batocera
if command -v batocera-services >/dev/null 2>&1; then
    echo "[INFO] Parando e desativando o serviço de monitorização..."
    batocera-services stop autodisc >/dev/null 2>&1
    batocera-services disable autodisc >/dev/null 2>&1
fi

# 2. Terminar processos remanescentes de monitorização de forma forçada
echo "[INFO] Parando processos ativos do daemon..."
pkill -f "autodisc/disc_monitor.py" >/dev/null 2>&1

# 3. Remover ficheiros de serviço, regras udev e pastas instaladas
SERVICE_PATH="/userdata/system/services/autodisc"
UDEV_RULE_PATH="/etc/udev/rules.d/99-autodisc.rules"
TARGET_DIR="/userdata/system/batocera-autodisc"

if [ -f "$SERVICE_PATH" ]; then
    rm -f "$SERVICE_PATH"
    echo "[INFO] Serviço removido: $SERVICE_PATH"
fi

if [ -f "$UDEV_RULE_PATH" ]; then
    rm -f "$UDEV_RULE_PATH"
    echo "[INFO] Regras udev removidas: $UDEV_RULE_PATH"
    if command -v udevadm >/dev/null 2>&1; then
        udevadm control --reload-rules
    fi
fi

if [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
    echo "[INFO] Pasta de instalação removida: $TARGET_DIR"
fi

# 4. Limpar referências do custom.sh
CUSTOM_SH="/userdata/system/custom.sh"
if [ -f "$CUSTOM_SH" ]; then
    if grep -q "autodisc/disc_monitor.py" "$CUSTOM_SH"; then
        echo "[INFO] Limpando referências no custom.sh..."
        sed -i '/autodisc\/disc_monitor.py/d' "$CUSTOM_SH"
    fi
fi

# 5. Salvar sobreposição do Batocera para garantir persistência após reiniciar
if command -v batocera-save-overlay >/dev/null 2>&1; then
    echo "[INFO] Salvando alterações de sobreposição no Batocera..."
    batocera-save-overlay
fi

echo "==================================================================="
echo "[SUCESSO] Desinstalação concluída com sucesso no Batocera!"
echo "==================================================================="
