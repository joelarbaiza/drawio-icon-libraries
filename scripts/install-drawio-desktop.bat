@echo off
rem Instala o actualiza las librerias de drawio-icon-libraries en Draw.io de escritorio (Windows).
rem Uso: doble clic. Ejecuta install-drawio-desktop.ps1 (junto a este archivo) con las librerias
rem de esta misma carpeta, sin cambiar la politica de ejecucion de PowerShell del equipo.
rem Para opciones avanzadas (-Library, -InstallDir...) ejecuta el .ps1 desde PowerShell.
setlocal
set "HERE=%~dp0"
if not exist "%HERE%install-drawio-desktop.ps1" (
    echo No se encuentra install-drawio-desktop.ps1 junto a este archivo.
    echo Descomprime el ZIP completo y vuelve a intentarlo.
    pause
    exit /b 1
)
rem Se lee como UTF-8 y se ejecuta como bloque: Windows PowerShell 5.1 leeria mal las tildes con -File.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$s = [IO.File]::ReadAllText('%HERE%install-drawio-desktop.ps1', [Text.Encoding]::UTF8); & ([scriptblock]::Create($s)) -Source '%HERE%.'"
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%
