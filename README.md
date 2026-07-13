# RetroBat AutoDisc v1.1.0 (Windows)

**RetroBat AutoDisc** é um addon modular completo e profissional desenvolvido especificamente para o sistema operativo **Windows 10 / 11** para integração com a interface de emulação **RetroBat**.

O seu principal objetivo é transformar qualquer computador de sala ou máquina de jogos retro numa consola de sala autêntica, permitindo a **deteção, identificação lógica e arranque automático de discos originais de consolas físicas** inseridos no leitor de DVD/CD-ROM.

---

## 🎯 Características Principais

* **Deteção nativa do Windows via ctypes:** Monitorização contínua de barramentos de leitores óticos e deteção automática do tipo de drive `DRIVE_CDROM` com suporte a hotplugging e múltiplos leitores.
* **Leitura Física e Assinaturas RAW:** Executa a leitura de setores binários de baixo nível via Win32 API para identificar consolas retro clássicas que usam formatos híbridos de CD/dados (**Sega Saturn**, **Sega CD**, **Sega Dreamcast**).
* **Análise Lógica e Identificação:** Analisa sistemas de ficheiros e assinaturas montadas no Windows para consolas como **PlayStation 1**, **PlayStation 2**, **PlayStation 3**, **Nintendo GameCube**, **Nintendo Wii**, **Xbox Original** e **Xbox 360**.
* **Notificações OSD nativas do Windows:** Utiliza balões de alertas (Toast notifications) nativos do Windows através do PowerShell de forma silenciosa e sem dependências gráficas externas.
* **Inicialização Silenciosa em Segundo Plano:** Executa de forma 100% invisível em segundo plano sem abrir nenhuma janela preta do CMD de sistema utilizando um launcher `autodisc.vbs` acoplado à pasta de arranque do utilizador (`Shell:Startup`).
* **Arranque Seguro com EmulationStation:** O daemon aguarda de forma inteligente que a interface EmulationStation ou o executável `retrobat.exe` estejam ativos antes de iniciar a monitorização ativa de mídias físicas.
* **Perfis Otimizados para GTX 1060 + i7-8700:** Mapeamentos em ficheiros YAML individuais na pasta `configs/` para emuladores standalone como **DuckStation**, **PCSX2**, **Dolphin**, **Flycast**, **Redream**, **Xemu**, **RPCS3** e **PPSSPP** com suporte nativo a Vulkan, multithreading e speedhacks.

---

## 📁 Estrutura de Diretórios do Addon

```text
├── autodisc/                  # Ficheiros e módulos Python do addon
│   ├── config.py              # Leitura de ficheiros de configuração YAML
│   ├── console_detector.py    # Algoritmos de deteção RAW e lógica de consolas
│   ├── disc_detector.py       # Deteção física de leitores óticos via ctypes
│   ├── disc_launcher.py       # Gestão de comandos e execução de emuladores
│   ├── disc_monitor.py        # Loop daemon de background e escuta ativa de processos
│   ├── emulators.py           # Associações e emuladores mapeados
│   ├── installer.py           # Utilitários de instalação
│   ├── logger.py              # Sistema de logs rotativo de 10MB
│   ├── notification.py        # Notificações Toast nativas via PowerShell
│   ├── updater.py             # Utilitários de atualização
│   └── utils.py               # Funções auxiliares do sistema
├── configs/                   # Pasta central de configurações e perfis YAML
│   ├── config.yaml            # Configurações globais de caminhos e leitor
│   ├── ps1.yaml               # Perfil otimizado DuckStation
│   ├── ps2.yaml               # Perfil otimizado PCSX2
│   ├── gamecube.yaml          # Perfil otimizado Dolphin
│   # ... (outros perfis de consolas)
├── docs/                      # Manuais e documentações de referência rápida
│   ├── configuration.md       # Opções e parametrização detalhada do addon
│   └── installation.md        # Manual passo a passo de instalação
├── CHANGELOG.md               # Diário de alterações e melhorias efetuadas
├── autodisc.vbs               # Script launcher silencioso em segundo plano
├── install.bat                # Instalador de cliques automatizado no Windows
├── uninstall.bat              # Desinstalador automático e limpeza do Windows
├── requirements.txt           # Ficheiro de requisitos do Python (PyYAML)
└── README.md                  # Este manual descritivo mestre
```

---

## 🚀 Como Instalar

Instalar o addon no Windows é extremamente simples e rápido:

1. Coloque a pasta do addon `batocera-autodisc` em qualquer local persistente no seu computador.
2. Dê duplo clique no ficheiro `install.bat`.
3. O script tratará de validar o Python, instalar o `PyYAML` e registar o arranque automático silencioso no Windows.
4. Insira um disco original no leitor ótico e desfrute do autoplay completo!

---

## 👥 Contribuição e Créditos

Desenvolvido por **CarlosTuga** para a comunidade retro gaming. Código aberto licenciado sob a licença MIT.
