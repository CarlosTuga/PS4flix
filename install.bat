@echo off
::==============================================================================
:: RetroBat AutoDisc - Script de Instalação (Windows)
:: Versão: 1.1.0
::==============================================================================
chcp 65001 >nul
echo ===================================================================
echo             RETROBAT AUTODISC - INSTALADOR WINDOWS
echo ===================================================================

:: 1. Verificar se o Python está instalado
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não foi encontrado no PATH do Windows.
    echo Por favor, instale o Python 3 e adicione-o ao PATH durante a instalação.
    pause
    exit /b 1
)

:: 2. Instalar dependências necessárias (PyYAML)
echo [INFO] Instalando dependências (PyYAML)...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [AVISO] Falha ao instalar dependências via pip. Tentando instalar pyyaml diretamente...
    python -m pip install pyyaml --quiet
)

:: 3. Criar atalho no Startup do utilizador do Windows para arranque automático silencioso
echo [INFO] Configurando inicialização automática persistente em segundo plano...
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_PATH=%~dp0autodisc.vbs"
set "SHORTCUT_PATH=%STARTUP_DIR%\RetroBatAutoDisc.lnk"

:: Criar atalho via PowerShell
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%SCRIPT_PATH%'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar o atalho de arranque automático.
    pause
    exit /b 1
)

:: 4. Iniciar imediatamente o monitor em segundo plano
echo [INFO] Iniciando o serviço de monitorização em segundo plano...
wscript.exe "%SCRIPT_PATH%"

echo ===================================================================
echo [SUCESSO] Instalação concluída com sucesso!
echo O AutoDisc foi adicionado ao seu arranque automático do Windows.
echo Por favor, reinicie a consola (RetroBat) para jogar!
echo ===================================================================
pause
