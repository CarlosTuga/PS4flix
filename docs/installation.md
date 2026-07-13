# Guia de Instalação - RetroBat AutoDisc (Windows)

Este guia descreve detalhadamente o processo de instalação e configuração do addon **RetroBat AutoDisc** no sistema operativo **Windows 10 / 11** para utilização com a interface **RetroBat**.

---

## 1. Pré-requisitos de Sistema

Antes de iniciar a instalação, certifique-se de que cumpre os seguintes requisitos mínimos:

### Requisitos de Software
* **Sistema Operativo:** Windows 10 ou Windows 11 (64-bit).
* **Interface:** RetroBat instalado (ex: em `C:\RetroBat`).
* **Python:** Python 3 instalado e configurado nas variáveis de ambiente (PATH) do Windows.

---

## 2. Instalação Automatizada (Recomendado)

O método mais fácil e rápido consiste em colocar a pasta do addon `batocera-autodisc` em qualquer diretório do seu PC e executar o script de instalação automática:

1. Clique duas vezes no ficheiro `install.bat`.
2. O instalador irá:
   * Verificar se o Python está presente no PATH.
   * Instalar as dependências necessárias via `pip` (como PyYAML).
   * Criar um atalho de inicialização silenciosa (`autodisc.vbs`) na pasta de arranque automático do Windows (`Shell:Startup`).
   * Iniciar de imediato o serviço em segundo plano de forma invisível.

---

## 3. Desinstalação

Se pretender remover por completo o addon do seu computador:

1. Clique duas vezes no ficheiro `uninstall.bat`.
2. O script irá:
   * Terminar todos os processos em segundo plano ativos.
   * Apagar o atalho da pasta de arranque automático do Windows.

---

## 4. Verificação de Funcionamento

Após a instalação, insira um disco de jogo original no seu leitor de DVD/CD do PC. Uma notificação balão (Toast) nativa do Windows será exibida no canto inferior direito do ecrã e o emulador correto será iniciado automaticamente em ecrã inteiro através do RetroBat!
