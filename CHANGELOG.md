# Changelog - Batocera AutoDisc

Todas as alterações e melhorias efetuadas no addon **Batocera AutoDisc** estão documentadas nesta página.

---

## [v1.1.0] - Estabilização de Arquitetura e Robustez Nativa (Versão Estável)

Esta versão foi totalmente revista e redesenhada para garantir máxima estabilidade e funcionamento ininterrupto de leitura ótica nas versões **v43.1** e **v44** do **Batocera Linux (x86_64)**.

### 🚀 Novas Funcionalidades e Correções de Bugs (v1.1.0)
* **Deteção de Discos de Baixo Nível via ioctl:** Substituição total da dependência de executáveis externos em falta (como `setcd`) por chamadas nativas ao kernel do Linux (`fcntl.ioctl` com as constantes `CDROM_DRIVE_STATUS` e `CDS_DISC_OK`). Evita tracebacks e loops de erros infinitos na presença de gavetas vazias.
* **Arranque Persistente e Automatizado:** Configuração cirúrgica de arranque nativo persistente através do script oficial de carregamento do utilizador `/userdata/system/custom.sh`. Corrige a ineficácia de registo de serviços systemd na pasta RAM virtual do Batocera que causava a perda completa do addon após reboots.
* **Deteção Inteligente de Variáveis Gráficas:** Parser integrado para ler de forma em tempo real o ambiente do processo do EmulationStation via `/proc/$(pidof emulationstation)/environ`, herdando corretamente as variáveis `DISPLAY`, `WAYLAND_DISPLAY`, `XAUTHORITY` e `XDG_RUNTIME_DIR`. Permite que emuladores gráficos e avisos OSD funcionem perfeitamente tanto no servidor gráfico **X11** como no moderno **Wayland (Sway)** (introduzido no Batocera v39+ e estendido na v44).
* **Varredura Dinâmica de Múltiplos Leitores:** Pesquisa ativa de dispositivos óticos sob o barramento `/dev/sr*` e ligação simbólica `/dev/cdrom`. Seleciona de forma dinâmica o leitor físico que tiver o disco inserido no momento, suportando reconfigurações a quente.
* **EmulationStation Boot-Safe Watcher:** O monitor daemon aguarda de forma inteligente que o EmulationStation esteja ativo e completamente carregado antes de iniciar varreduras de leitura física, prevenindo conflitos gráficos no boot.
* **Migração Completa para JSON (Zero-Dependency):** Substituição total de todos os ficheiros YAML e da biblioteca terceira `PyYAML` pela biblioteca nativa do Python `json`. Garante execução out-of-the-box instantânea sem necessidade de instalações adicionais no sistema de ficheiros read-only do Batocera.
* **Bypass Seguro do EmulatorLauncher:** Os emuladores standalone de leitores físicos são agora invocados diretamente através de comandos e parâmetros nativos com argumentos do leitor (`--disc`, `-disc`, `-dvd_path`), resolvendo falhas do wrapper `emulatorlauncher` nativo do Batocera ao receber dispositivos de bloco `/dev/sr*`.
* **Segurança e Robustez nos Parâmetros de Lançamento:** Remoção absoluta do comando `-set` não-suportado na CLI do DuckStation-Qt, corrigindo falhas de inicialização do PS1.
* **Salvaguarda do cursor do rato:** Desativação segura das chamadas do utilitário X11 `unclutter` em ambientes Wayland puro para evitar tracebacks ou falhas silenciosas.

### 📦 Melhorias no Instalador (`install.sh`)
* **Logging simultâneo:** Registo completo de auditoria física de todas as mensagens e etapas de instalação salvas em `/userdata/system/logs/autodisc/install.log`.
* **Cópia de Segurança Automatizada:** Cópia de segurança física e instantânea de qualquer instalação ou perfil pré-existente antes de iniciar a cópia do pacote.
* **Rollback Automático integrado:** Em caso de falhas mecânicas ou erros de escrita de disco a meio do processo, o script reverte imediatamente o sistema para o estado estável anterior ao arranque do script.
* **Injeção de Hooks Cirúrgica e Segura:** Utiliza interpretador Python para ler `/userdata/system/custom.sh` e injetar os blocos de boot de forma estritamente segura antes de qualquer instrução do sistema como `exit 0`, prevenindo que os hooks fiquem inacessíveis.
* **Opção de Desinstalação limpa:** Suporte completo de limpeza do sistema através da passagem do argumento `uninstall`, `--uninstall` ou `-u` ao script `install.sh`. Limpa todos os ficheiros, udev rules e remove cirurgicamente os hooks do ficheiro `custom.sh`.
* **Notificação OSD de conclusão:** Dispara um alerta sonoro e de ecrã instantâneo após a conclusão informando que a instalação terminou com sucesso e solicita o reinício da consola.

---

## [v1.0.0] - Lançamento Inicial (Fase 1)
* Daemon inicial de monitorização física do leitor `/dev/sr0`.
* Suporte inicial a perfis otimizados YAML de emuladores para i7-8700 + GTX 1060 3GB.
* Integração base de regras udev e serviço systemd.
* Sistema de notificações amigáveis OSD em português.
