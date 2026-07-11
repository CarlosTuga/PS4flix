# Batocera AutoDisc v1.0.0

**Batocera AutoDisc** é um addon/complemento modular completo e profissional desenvolvido especificamente para o **Batocera Linux v43.1 (x86_64)**. O seu principal objetivo é transformar um PC numa consola de sala de jogos nativa, adicionando suporte completo para a **deteção, identificação lógica e arranque automático de discos originais de consolas** no leitor físico do sistema.

---

## 🎯 Características Principais

* **Deteção Física via udev e Polling:** Serviço daemon em background altamente eficiente que monitoriza inserção de discos em `/dev/sr0`.
* **Identificação de Baixo Nível (RAW):** Lê os primeiros setores físicos (CD-ROM RAW) do leitor para identificar discos híbridos e formatos especiais de consolas retro clássicas (**Sega Saturn**, **Sega CD**, **Sega Dreamcast**).
* **Análise Lógica de Ficheiros de Sistema:** Efetua montagem temporária de volumes UDF/ISO9660 para ler ficheiros como `SYSTEM.CNF` ou `PARAM.SFO` e identificar consolas como **PlayStation 1**, **PlayStation 2**, **PlayStation 3**, **Nintendo GameCube**, **Nintendo Wii**, **Xbox Original** e **Xbox 360**.
* **Extração de Títulos de Jogos:** Parser integrado de baixo nível para extrair nomes de jogos originais (ex: ler títulos de PS3 codificados em UTF-8 dentro de ficheiros SFO).
* **Parâmetros Altamente Otimizados:** Perfis de emuladores configurados especificamente com suporte a **Vulkan**, **Multithreading**, **Speedhacks recomendados** e **Shader Cache** para maximizar o desempenho na combinação de hardware **Intel Core i7-8700** e **NVIDIA GeForce GTX 1060 (3GB)**.
* **Sistema de Notificações OSD:** Notificações em português diretamente no ecrã de utilizador do Batocera ao detetar ou terminar sessões de jogo.
* **Retorno Automático (Clean Loop):** Desativação do rato com `unclutter` ao jogar, fechando o emulador de forma limpa e retornando ao EmulationStation após a sessão.

---

## 📁 Estrutura de Diretórios do Projeto

Este repositório está organizado profissionalmente com os seguintes ficheiros limpos (sem extensões duplicadas):

```text
├── docs/                      # Documentação de referência detalhada em Português
│   ├── configuration.md       # Guia completo de parametrização e opções de perfis
│   └── installation.md        # Manual detalhado de instalação automatizada e manual
├── profiles/                  # Perfis de emuladores otimizados para i7-8700 + GTX 1060
│   ├── dolphin.yaml           # Otimização para GameCube e Wii (Dolphin)
│   ├── duckstation.yaml       # Otimização para PlayStation 1 (DuckStation)
│   ├── flycast.yaml           # Otimização para Sega Dreamcast (Flycast)
│   ├── pcsx2.yaml             # Otimização para PlayStation 2 (PCSX2)
│   ├── ppsspp.yaml            # Otimização para PlayStation Portable (PPSSPP)
│   ├── redream.yaml           # Otimização alternativa para Sega Dreamcast (Redream)
│   ├── rpcs3.yaml             # Otimização para PlayStation 3 (RPCS3)
│   └── xemu.yaml              # Otimização para Xbox Clássica (Xemu)
├── scripts/                   # Utilitários auxiliares de shell script
│   ├── notify.sh              # Script do sistema de notificações visuais no ecrã
│   └── update.sh              # Script de atualização automática do addon e perfis
├── 99-disc-monitor.rules      # Ficheiro de regras udev para integração física
├── config.yaml                # Parametrização geral do leitor e emuladores mapeados
├── disc-launcher.py           # Script lançador otimizado que interpreta os perfis YAML
├── disc-monitor.py            # Daemon de monitorização contínua e identificação de discos
├── disc-monitor.service       # Descritor de serviço Systemd para execução no boot
├── install.sh                 # Script instalador mestre automatizado com verificações de root
├── logger.py                  # Módulo Python centralizado de registos com rotação de 10MB
└── README.md                  # Este ficheiro descritivo mestre
```

---

## 📋 Requisitos de Sistema Recomendados

* **Hardware:**
  * Processador Intel Core i7-8700 (6 Cores / 12 Threads).
  * Placa gráfica dedicada NVIDIA GeForce GTX 1060 3GB.
  * 16 GB de RAM de duplo canal.
  * Leitor ótico SATA (ex: HP PLDS DU8AESH).
* **Software:**
  * Batocera Linux v43.1 (x86_64).

---

## 🚀 Como Instalar

Para instalar de forma completamente automática no seu sistema Batocera, aceda ao terminal de comandos (via SSH ou F1 no menu do Batocera -> Terminal) e execute as seguintes linhas de comando:

```bash
cd /userdata/system
git clone https://github.com/CarlosTuga/batocera-autodisc.git
cd batocera-autodisc
chmod +x install.sh
./install.sh
```

---

## 🛠️ Comandos de Gestão de Serviço Úteis

O addon funciona silenciosamente como um daemon Systemd em background. Pode gerir o seu ciclo de vida utilizando os seguintes comandos no terminal:

```bash
# Validar se o serviço monitor de discos está ativo e operacional
systemctl status disc-monitor.service

# Parar o serviço de monitorização
systemctl stop disc-monitor.service

# Iniciar ou reiniciar o serviço
systemctl restart disc-monitor.service

# Ler o registo de atividade do monitor em tempo real
tail -f /userdata/system/logs/autodisc/disc-monitor.log
```

---

## ⚙️ Configuração Personalizada

Toda a parametrização do serviço pode ser personalizada de forma simples editando o ficheiro YAML de configuração central com um editor de texto (como o `nano`):

```bash
nano /userdata/system/configs/autodisc/config.yaml
```

Para mais detalhes sobre as chaves disponíveis, consulte o manual em `docs/configuration.md`.

---

## 👥 Contribuição e Créditos

Desenvolvido por **CarlosTuga** como um complemento completo e profissional de integração física de leitores de discos para o ecossistema Batocera Linux. Código inteiramente aberto sob licença MIT.
