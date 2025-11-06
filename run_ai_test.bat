@echo off
chcp 65001 >nul

REM ========================================
REM AI-Powered Mobile Testing Agent
REM ========================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   🤖 AI-Powered Mobile App Testing Agent                  ║
echo ║   Powered by Google Gemini AI                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Set up Android environment
echo [1/4] Setting up Android environment...
set ANDROID_HOME=C:\Users\hasib\AppData\Local\Android\Sdk
set PATH=%ANDROID_HOME%\platform-tools;%PATH%
set PATH=%ANDROID_HOME%\emulator;%PATH%
set PATH=%ANDROID_HOME%\tools;%PATH%
set PATH=%ANDROID_HOME%\build-tools\35.0.0;%PATH%

echo      ✓ ANDROID_HOME = %ANDROID_HOME%
echo.

REM Set Gemini API Key (your key is embedded)
set GEMINI_API_KEY=AIzaSyC41RoUNUYb_q6hJERw99DJr3f-oz2OMRc

REM Check if APK provided
if "%1"=="" (
    echo [ERROR] No APK file provided!
    echo.
    echo Usage: run_ai_test.bat path\to\your\app.apk [options]
    echo.
    echo Examples:
    echo   run_ai_test.bat tests\sample_apks\myapp.apk
    echo   run_ai_test.bat myapp.apk --skip-emulator
    echo   run_ai_test.bat myapp.apk --disable-ai
    echo.
    pause
    exit /b 1
)

REM Check if APK exists
if not exist "%1" (
    echo [ERROR] APK file not found: %1
    echo.
    pause
    exit /b 1
)

echo [2/4] APK file verified: %1
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

echo [3/4] Python installation verified
echo.

REM Check dependencies
echo [4/4] Checking dependencies...
python -c "import google.generativeai" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] AI dependencies not found!
    echo.
    echo Installing required packages...
    pip install google-generativeai
)
echo      ✓ All dependencies ready
echo.

REM Display test information
echo ════════════════════════════════════════════════════════════
echo Test Configuration:
echo ════════════════════════════════════════════════════════════
echo APK File:    %1
echo AI Mode:     ✓ ENABLED (Gemini AI)
echo Options:     %2 %3 %4 %5
echo ════════════════════════════════════════════════════════════
echo.

REM Ask for confirmation
echo Press any key to start AI-powered testing...
pause >nul

echo.
echo ════════════════════════════════════════════════════════════
echo 🚀 Starting AI-Powered Testing...
echo ════════════════════════════════════════════════════════════
echo.

REM Run the AI-powered testing agent
python main.py --apk %1 --ai-key %GEMINI_API_KEY% %2 %3 %4 %5

REM Check exit code
if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo ❌ Testing failed! Check the logs above.
    echo ════════════════════════════════════════════════════════════
) else (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo ✅ Testing completed successfully!
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 📊 Check the reports folder for detailed results
    echo 🧠 AI insights included in the HTML report
    echo.
)

echo.
pause