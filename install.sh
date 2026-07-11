#!/bin/bash
#===============================================================================
# Batocera AutoDisc - Script de Instalação Automatizado
# Versão: 1.0.0
# Descrição: Instala e configura de forma profissional todos os componentes
#            do addon Batocera AutoDisc no sistema alvo.
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
SERVICE_NAME="disc-monitor"
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

# 3. Criar a estrutura hierárquica profissional de diretórios
create_directories() {
    log_step "A criar diretórios de sistema e configuração"

    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "${INSTALL_DIR}/profiles"
    mkdir -p "${INSTALL_DIR}/scripts"
    mkdir -p "${INSTALL_DIR}/docs"

    log_info "Diretórios criados com sucesso."
}

# 4. Copiar ficheiros e scripts limpos do pacote local
copy_files() {
    log_step "A copiar componentes de software"

    # Scripts executáveis principais (Python)
    cp "${SCRIPT_DIR}/disc-monitor.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/disc-launcher.py" "$INSTALL_DIR/"
    cp "${SCRIPT_DIR}/logger.py" "$INSTALL_DIR/"

    # Configurações do utilizador (Não sobrescreve se já existir uma modificada)
    if [[ -f "${CONFIG_DIR}/config.yaml" ]]; then
        log_warn "config.yaml já existe em ${CONFIG_DIR}. Preservando personalização do utilizador."
        cp "${SCRIPT_DIR}/config.yaml" "${CONFIG_DIR}/config.yaml.template"
    else
        cp "${SCRIPT_DIR}/config.yaml" "$CONFIG_DIR/"
    fi

    # Copiar perfis otimizados de emulação
    if [[ -d "${SCRIPT_DIR}/profiles" ]]; then
        cp "${SCRIPT_DIR}/profiles/"*.yaml "${INSTALL_DIR}/profiles/"
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
    ln -sf "${CONFIG_DIR}/config.yaml" "${INSTALL_DIR}/config.yaml"
}

# 5. Configurar as permissões Unix e ACLs adequadas
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

# 6. Instalar e validar as dependências Python
install_dependencies() {
    log_step "A validar dependências do interpretador Python"

    if ! python3 -c "import yaml" 2>/dev/null; then
        log_warn "Biblioteca PyYAML não encontrada. A tentar instalar via pip..."
        pip3 install pyyaml 2>/dev/null || log_error "Falha ao instalar PyYAML. O instalador tentará obter na execução."
    else
        log_info "Dependência PyYAML já se encontra instalada no sistema."
    fi
}

# 7. Configurar e recarregar regras udev
setup_udev() {
    log_step "A configurar regras do gestor de dispositivos udev"

    cp "${SCRIPT_DIR}/99-disc-monitor.rules" /etc/udev/rules.d/
    udevadm control --reload-rules 2>/dev/null || true
    udevadm trigger 2>/dev/null || true

    log_info "Regras udev ativas e aplicadas."
}

# 8. Instalar, habilitar e iniciar o serviço Systemd Daemon
setup_service() {
    log_step "A registar daemon no Systemd"

    cp "${SCRIPT_DIR}/disc-monitor.service" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}.service"
    systemctl restart "${SERVICE_NAME}.service"

    # Validar se o serviço arrancou corretamente em background
    if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        log_info "Serviço daemon '${SERVICE_NAME}' iniciado e a correr ativamente!"
    else
        log_error "O serviço falhou ao arrancar. Verifique o estado com: systemctl status ${SERVICE_NAME}"
    fi
}

# 9. Configurar rotação automática de logs para poupar armazenamento (Logrotate)
setup_logrotate() {
    log_step "A configurar logrotate"

    cat > /etc/logrotate.d/autodisc << EOF
${LOG_DIR}/*.log {
    daily
    rotate 5
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    log_info "Logrotate configurado com sucesso."
}

# 10. Gravar metadados de versão
write_metadata() {
    echo "1.0.0" > "${INSTALL_DIR}/version.txt"
}

# 11. Exibição de conclusão bem-sucedida do assistente
show_completion() {
    log_step "Instalação do Batocera AutoDisc Concluída!"

    cat << EOF

${GREEN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        Batocera AutoDisc v1.0.0 Instalado com Sucesso!        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝${NC}

${BLUE}📁 Estrutura de Diretórios:${NC}
  Instalação: ${INSTALL_DIR}
  Configuração: ${CONFIG_DIR}
  Registos:     ${LOG_DIR}

${BLUE}🔧 Gestão do Serviço:${NC}
  Status do daemon:  systemctl status ${SERVICE_NAME}
  Verificar registos: tail -f ${LOG_DIR}/disc-monitor.log
  Modificar opções:   nano ${CONFIG_DIR}/config.yaml

${GREEN}Pronto para jogar! Insira um disco original de consola no leitor.${NC}

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
    create_directories
    copy_files
    set_permissions
    install_dependencies
    setup_udev
    setup_service
    setup_logrotate
    write_metadata
    show_completion
}

# Executar o assistente
main "$@"
