#!/bin/bash
#===============================================================================
# Batocera AutoDisc - Script de Instalação Automatizado e Persistente
# Versão: 1.0.0
# Descrição: Instala e configura de forma profissional e persistente todos os
#            componentes do addon Batocera AutoDisc no sistema alvo, garantindo
#            o arranque automático após reboots (via custom.sh e udev persistente).
#===============================================================================

# Interromper imediatamente o script se algum comando falhar para evitar corrupção
set -e

# Paleta de cores ANSI para formatação elegante do terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor (Reset)

# Definição de localizações físicas no Batocera
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/userdata/system/autodisc"
CONFIG_DIR="/userdata/system/configs/autodisc"
LOG_DIR="/userdata/system/logs/autodisc"
USER="batocera"

# Funções auxiliares de feedback visual
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# 1. Validar privilégios de administrador (root)
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script de instalação deve ser executado com privilégios de ROOT (Administrador)."
        log_info "Por favor, execute como: sudo $0"
        exit 1
    fi
}

# 2. Validar se o sistema hospedeiro é de facto um Batocera Linux
check_system() {
    log_step "A verificar compatibilidade do sistema"

    if [[ ! -f "/etc/batocera-release" ]]; then
        log_warn "Ficheiro /etc/batocera-release não detetado. Isto pode não ser um sistema Batocera padrão."
    else
        BATOCERA_VERSION=$(cat /etc/batocera-release | cut -d' ' -f2-3)
        log_info "Batocera Linux detetado: $BATOCERA_VERSION"
    fi

    # Validar se existe o leitor físico no caminho padrão /dev/sr0
    if [[ ! -e "/dev/sr0" ]]; then
        log_warn "Leitor ótico físico em /dev/sr0 não foi encontrado no barramento SCSI atual."
        log_warn "O serviço será instalado mas necessitará de hardware compatível para funcionar."
    else
        log_info "Dispositivo ótico compatível encontrado em /dev/sr0."
    fi
}

# 3. Baixar e instalar o Python 3 e o melhor terminal de Linux (Xterm/Alacritty) se suportado pelo sistema
install_system_packages() {
    log_step "Instalando dependências de sistema (Python 3 e o melhor Terminal Linux)"

    # 3.1 Garantir a presença do Python 3
    if ! command -v python3 &>/dev/null; then
        log_warn "Python 3 não detetado no sistema. Tentando efetuar a instalação..."
        if command -v apt-get &>/dev/null; then
            apt-get update && apt-get install -y python3 python3-pip
        elif command -v pacman &>/dev/null; then
            pacman -Sy --noconfirm python3
        elif command -v dnf &>/dev/null; then
            dnf install -y python3
        else
            log_error "Não foi possível instalar o Python 3 de forma automatizada (Gestor de pacotes não suportado)."
            log_info "Se está no Batocera nativo, o Python 3 já se encontra instalado nativamente."
        fi
    else
        log_info "Python 3 já se encontra instalado nativamente no sistema."
    fi

    # 3.2 Tentar instalar um emulador de terminal moderno e robusto (Xterm como padrão de compatibilidade)
    if ! command -v xterm &>/dev/null && ! command -v alacritty &>/dev/null; then
        log_warn "Nenhum emulador de terminal avançado encontrado. Instalando o xterm (melhor terminal clássico estável)..."
        if command -v apt-get &>/dev/null; then
            apt-get install -y xterm || true
        elif command -v pacman &>/dev/null; then
            pacman -Sy --noconfirm xterm || true
        elif command -v dnf &>/dev/null; then
            dnf install -y xterm || true
        else
            log_info "No Batocera nativo, o emulador de terminal padrão já se encontra integrado na interface."
        fi
    else
        log_info "Um terminal avançado já se encontra disponível no sistema."
    fi
}

# 4. Criar a estrutura hierárquica profissional de diretórios (incluindo caminhos persistentes do Batocera)
create_directories() {
    log_step "A criar diretórios de sistema e configuração"

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "${INSTALL_DIR}/profiles"
    mkdir -p "${INSTALL_DIR}/scripts"
    mkdir -p "${INSTALL_DIR}/docs"

    # Diretório persistente para regras do udev no Batocera
    mkdir -p "/userdata/system/udev/rules.d"

    log_info "Diretórios criados com sucesso."
}

