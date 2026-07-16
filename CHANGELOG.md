# Changelog - RetroBat AutoDisc

Todas as alterações e melhorias efetuadas no addon **RetroBat AutoDisc** estão documentadas nesta página.

---

## [v1.1.0-Windows] - Transformação de Arquitetura para Windows e RetroBat

Esta versão marca a **conversão total e transição estável de arquitetura do addon para suporte completo ao Windows 10/11 e à interface RetroBat**.

### 🚀 Novidades e Melhorias no Windows (v1.1.0-Windows)
* **Deteção de Leitores via ctypes:** Substituição de regras udev por varreduras de baixo nível baseadas em chamadas à API `kernel32` do Windows (`GetLogicalDriveStringsW` e `GetDriveTypeW`) para filtrar e selecionar leitores óticos físicos (`DRIVE_CDROM`) em tempo real.
* **Leitura RAW de Baixo Nível via Win32 API:** Implementação de um leitor direto de setores binários de disco utilizando chamadas `CreateFileW` e `ReadFile` da Win32 API. Permite identificar assinaturas de consolas antigas (**Sega Saturn**, **Sega CD**, **Dreamcast**) de forma autónoma e sem dependências externas.
* **Notificações Balloon/Toast Nativas:** Substituição dos scripts bash de notificação por chamadas PowerShell assíncronas e ocultas para disparar alertas e balões nativos no ecrã do Windows de forma elegante.
* **Execução em Segundo Plano Silenciosa:** Launcher `autodisc.vbs` integrado de forma a invocar o monitor de discos usando `pythonw.exe` de forma a ocultar por completo qualquer janela preta de comando terminal CMD.
* **Arranque Automático com o Windows:** Integração com a pasta de arranque do utilizador (`Shell:Startup`) através da criação dinâmica de atalhos VBS via PowerShell, garantindo 100% de persistência após encerramento ou reinicializações do PC.
* **Perfis Completos Otimizados em YAML:** Configurações e perfis individuais YAML para emuladores standalones instalados na diretoria do RetroBat, mapeando caminhos relativos de forma limpa.
* **Fácil Instalação/Desinstalação de Cliques:** Scripts automatizados `install.bat` e `uninstall.bat` que efetuam todas as validações de PATH, instalações de dependências (PyYAML) e limpezas automáticas no Windows de forma rápida e segura.
