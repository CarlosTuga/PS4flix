#!/bin/bash
#===============================================================================
# Batocera AutoDisc - Utilitário de Atualização do Addon
# Versão: 1.0.0
# Descrição: Verifica atualizações remotas, efetua cópia de segurança e instala
#===============================================================================

# Garantir interrupção imediata em caso de erro grave durante a atualização
set -e

# Variáveis globais de localização
INSTALL_DIR="/userdata/system/autodisc"
CONFIG_DIR="/userdata/system/configs/autodisc"
VERSION_FILE="${INSTALL_DIR}/version.txt"
# URL do repositório remoto para descarregar atualizações (pode ser personalizada)
REPO_URL="https://raw.githubusercontent.com/CarlosTuga/batocera-autodisc/main"

# Paleta de cores para output formatado no terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color (Reset)

print_message() {
    echo -e "${GREEN}[ATUALIZAR]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# 1. Determinar a versão atualmente instalada no sistema
if [[ -f "$VERSION_FILE" ]]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
else
    CURRENT_VERSION="0.0.0"
fi

print_message "Versão atual instalada: $CURRENT_VERSION"

# 2. Consultar o repositório remoto para saber qual a última versão estável disponível
print_message "A verificar nova versão remotamente..."
LATEST_VERSION=$(curl -s --connect-timeout 5 "${REPO_URL}/version.txt" || echo "$CURRENT_VERSION")

if [[ -z "$LATEST_VERSION" ]]; then
    print_error "Não foi possível conectar ao servidor de atualizações."
    exit 1
fi

print_message "Versão mais recente disponível: $LATEST_VERSION"

# Se as versões coincidirem, terminar o processo sem fazer alterações
if [[ "$CURRENT_VERSION" == "$LATEST_VERSION" ]]; then
    print_message "O Batocera AutoDisc já se encontra na versão mais recente!"
    exit 0
fi

print_warning "Nova versão ($LATEST_VERSION) detetada! Iniciando atualização..."

# 3. Parar temporariamente o serviço para não corromper ficheiros em execução
print_message "Parando o serviço disc-monitor..."
systemctl stop disc-monitor.service 2>/dev/null || true

# 4. Criar Cópia de Segurança (Backup) da versão atual instalada
BACKUP_DIR="/userdata/system/backups/autodisc_$(date +%Y%m%d_%H%M%S)"
print_message "Criando cópia de segurança em: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$INSTALL_DIR" "$BACKUP_DIR/" 2>/dev/null || true

# 5. Descarregar e atualizar os ficheiros executáveis principais
print_message "Descarregando ficheiros de código principais..."
FILES=(
    "disc-monitor.py"
    "disc-launcher.py"
    "logger.py"
    "99-disc-monitor.rules"
    "disc-monitor.service"
    "config.yaml"
)

for file in "${FILES[@]}"; do
    if [[ "$file" == "config.yaml" ]]; then
        # Evitar sobrescrever a configuração personalizada do utilizador diretamente
        wget -q -O "${CONFIG_DIR}/config.yaml.new" "${REPO_URL}/${file}" || print_warning "Falha ao obter config.yaml novo."
        print_message "Nova configuração padrão guardada como config.yaml.new (verifique diferenças)."
    else
        wget -q -O "${INSTALL_DIR}/${file}" "${REPO_URL}/${file}" || {
            print_error "Falha ao descarregar ${file}"
            exit 1
        }
        chmod 755 "${INSTALL_DIR}/${file}"
    fi
done

# 6. Atualizar os perfis padrão das consolas de emulação
print_message "Atualizando perfis de emuladores..."
mkdir -p "${INSTALL_DIR}/profiles"
PROFILES=(
    "dolphin.yaml"
    "duckstation.yaml"
    "flycast.yaml"
    "pcsx2.yaml"
    "ppsspp.yaml"
    "redream.yaml"
    "rpcs3.yaml"
    "xemu.yaml"
)

for profile in "${PROFILES[@]}"; do
    wget -q -O "${INSTALL_DIR}/profiles/${profile}" "${REPO_URL}/profiles/${profile}" || print_warning "Falha ao atualizar perfil ${profile}."
done

# 7. Atualizar as regras do udev e reiniciar o gestor de dispositivos udevadm
print_message "Atualizando e recarregando regras do udev..."
if [[ -f "${INSTALL_DIR}/99-disc-monitor.rules" ]]; then
    cp "${INSTALL_DIR}/99-disc-monitor.rules" /etc/udev/rules.d/
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true
fi

# 8. Atualizar o ficheiro de definição do serviço Systemd e recarregar
print_message "Atualizando e recarregando serviço systemd..."
if [[ -f "${INSTALL_DIR}/disc-monitor.service" ]]; then
    cp "${INSTALL_DIR}/disc-monitor.service" /etc/systemd/system/
    systemctl daemon-reload 2>/dev/null || true
fi

# 9. Guardar a nova versão bem-sucedida e reiniciar o serviço
echo "$LATEST_VERSION" > "$VERSION_FILE"
print_message "Iniciando o serviço disc-monitor atualizado..."
systemctl start disc-monitor.service 2>/dev/null || true

print_message "Atualização para a versão $LATEST_VERSION efetuada com total sucesso!"
exit 0