# 5. Copiar ficheiros e scripts limpos do pacote local
copy_files() {
    log_step "A copiar componentes de software"

    # Scripts executáveis principais (Python)
    cp "${SCRIPT_DIR}/disc-monitor.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/disc-launcher.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/logger.py" "$INSTALL_DIR/"

    # Configurações do utilizador (Não sobrescreve se já existir uma modificada)
    if [[ -f "${CONFIG_DIR}/config.json" ]]; then
        log_warn "config.json já existe em ${CONFIG_DIR}. Preservando personalização do utilizador."
        cp "${SCRIPT_DIR}/config.json" "${CONFIG_DIR}/config.json.template"
    else
        cp "${SCRIPT_DIR}/config.json" "$CONFIG_DIR/"
    fi

    # Copiar perfis otimizados de emulação
    if [[ -d "${SCRIPT_DIR}/profiles" ]]; then
        cp "${SCRIPT_DIR}/profiles/"*.json "${INSTALL_DIR}/profiles/"
        log_info "Perfis de emuladores copiados."
    fi

    # Copiar scripts auxiliares
    if [[ -d "${SCRIPT_DIR}/scripts" ]]; then
        cp "${SCRIPT_DIR}/scripts/"*.sh "${INSTALL_DIR}/scripts/"
        chmod +x "${INSTALL_DIR}/scripts/"*.sh
        log_info "Scripts utilitários copiados."
    fi

    # Copiar documentação local
    if [[ -d "${SCRIPT_DIR}/docs" ]]; then
        cp "${SCRIPT_DIR}/docs/"*.md "${INSTALL_DIR}/docs/" 2>/dev/null || true
        log_info "Documentação de referência copiada."
    fi

    # Criar link simbólico para o ficheiro de configuração no diretório principal
    ln -sf "${CONFIG_DIR}/config.json" "${INSTALL_DIR}/config.json"
}

# 6. Configurar as permissões Unix e ACLs adequadas
set_permissions() {
    log_step "A configurar permissões e proprietários de ficheiros"

    # Associar ficheiros de dados ao utilizador padrão do Batocera (batocera) se existir
    if id "$USER" &>/dev/null; then
        chown -R ${USER}:${USER} "$INSTALL_DIR" || true
        chown -R ${USER}:${USER} "$CONFIG_DIR" || true
        chown -R ${USER}:${USER} "$LOG_DIR" || true
    fi

    # Definir permissões estritas de leitura/escrita e execução para os binários python
    chmod 755 "$INSTALL_DIR/disc-monitor.py"
    chmod 755 "$INSTALL_DIR/disc-launcher.py"
    chmod 755 "$INSTALL_DIR/logger.py"

    log_info "Permissões aplicadas com absoluto sucesso."
}

# 7. Configurar e recarregar regras udev (tanto na RAM /etc como no caminho persistente do /userdata)
setup_udev() {
    log_step "A configurar regras do gestor de dispositivos udev"

    # 1. Copiar para o diretório persistente do Batocera (permanece após reboot!)
    cp "${SCRIPT_DIR}/99-disc-monitor.rules" "/userdata/system/udev/rules.d/"

    # 2. Copiar para o diretório ativo em RAM do Linux (funciona imediatamente sem reboot!)
    cp "${SCRIPT_DIR}/99-disc-monitor.rules" /etc/udev/rules.d/

    # Recarregar e disparar regras
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true

    log_info "Regras udev ativas de imediato e guardadas de forma persistente."
}

