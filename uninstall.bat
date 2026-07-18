@echo off
::==============================================================================
:: RetroBat AutoDisc - Script de Desinstalação (Windows)
:: Versão: 2.0.0
::==============================================================================
chcp 65001 >nul
echo ===================================================================
echo             RETROBAT AUTODISC - DESINSTALADOR WINDOWS
echo ===================================================================

:: 1. Parar o processo em segundo plano
echo [INFO] Parando o daemon de monitorização ativo...
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RetroBatAutoDisc" >nul 2>&1

:: 2. Remover atalho da pasta de arranque do Windows
echo [INFO] Removendo o atalho da pasta de arranque automático...
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_DIR%\RetroBatAutoDisc.lnk"

if exist "%SHORTCUT_PATH%" (
    del /f /q "%SHORTCUT_PATH%"
    echo [INFO] Atalho removido com sucesso.
) else (
    echo [INFO] Nenhum atalho de arranque automático foi encontrado.
)

echo ===================================================================
echo [SUCESSO] Desinstalação concluída com sucesso!
echo O AutoDisc foi removido por completo do sistema Windows.
echo ===================================================================
pause
