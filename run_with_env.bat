@echo off
chcp 65001 >nul
REM Temporary Environment Fix - run_with_env.bat
REM Use this until you restart PowerShell

echo Setting up environment variables...

REM Set ANDROID_HOME
set ANDROID_HOME=C:\Users\hasib\AppData\Local\Android\Sdk

REM Add to PATH
set PATH=%ANDROID_HOME%\platform-tools;%PATH%
set PATH=%ANDROID_HOME%\emulator;%PATH%
set PATH=%ANDROID_HOME%\tools;%PATH%
set PATH=%ANDROID_HOME%\build-tools\35.0.0;%PATH%

echo Environment configured!
echo.
echo ANDROID_HOME = %ANDROID_HOME%
echo.

REM Check if APK provided
if "%1"=="" (
    echo Usage: run_with_env.bat your_app.apk
    echo Example: run_with_env.bat tests\sample_apks\myapp.apk
    pause
    exit /b 1
)

REM Run the testing agent
echo Running testing agent...
python main.py --apk %1 %2 %3 %4 %5

pause