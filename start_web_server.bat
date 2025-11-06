@echo off
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   🌐 AI Mobile Testing Agent - Web Interface              ║
echo ║   Starting Backend and Frontend Servers                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Set Android environment
set ANDROID_HOME=C:\Users\hasib\AppData\Local\Android\Sdk
set PATH=%ANDROID_HOME%\platform-tools;%PATH%
set PATH=%ANDROID_HOME%\emulator;%PATH%
set PATH=%ANDROID_HOME%\build-tools\35.0.0;%PATH%

REM Set Gemini API Key
set GEMINI_API_KEY=AIzaSyC41RoUNUYb_q6hJERw99DJr3f-oz2OMRc

echo [1/3] Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing Flask...
    pip install flask flask-cors
)

echo [2/3] Starting Flask Backend Server...
start "AI Testing Backend" cmd /k "python api_server.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting React Frontend...
cd frontend
start "AI Testing Frontend" cmd /k "npm start"
cd ..

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ Servers Started!
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo The frontend should open automatically in your browser.
echo ════════════════════════════════════════════════════════════
echo.
pause