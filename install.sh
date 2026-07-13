#!/bin/bash
#===============================================================================
# Batocera AutoDisc - Script de Instalação e Gestão (v1.1.0)
# Descrição: Instalação automatizada, desinstalação, backups, logs e rollback.
#            Garante compatibilidade total e persistência no Batocera.
#===============================================================================

# Interromper imediatamente o script se algum comando falhar para evitar corrupção
set -e

# Paleta de cores ANSI para formatação elegante do terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor (Reset)

# Definição de caminhos absolutos de instalação
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/userdata/system/autodisc"
CONFIG_DIR="/userdata/system/configs/autodisc"
LOG_DIR="/userdata/system/logs/autodisc"
USER="batocera"

# Configuração de registo físico de log de instalação (tee simultâneo)
INSTALL_LOG="${LOG_DIR}/install.log"
mkdir -p "$LOG_DIR"
# Enviar todo o stdout e stderr para o ficheiro de log e terminal simultaneamente
exec > >(tee -a "$INSTALL_LOG") 2>&1

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

# 2. Desinstalação completa do Addon
uninstall() {
    log_step "Desinstalando o Batocera AutoDisc v1.1.0"

    # Parar daemon ativo
    log_info "Parando daemon e limpando processos ativos..."
    /userdata/system/custom.sh stop 2>/dev/null || true
    pkill -f disc-monitor.py 2>/dev/null || true
    pkill -f disc-launcher.py 2>/dev/null || true

    # Remover diretórios principais
    log_info "Removendo diretórios físicos do addon..."
    rm -rf "$INSTALL_DIR"

    # Limpar regras do udev e serviços
    log_info "Removendo regras de udev e serviços do sistema..."
    rm -f "/userdata/system/udev/rules.d/99-disc-monitor.rules"
    rm -f "/etc/udev/rules.d/99-disc-monitor.rules"
    rm -f "/etc/systemd/system/disc-monitor.service"

    # Desvincular de forma cirúrgica do custom.sh do Batocera
    CUSTOM_SH="/userdata/system/custom.sh"
    if [[ -f "$CUSTOM_SH" ]]; then
        log_info "Limpando hooks de arranque em $CUSTOM_SH..."
        python3 -c "
import re
try:
    with open('$CUSTOM_SH', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Remover bloco delimitado por marcadores de boot hook
    cleaned = re.sub(r'# --- Batocera AutoDisc Boot Hook ---.*?# --- End Batocera AutoDisc ---', '', content, flags=re.DOTALL)
    with open('$CUSTOM_SH', 'w', encoding='utf-8') as f:
        f.write(cleaned)
except Exception as e:
    print('Erro não fatal ao limpar custom.sh:', e)
"
    fi

    # Recarregar udevadm
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true

    # Notificação OSD amigável de conclusão
    if [[ -f "${INSTALL_DIR}/scripts/notify.sh" ]]; then
        "${INSTALL_DIR}/scripts/notify.sh" "AutoDisc Desinstalado" "Addon removido com sucesso de forma permanente." "5000" || true
    fi

    log_info "Batocera AutoDisc removido por completo do sistema com sucesso!"
    exit 0
}

# 3. Validar se o sistema hospedeiro é de facto um Batocera Linux
check_system() {
    log_step "A verificar compatibilidade do sistema"

    if [[ ! -f "/etc/batocera-release" ]]; then
        log_warn "Ficheiro /etc/batocera-release não detetado. Isto pode não ser um sistema Batocera padrão."
    else
        BATOCERA_VERSION=$(cat /etc/batocera-release | cut -d' ' -f2-3)
        log_info "Batocera Linux detetado: $BATOCERA_VERSION"
    fi
}

# 4. Criar Backup de Segurança das configurações atuais se existirem
create_backup() {
    log_step "A criar cópia de segurança prévia"

    BACKUP_DIR="/userdata/system/backups/autodisc_install_$(date +%Y%m%d_%H%M%S)"
    if [[ -d "$INSTALL_DIR" ]]; then
        log_info "Instalação anterior encontrada. Salvaguardando para $BACKUP_DIR..."
        mkdir -p "/userdata/system/backups"
        cp -r "$INSTALL_DIR" "$BACKUP_DIR"
    fi
}

# 5. Rollback automático em caso de erro de instalação intermediário
rollback_on_failure() {
    log_error "Erro catastrófico ocorrido durante a instalação. Iniciando reversão (Rollback) automática..."
    if [[ -d "$BACKUP_DIR" ]]; then
        log_info "Restaurando cópia estável anterior..."
        rm -rf "$INSTALL_DIR"
        cp -r "$BACKUP_DIR" "$INSTALL_DIR"
    else
        log_info "Limpando diretórios residuais criados..."
        rm -rf "$INSTALL_DIR"
        rm -f "/userdata/system/udev/rules.d/99-disc-monitor.rules"
    fi
    log_info "Reversão para o estado estável anterior concluída."
}

# 6. Criar estrutura de diretórios necessária
create_directories() {
    log_step "A criar estrutura de pastas"

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "${INSTALL_DIR}/profiles"
    mkdir -p "${INSTALL_DIR}/scripts"
    mkdir -p "${INSTALL_DIR}/docs"

    # Pasta de regras udev persistentes do Batocera
    mkdir -p "/userdata/system/udev/rules.d"

    log_info "Diretórios de dados criados com absoluto sucesso."
}

# 7. Copiar ficheiros de sistema de forma cirúrgica
copy_files() {
    log_step "A copiar ficheiros de software"

    # Scripts Python
    cp "${SCRIPT_DIR}/disc-monitor.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/disc-launcher.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/logger.py" "$INSTALL_DIR/"

    # Configuração JSON do Utilizador (Preserva existente se houver)
    if [[ -f "${CONFIG_DIR}/config.json" ]]; then
        log_warn " config.json personalizado já existe em ${CONFIG_DIR}. Preservando opções atuais do utilizador."
        cp "${SCRIPT_DIR}/config.json" "${CONFIG_DIR}/config.json.template"
    else
        cp "${SCRIPT_DIR}/config.json" "$CONFIG_DIR/"
    fi

    # Perfis de Emulação
    if [[ -d "${SCRIPT_DIR}/profiles" ]]; then
        cp "${SCRIPT_DIR}/profiles/"*.json "${INSTALL_DIR}/profiles/"
        log_info "Perfis JSON copiados com sucesso."
    fi

    # Scripts OSD e Atualizador
    if [[ -d "${SCRIPT_DIR}/scripts" ]]; then
        cp "${SCRIPT_DIR}/scripts/"*.sh "${INSTALL_DIR}/scripts/"
        chmod +x "${INSTALL_DIR}/scripts/"*.sh
        log_info "Scripts auxiliares copiados e tornados executáveis."
    fi

    # Documentação
    if [[ -d "${SCRIPT_DIR}/docs" ]]; then
        cp "${SCRIPT_DIR}/docs/"*.md "${INSTALL_DIR}/docs/" 2>/dev/null || true
        log_info "Manuais e documentação copiados."
    fi

    # Link simbólico para facilitar localização de ficheiros
    ln -sf "${CONFIG_DIR}/config.json" "${INSTALL_DIR}/config.json"
}

# 8. Definir permissões de barramento de barramento adequadas
set_permissions() {
    log_step "A definir permissões Unix e proprietários"

    if id "$USER" &>/dev/null; then
        chown -R ${USER}:${USER} "$INSTALL_DIR" || true
        chown -R ${USER}:${USER} "$CONFIG_DIR" || true
        chown -R ${USER}:${USER} "$LOG_DIR" || true
    fi

    chmod 755 "$INSTALL_DIR/disc-monitor.py"
    chmod 755 "$INSTALL_DIR/disc-launcher.py"
    chmod 755 "$INSTALL_DIR/logger.py"

    log_info "Permissões de execução atribuídas."
}

# 9. Aplicar regras do udev
setup_udev() {
    log_step "A carregar regras de barramento ótico udev"

    # Diretório persistente
    cp "${SCRIPT_DIR}/99-disc-monitor.rules" "/userdata/system/udev/rules.d/"

    # Diretório dinâmico ativo em RAM
    cp "${SCRIPT_DIR}/99-disc-monitor.rules" /etc/udev/rules.d/

    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true

    log_info "Udev reindexado e ativo de imediato."
}

# 10. Registar e iniciar boot loader custom.sh do Batocera
setup_custom_startup() {
    log_step "A configurar inicialização do custom.sh"

    CUSTOM_SH="/userdata/system/custom.sh"

    # Se custom.sh não existir, criar um novo padrão com suporte a start/stop
    if [[ ! -f "$CUSTOM_SH" ]]; then
        log_info "Criando ficheiro custom.sh em falta..."
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
        log_info "Ficheiro custom.sh ativo encontrado. Injetando boot hooks..."
        if grep -q "disc-monitor.py" "$CUSTOM_SH"; then
            log_info "Os boot hooks do AutoDisc já se encontram ativos em custom.sh."
        else
            log_info "Injetando código AutoDisc de forma segura..."

            HOOK_TXT="
# --- Batocera AutoDisc Boot Hook ---
if [ -z \"\$1\" ] || [ \"\$1\" = \"start\" ]; then
    python3 /userdata/system/autodisc/disc-monitor.py > /userdata/system/logs/autodisc/monitor-service.log 2>&1 &
elif [ \"\$1\" = \"stop\" ]; then
    pkill -f disc-monitor.py || true
fi
# --- End Batocera AutoDisc ---
"
            # Executar injeção precisa usando interpretador Python nativo antes de qualquer instrução 'exit'
            python3 -c "
import sys
with open('$CUSTOM_SH', 'r', encoding='utf-8', errors='ignore') as f:
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
            log_info "Injeção de código custom.sh concluída com sucesso."
        fi
    fi

    chmod +x "$CUSTOM_SH"
    if id "$USER" &>/dev/null; then
        chown ${USER}:${USER} "$CUSTOM_SH" || true
    fi

    # Iniciar imediatamente o monitor em background sem necessidade de reiniciar agora
    log_info "A iniciar o monitor de discos em background imediatamente..."
    pkill -f disc-monitor.py || true
    python3 /userdata/system/autodisc/disc-monitor.py > /userdata/system/logs/autodisc/monitor-service.log 2>&1 &

    log_info "Daemon de monitorização ativado de imediato."
}

# 11. Gravar metadados de versão
write_metadata() {
    echo "1.1.0" > "${INSTALL_DIR}/version.txt"
}

# 12. Instalação e verificação de dependências Python
install_system_packages() {
    log_step "Instalando dependências de sistema (Python 3 e o melhor Terminal Linux)"

    # 1. Garantir a presença do Python 3
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

    # 2. Tentar instalar um emulador de terminal moderno e robusto (Xterm como padrão de compatibilidade)
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

# 13. Mostrar ecrã de conclusão bem-sucedido
show_completion() {
    log_step "Instalação Terminada!"

    # Disparar notificação OSD imediata
    if [[ -f "${INSTALL_DIR}/scripts/notify.sh" ]]; then
        "${INSTALL_DIR}/scripts/notify.sh" "Instalação Terminada" "Instalação terminada. Reinicie a consola para aplicar as alterações." "8000" || true
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
  Por favor, REINICIE A CONSOLA para que todas as regras de
  barramento udev sejam aplicadas no arranque do sistema de forma estrita.

EOF
}

# 14. Menu de Inicialização mestre (Tratamento de argumentos)
main() {
    check_root

    # Suportar flags de desinstalação
    if [[ "$1" == "uninstall" || "$1" == "--uninstall" || "$1" == "-u" ]]; then
        uninstall
    fi

    echo -e "${BLUE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════════════════╗
    ║                 BATOCERA AUTODISC ADDON                   ║
    ║           Instalador Físico do Serviço Daemon             ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # Configurar trap de erro ativo para rollback imediato se falhar
    trap rollback_on_failure ERR

    check_system
    install_system_packages
    create_backup
    create_directories
    copy_files
    set_permissions
    setup_udev
    setup_custom_startup
    write_metadata

    # Desarmar trap pois correu perfeitamente
    trap - ERR

    show_completion
}

# Iniciar assistente
main "$@"
