@echo off
REM Health Monitoring System - Windows Startup Script
REM This script starts the complete system on Windows

echo.
echo ================================================
echo Health Monitoring System - Windows Startup
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [SUCCESS] Python is available

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment found, activating...
    call venv\Scripts\activate.bat
    echo [SUCCESS] Virtual environment activated
) else (
    echo [WARNING] No virtual environment found
    echo [INFO] You may want to create one: python -m venv venv
)

REM Check command line arguments
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--setup" goto :setup
if "%1"=="-s" goto :setup
if "%1"=="--dashboard-only" goto :dashboard
if "%1"=="-d" goto :dashboard
if "%1"=="--api-only" goto :api
if "%1"=="-a" goto :api
if "%1"=="--check" goto :check
if "%1"=="-c" goto :check

REM Default: start complete system
echo [INFO] Starting complete system...
python start_system.py
goto :end

:help
echo.
echo Health Monitoring System - Windows Startup Script
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -h, --help              Show this help message
echo   -s, --setup             Run setup first
echo   -d, --dashboard-only    Start only the Streamlit dashboard
echo   -a, --api-only          Start only the FastAPI backend
echo   -c, --check             Check system status only
echo.
echo Examples:
echo   %0                      # Start both API and dashboard
echo   %0 --setup              # Run setup then start system
echo   %0 --dashboard-only     # Start only dashboard
echo   %0 --api-only           # Start only API
echo   %0 --check              # Check system status
goto :end

:setup
echo [INFO] Running system setup...
python setup.py
if errorlevel 1 (
    echo [ERROR] Setup failed
    pause
    exit /b 1
)
echo [SUCCESS] Setup completed successfully
echo [INFO] Starting system after setup...
python start_system.py
goto :end

:dashboard
echo [INFO] Starting Streamlit dashboard only...
python -c "import sys; import types; imghdr = types.ModuleType('imghdr'); def mock_what(file, h=None): return None; imghdr.what = mock_what; imghdr.test_jpeg = lambda h, f: None; imghdr.test_png = lambda h, f: None; imghdr.test_gif = lambda h, f: None; imghdr.test_bmp = lambda h, f: None; sys.modules['imghdr'] = imghdr; import streamlit.web.cli as stcli; sys.argv = ['streamlit', 'run', 'frontend/dashboard.py', '--server.port', '8501', '--server.address', '0.0.0.0']; stcli.main()"
goto :end

:api
echo [INFO] Starting FastAPI backend only...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
goto :end

:check
echo [INFO] Checking system status...
echo.
echo Checking FastAPI backend...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FastAPI backend is not running
) else (
    echo [SUCCESS] FastAPI backend is running
)

echo.
echo Checking Streamlit dashboard...
curl -s http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Streamlit dashboard is not running
) else (
    echo [SUCCESS] Streamlit dashboard is running
)

echo.
echo Checking database...
if exist "data\health_monitoring.db" (
    echo [SUCCESS] Database exists
) else (
    echo [WARNING] Database not found
)
goto :end

:end
echo.
echo Press any key to exit...
pause >nul