# 8. Configurar inicialização persistente e imediata através do custom.sh do Batocera
setup_custom_startup() {
    log_step "A configurar inicialização persistente (/userdata/system/custom.sh)"

    CUSTOM_SH="/userdata/system/custom.sh"

    # Se o ficheiro não existir, criar um novo padrão com suporte a start/stop
    if [[ ! -f "$CUSTOM_SH" ]]; then
        log_info "Criando novo ficheiro custom.sh..."
        cat > "$CUSTOM_SH" << 'EOF'
#!/bin/bash
#===============================================================================
# Batocera Custom Startup Script - AutoDisc Daemon Bootloader
#===============================================================================

# Iniciar o monitor de discos se executado sem argumentos ou com "start"
if [ -z "$1" ] || [ "$1" = "start" ]; then
    python3 /userdata/system/autodisc/disc-monitor.py > /userdata/system/logs/autodisc/monitor-service.log 2>&1 &
elif [ "$1" = "stop" ]; then
    pkill -f disc-monitor.py || true
fi
exit 0
EOF
    else
        log_info "Ficheiro custom.sh existente detetado. Injetando hooks do AutoDisc..."
        # Evitar duplicados verificando a presença do disc-monitor.py
        if grep -q "disc-monitor.py" "$CUSTOM_SH"; then
            log_info "A inicialização do disc-monitor já está configurada no custom.sh existente."
        else
            log_info "Injetando código AutoDisc de forma segura..."

            # Hook em bloco a ser injetado de forma segura antes de qualquer exit 0
            HOOK_TXT="
# --- Batocera AutoDisc Boot Hook ---
if [ -z \"\$1\" ] || [ \"\$1\" = \"start\" ]; then
    python3 /userdata/system/autodisc/disc-monitor.py > /userdata/system/logs/autodisc/monitor-service.log 2>&1 &
elif [ \"\$1\" = \"stop\" ]; then
    pkill -f disc-monitor.py || true
fi
# --- End Batocera AutoDisc ---
"
            # Executar injeção precisa usando interpretador Python nativo
            python3 -c "
import sys
with open('$CUSTOM_SH', 'r', encoding='utf-8') as f:
    lines = f.readlines()
inserted = False
for idx, line in enumerate(lines):
    if line.strip().startswith('exit'):
        lines.insert(idx, '''$HOOK_TXT\n''')
        inserted = True
        break
if not inserted:
    lines.append('''$HOOK_TXT\n''')
with open('$CUSTOM_SH', 'w', encoding='utf-8') as f:
    f.writelines(lines)
"
            log_info "Injeção de código custom.sh efetuada com sucesso antes da instrução de saída."
        fi
    fi

    # Garantir permissões corretas de execução
    chmod +x "$CUSTOM_SH"
    if id "$USER" &>/dev/null; then
        chown ${USER}:${USER} "$CUSTOM_SH" || true
    fi

    # Iniciar imediatamente o monitor em background sem necessidade de reiniciar agora
    log_info "A iniciar o monitor de discos em background imediatamente..."
    pkill -f disc-monitor.py || true
    python3 /userdata/system/autodisc/disc-monitor.py > /userdata/system/logs/autodisc/monitor-service.log 2>&1 &

    log_info "Inicialização do custom.sh configurada e daemon ativado com sucesso."
}

# 9. Gravar metadados de versão
write_metadata() {
    echo "1.0.0" > "${INSTALL_DIR}/version.txt"
}

# 10. Exibição de conclusão bem-sucedida do assistente com notificações
show_completion() {
    log_step "Instalação do Batocera AutoDisc Concluída!"

    # Disparar notificação OSD física no ecrã da consola
    if [[ -f "${INSTALL_DIR}/scripts/notify.sh" ]]; then
        "${INSTALL_DIR}/scripts/notify.sh" "Instalação Concluída" "Instalação terminada. Reinicie a consola para aplicar as alterações." "8000" || true
    fi

    cat << EOF

${GREEN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               INSTALAÇÃO TERMINADA!                           ║
║               REINICIE A CONSSOLA                             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝${NC}

${BLUE}📁 Estrutura de Diretórios Persistente:${NC}
  Instalação: ${INSTALL_DIR}
  Configuração: ${CONFIG_DIR}
  Registos:     ${LOG_DIR}
  Udev Regras:  /userdata/system/udev/rules.d/99-disc-monitor.rules
  Boot Hook:    /userdata/system/custom.sh

${BLUE}🔧 Gestão do Serviço Daemon:${NC}
  Iniciar/Parar:      /userdata/system/custom.sh [start|stop]
  Verificar registos: tail -f ${LOG_DIR}/disc-monitor.log
  Modificar opções:   nano ${CONFIG_DIR}/config.json

${YELLOW}⚠️  IMPORTANTE:${NC}
  Por favor, REINICIE A CONSOLA para que todas as regras persistentes de
  barramento udev sejam ativadas de forma definitiva na inicialização.

EOF
}

# Função principal
main() {
    echo -e "${BLUE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════╗
    ║                 BATOCERA AUTODISC ADDON                   ║
    ║           Instalador Físico do Serviço Daemon             ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    check_root
    check_system
    install_system_packages
    create_directories
    copy_files
    set_permissions
    setup_udev
    setup_custom_startup
    write_metadata
    show_completion
}

# Executar o assistente
main "$@"
