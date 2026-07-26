# Batocera AutoDisc v2.0.0 (Linux)

**Batocera AutoDisc** é um addon modular completo e profissional desenvolvido especificamente para o sistema operativo **Batocera Linux 43.1 (x86_64)**.

O seu principal objetivo é transformar qualquer computador de sala ou máquina de jogos retro numa consola física autêntica, permitindo a **deteção, identificação física/lógica e arranque automático de discos originais de consolas físicas** inseridos no leitor de DVD/CD-ROM.

---

## 🎯 Características Principais

* **Deteção nativa via Linux udev e ioctl:** Monitorização contínua de barramentos de leitores óticos e deteção do estado do disco através de códigos ioctl `CDROM_DRIVE_STATUS` (0x5326) de forma 100% nativa em Linux.
* **Leitura Física e Assinaturas RAW:** Executa a leitura de setores binários de baixo nível via dispositivo `/dev/sr0` para identificar consolas retro clássicas que usam formatos híbridos de CD/dados (**Sega Saturn**, **Sega CD**, **Sega Dreamcast**, **PC Engine CD**, **NeoGeo CD**, **3DO**, **CD-i**).
* **Análise Lógica e Identificação:** Analisa sistemas de ficheiros e assinaturas montadas dinamicamente no Linux para consolas como **PlayStation 1**, **PlayStation 2**, **PlayStation 3**, **Nintendo GameCube**, **Nintendo Wii**, **Xbox Original** e **Xbox 360**.
* **Notificações OSD nativas do Batocera:** Utiliza mensagens On-Screen Display (OSD) no ecrã principal através do utilitário `osd_cat` com fallbacks amigáveis para consolas e logging centralizado.
* **Inicialização Silenciosa em Segundo Plano:** Executa de forma 100% invisível em segundo plano como um serviço do Batocera (`batocera-services`) ou script `custom.sh`.
* **Arranque Seguro com EmulationStation:** O daemon aguarda de forma inteligente que a interface EmulationStation ou o executável `batocera-es` estejam ativos antes de iniciar a monitorização ativa de mídias físicas.
* **Perfis Otimizados para GTX 1060 + i7-8700:** Mapeamentos em ficheiros YAML individuais na pasta `configs/` para emuladores standalone como **DuckStation**, **PCSX2**, **Dolphin**, **Flycast**, **Redream**, **Xemu**, **RPCS3** e **PPSSPP** com suporte nativo a Vulkan, multithreading, shader cache e speedhacks.

---

## 📁 Estrutura de Diretórios do Addon

```text
batocera-autodisc/
├── autodisc/                  # Ficheiros e módulos Python do addon
│   ├── config.py              # Leitura de ficheiros de configuração YAML
│   ├── console_detector.py    # Algoritmos de deteção RAW e lógica de consolas
│   ├── disc_detector.py       # Deteção física de leitores óticos via ioctl
│   ├── disc_launcher.py       # Gestão de comandos e execução de emuladores via emulatorlauncher
│   ├── disc_monitor.py        # Loop daemon de background e escuta ativa de processos
│   ├── emulators.py           # Associações e emuladores mapeados
│   ├── installer.py           # Utilitários de instalação
│   ├── logger.py              # Sistema de logs rotativo de 10MB em /userdata/system/autodisc/logs/
│   ├── notification.py        # Notificações Toast/OSD nativas via osd_cat
│   ├── updater.py             # Utilitários de atualização
│   └── utils.py               # Funções auxiliares do sistema (pgrep)
├── configs/                   # Pasta central de configurações e perfis YAML
│   ├── config.yaml            # Configurações globais de caminhos e leitor
│   ├── ps1.yaml               # Perfil otimizado DuckStation
│   ├── ps2.yaml               # Perfil otimizado PCSX2
│   ├── gamecube.yaml          # Perfil otimizado Dolphin
│   # ... (outros perfis de consolas)
├── services/                  # Ficheiros de registo de serviço no sistema
│   ├── autodisc.service       # Ficheiro de serviço systemd
│   └── 99-autodisc.rules      # Regra udev de deteção de eventos óticos
├── docs/                      # Manuais e documentações de referência rápida
├── CHANGELOG.md               # Diário de alterações e melhorias efetuadas
├── install.sh                 # Instalador automatizado no Batocera
├── uninstall.sh               # Desinstalador automático do Batocera
├── requirements.txt           # Ficheiro de requisitos do Python (PyYAML)
└── LICENSE                    # Licença MIT open-source
```

---

## 🚀 Como Instalar

Instalar o addon no Batocera é extremamente simples e rápido:

```bash
# Baixar e executar o instalador
wget -O install.sh https://raw.githubusercontent.com/CarlosTuga/batocera-autodisc/main/install.sh
chmod +x install.sh
./install.sh
```

---

## 👥 Contribuição e Créditos

Desenvolvido por **CarlosTuga** para a comunidade retro gaming. Código aberto licenciado sob a licença MIT.
