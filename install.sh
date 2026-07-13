#!/usr/bin/env bash
#===============================================================================
# Batocera AutoDisc - Script de Instalação (Nativa Linux/Batocera)
# Versão: 2.0.0
#===============================================================================

echo "==================================================================="
echo "            BATOCERA AUTODISC - INSTALADOR LINUX"
echo "==================================================================="

# 1. Definir caminhos de destino no sistema Batocera
TARGET_DIR="/userdata/system/batocera-autodisc"
SERVICE_PATH="/userdata/system/services/autodisc"
UDEV_RULE_PATH="/etc/udev/rules.d/99-autodisc.rules"

echo "[INFO] Criando diretórios e copiando arquivos para: $TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -r autodisc configs services requirements.txt "$TARGET_DIR/"

# 2. Criar ficheiro de serviço do Batocera
echo "[INFO] Configurando serviço em segundo plano: $SERVICE_PATH"
mkdir -p "/userdata/system/services"

cat << 'EOF' > "$SERVICE_PATH"
#!/usr/bin/env bash
#===============================================================================
# Batocera AutoDisc - Script de Serviço
#===============================================================================

DAEMON_PATH="/userdata/system/batocera-autodisc/autodisc/disc_monitor.py"

case "$1" in
    start)
        if pgrep -f "autodisc/disc_monitor.py" > /dev/null; then
            echo "AutoDisc já se encontra em execução."
            exit 0
        fi
        echo "Iniciando o serviço AutoDisc em segundo plano..."
        python3 "$DAEMON_PATH" > /userdata/system/logs/autodisc.log 2>&1 &
        ;;
    stop)
        echo "Parando o serviço AutoDisc..."
        pkill -f "autodisc/disc_monitor.py"
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    *)
        echo "Utilização: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
EOF

# 3. Ajustar permissões de execução
chmod +x "$SERVICE_PATH"
chmod +x "$TARGET_DIR/autodisc/disc_monitor.py"

# 4. Configurar regras udev no sistema para deteção de hardware dinâmica
echo "[INFO] Configurando regras de udev..."
if [ -d "/etc/udev/rules.d" ]; then
    cp "$TARGET_DIR/services/99-autodisc.rules" "$UDEV_RULE_PATH"
    # Recarregar regras udev se comando udevadm estiver ativo
    if command -v udevadm >/dev/null 2>&1; then
        udevadm control --reload-rules && udevadm trigger
    fi
fi

# 5. Ativar e iniciar o serviço através do batocera-services
if command -v batocera-services >/dev/null 2>&1; then
    echo "[INFO] Ativando e iniciando o serviço via batocera-services..."
    batocera-services enable autodisc
    batocera-services start autodisc
else
    # Fallback clássico via custom.sh caso não exista o batocera-services
    echo "[AVISO] batocera-services não encontrado. Utilizando fallback custom.sh..."
    CUSTOM_SH="/userdata/system/custom.sh"
    if [ -f "$CUSTOM_SH" ]; then
        if ! grep -q "autodisc/disc_monitor.py" "$CUSTOM_SH"; then
            echo "python3 $TARGET_DIR/autodisc/disc_monitor.py &" >> "$CUSTOM_SH"
        fi
    else
        echo -e "#!/bin/bash\npython3 $TARGET_DIR/autodisc/disc_monitor.py &" > "$CUSTOM_SH"
        chmod +x "$CUSTOM_SH"
    fi
    # Iniciar imediatamente
    python3 "$TARGET_DIR/autodisc/disc_monitor.py" > /userdata/system/logs/autodisc.log 2>&1 &
fi

# 6. Salvar sobreposição do Batocera para garantir persistência do udev após reiniciar
if command -v batocera-save-overlay >/dev/null 2>&1; then
    echo "[INFO] Salvando alterações de sobreposição para persistência do udev no Batocera..."
    batocera-save-overlay
fi

echo "==================================================================="
echo "[SUCESSO] Instalação do AutoDisc concluída com sucesso no Batocera!"
echo "O serviço foi configurado para arranque automático persistente."
echo "==================================================================="
