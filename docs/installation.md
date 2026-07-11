# Guia de Instalação - Batocera AutoDisc

Este guia descreve detalhadamente o processo de instalação do addon **Batocera AutoDisc** no sistema **Batocera Linux v43.1 (x86_64)**.

---

## 1. Pré-requisitos de Sistema

Antes de iniciar a instalação, certifique-se de que o hardware e o software cumprem as especificações recomendadas para um desempenho ótimo de emulação em 1080p:

### Hardware Recomendado
* **CPU:** Intel Core i7-8700 (6 Cores / 12 Threads) ou superior.
* **GPU:** NVIDIA GeForce GTX 1060 3GB ou superior.
* **RAM:** 16 GB de RAM de duplo canal.
* **Leitor Ótico:** Leitor de DVD/Blu-ray SATA interno ou HP PLDS DU8AESH montado em `/dev/sr0`.

### Requisitos de Software
* **Sistema Operativo:** Batocera Linux v43.1 (x86_64) instalado de forma limpa.
* **Acesso SSH:** Conexão de rede ativa e credenciais de administrador (por padrão, utilizador `root` e palavra-passe `recalboxroot`).

---

## 2. Instalação Automatizada (Recomendado)

O método mais seguro e rápido consiste em clonar ou extrair o pacote AutoDisc diretamente para o PC com Batocera e executar o assistente automático:

```bash
# 1. Aceder ao terminal do Batocera (via SSH ou pressionando F1 -> Terminal)
cd /userdata/system

# 2. Clonar ou transferir o repositório do addon
git clone https://github.com/CarlosTuga/batocera-autodisc.git
cd batocera-autodisc

# 3. Executar o script instalador com privilégios de root
chmod +x install.sh
./install.sh
```

### O que o instalador faz automaticamente:
1. Valida se o sistema é compatível com o Batocera v43.1.
2. Cria os diretórios necessários em `/userdata/system/autodisc` e `/userdata/system/configs/autodisc`.
3. Copia todos os ficheiros Python, perfis YAML otimizados e utilitários de sistema para os locais apropriados.
4. Regista e ativa as regras do gestor de dispositivos **udev** em `/etc/udev/rules.d/99-disc-monitor.rules`.
5. Instala e ativa o serviço em background **Systemd** (`disc-monitor.service`).
6. Configura o utilitário **logrotate** para evitar que os ficheiros de registo sobrecarreguem o armazenamento interno.

---

## 3. Instalação Manual (Passo a Passo)

Caso prefira instalar os componentes individualmente para fins de depuração, siga as etapas abaixo:

### Passo 3.1: Criação da estrutura de pastas
```bash
mkdir -p /userdata/system/autodisc/profiles
mkdir -p /userdata/system/autodisc/scripts
mkdir -p /userdata/system/configs/autodisc
mkdir -p /userdata/system/logs/autodisc
```

### Passo 3.2: Transferência de ficheiros de código
Copie os ficheiros de código de forma correspondente:
* `disc-monitor.py` -> `/userdata/system/autodisc/disc-monitor.py`
* `disc-launcher.py` -> `/userdata/system/autodisc/disc-launcher.py`
* `logger.py` -> `/userdata/system/autodisc/logger.py`
* `config.yaml` -> `/userdata/system/configs/autodisc/config.yaml`
* `profiles/*.yaml` -> `/userdata/system/autodisc/profiles/`
* `scripts/*.sh` -> `/userdata/system/autodisc/scripts/`

Ajuste as permissões de execução dos scripts principais:
```bash
chmod 755 /userdata/system/autodisc/*.py
chmod +x /userdata/system/autodisc/scripts/*.sh
```

### Passo 3.3: Instalar as Regras udev
Copie o ficheiro de regras de barramento para o diretório padrão de regras do Linux:
```bash
cp 99-disc-monitor.rules /etc/udev/rules.d/
udevadm control --reload-rules
udevadm trigger
```

### Passo 3.4: Instalar e iniciar o Serviço Systemd
Copie o descritor de serviço systemd, recarregue o gestor de daemons e inicie o serviço em background:
```bash
cp disc-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable disc-monitor.service
systemctl start disc-monitor.service
```

---

## 4. Verificação de Funcionamento

Após a conclusão da instalação, pode verificar se tudo está a correr em conformidade através dos seguintes comandos de diagnóstico rápidos:

* **Verificar o estado do Daemon:**
  ```bash
  systemctl status disc-monitor.service
  ```
  *(Deverá exibir o estado como "active (running)")*

* **Monitorizar os registos em tempo real:**
  ```bash
  tail -f /userdata/system/logs/autodisc/disc-monitor.log
  ```

* **Testar inserção física:**
  Insira um disco original de PlayStation 2 ou PlayStation 1 no leitor de discos. Uma notificação OSD deverá surgir no ecrã principal dentro de 5 a 8 segundos, iniciando o emulador correto.
