#!/bin/bash
#===============================================================================
# Batocera AutoDisc - Sistema de Notificações no Ecrã
# Versão: 1.0.0
# Descrição: Exibe alertas visuais diretamente na interface do utilizador
#===============================================================================

# Definir parâmetros padrão caso não sejam passados argumentos
TITLE="${1:-Batocera AutoDisc}"
MESSAGE="${2:-Novo disco detetado}"
TIMEOUT="${3:-5000}" # Tempo de exibição em milissegundos (5 segundos)

# Exportar a variável de ecrã DISPLAY para garantir que as notificações X11 funcionam
if [[ -z "$DISPLAY" ]]; then
    export DISPLAY=:0.0
fi

# 1. Tentar utilizar o utilitário nativo do Batocera para notificações se disponível
if [[ -f "/usr/bin/batocera-notification" ]]; then
    /usr/bin/batocera-notification "$TITLE" "$MESSAGE" 2>/dev/null && exit 0
fi

# 2. Tentar utilizar o notify-send (geralmente instalado no servidor gráfico)
if command -v notify-send &> /dev/null; then
    notify-send -t "$TIMEOUT" "$TITLE" "$MESSAGE"
    exit 0
fi

# 3. Tentar utilizar o dunstify (usado no gestor de janelas leve do Batocera)
if command -v dunstify &> /dev/null; then
    dunstify -t "$TIMEOUT" "$TITLE" "$MESSAGE"
    exit 0
fi

# 4. Fallback 1: Imprimir no terminal de parede do sistema (útil para sessões SSH ativas)
echo -e "\n*** [$TITLE] ***\n$MESSAGE\n" | wall 2>/dev/null

# 5. Fallback 2: Registar no syslog geral do sistema Linux
logger -t "BatoceraAutoDisc" "$TITLE - $MESSAGE"

exit 0
