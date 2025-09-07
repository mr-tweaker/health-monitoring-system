#!/usr/bin/env python3
"""
Health Monitoring System - Complete Startup Script
This script starts both the FastAPI backend and Streamlit dashboard with Python 3.13 compatibility
"""

import sys
import types
import os
import subprocess
import time
import signal
import threading
from pathlib import Path
from typing import Dict

# Global variables to track processes
api_process = None
dashboard_process = None

def patch_imghdr():
    """Patch the missing imghdr module for Python 3.13 compatibility"""
    print("🔧 Applying Python 3.13 compatibility fixes...")
    
    # Create mock imghdr module
    imghdr = types.ModuleType('imghdr')
    
    def mock_what(file, h=None):
        """Mock function that returns None (no image type detected)"""
        return None
    
    def mock_test_jpeg(h, f):
        return None
    
    def mock_test_png(h, f):
        return None
    
    def mock_test_gif(h, f):
        return None
    
    def mock_test_bmp(h, f):
        return None
    
    def mock_test_tiff(h, f):
        return None
    
    def mock_test_webp(h, f):
        return None
    
    # Add all the functions to the module
    imghdr.what = mock_what
    imghdr.test_jpeg = mock_test_jpeg
    imghdr.test_png = mock_test_png
    imghdr.test_gif = mock_test_gif
    imghdr.test_bmp = mock_test_bmp
    imghdr.test_tiff = mock_test_tiff
    imghdr.test_webp = mock_test_webp
    imghdr.__version__ = "1.0.0"
    
    # Install in sys.modules
    sys.modules['imghdr'] = imghdr
    print("✅ imghdr module patched successfully")

def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load simple KEY=VALUE lines from an env file into os.environ"""
    if not env_path.exists():
        return {}
    loaded = {}
    try:
        with env_path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
                    loaded[key] = value
        print(f"✅ Loaded env from {env_path}")
    except Exception as e:
        print(f"⚠️  Failed to load env file {env_path}: {e}")
    return loaded

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['fastapi', 'uvicorn', 'streamlit', 'sqlalchemy', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Please install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are available")
    return True

def check_database():
    """Check if database exists and has data"""
    print("🔍 Checking database...")
    
    db_path = Path("data/health_monitoring.db")
    if not db_path.exists():
        print("  ⚠️  Database not found")
        print("  💡 Run 'python scripts/generate_sample_data.py' to create sample data")
        return False
    
    print("  ✅ Database exists")
    return True

def start_fastapi():
    """Start the FastAPI backend"""
    global api_process
    
    print("🚀 Starting FastAPI backend...")
    
    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        api_log = open("logs/api.out", "ab", buffering=0)

        # Use system python to avoid AppImage/Qt issues
        system_python = "/usr/bin/python3"

        # Prepare environment (force offscreen to avoid Qt/Wayland issues)
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = env.get("QT_QPA_PLATFORM", "offscreen")

        # Inline Python that imports app and runs uvicorn directly
        inline_code = (
            "import sys, os; "
            "sys.path.insert(0, os.getcwd()); "
            "sys.path.insert(0, os.path.join(os.getcwd(), 'venv', 'lib', 'python3.13', 'site-packages')); "
            "from app.main import app; import uvicorn; "
            "uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')"
        )

        api_process = subprocess.Popen(
            [system_python, "-c", inline_code],
            stdout=api_log,
            stderr=api_log,
            env=env,
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if api_process.poll() is None:
            print("  ✅ FastAPI backend started successfully")
            print("  🌐 API available at: http://localhost:8000")
            print("  📚 API docs at: http://localhost:8000/docs")
            return True
        else:
            print(f"  ❌ FastAPI failed to start")
            try:
                with open("logs/api.out", "rb") as f:
                    last = f.read().decode(errors="ignore").splitlines()[-20:]
                    print("\n".join(last))
            except Exception:
                pass
            return False
            
    except Exception as e:
        print(f"  ❌ Error starting FastAPI: {e}")
        return False

def start_streamlit():
    """Start the Streamlit dashboard with imghdr fix"""
    global dashboard_process
    
    print("🚀 Starting Streamlit dashboard...")
    
    try:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        dash_log = open("logs/dashboard.out", "ab", buffering=0)

        # Use system python with imghdr patch and headless flags
        system_python = "/usr/bin/python3"

        inline_code = (
            "import sys, types, os; "
            "imghdr = types.ModuleType('imghdr'); "
            "imghdr.what = lambda *a, **k: None; "
            "imghdr.test_jpeg = imghdr.test_png = imghdr.test_gif = imghdr.test_bmp = imghdr.test_tiff = imghdr.test_webp = (lambda *a, **k: None); "
            "sys.modules['imghdr'] = imghdr; "
            "import streamlit.web.cli as stcli; "
            "sys.argv = ['streamlit','run','frontend/dashboard.py','--server.port','8501','--server.address','0.0.0.0','--server.headless','true','--browser.gatherUsageStats','false']; "
            "stcli.main()"
        )

        dashboard_process = subprocess.Popen(
            [system_python, "-c", inline_code],
            stdout=dash_log,
            stderr=dash_log,
        )
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Check if process is still running
        if dashboard_process.poll() is None:
            print("  ✅ Streamlit dashboard started successfully")
            print("  🌐 Dashboard available at: http://localhost:8501")
            return True
        else:
            print(f"  ❌ Streamlit failed to start")
            try:
                with open("logs/dashboard.out", "rb") as f:
                    last = f.read().decode(errors="ignore").splitlines()[-20:]
                    print("\n".join(last))
            except Exception:
                pass
            return False
            
    except Exception as e:
        print(f"  ❌ Error starting Streamlit: {e}")
        return False

def check_api_health():
    """Check if API is responding"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def wait_for_api():
    """Wait for API to be ready"""
    print("⏳ Waiting for API to be ready...")
    
    for i in range(30):  # Wait up to 30 seconds
        if check_api_health():
            print("  ✅ API is ready")
            return True
        time.sleep(1)
        print(f"  ⏳ Waiting... ({i+1}/30)")
    
    print("  ❌ API did not become ready in time")
    return False

def cleanup_processes():
    """Clean up running processes"""
    global api_process, dashboard_process
    
    print("\n🛑 Shutting down services...")
    
    if api_process and api_process.poll() is None:
        print("  Stopping FastAPI...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
    
    if dashboard_process and dashboard_process.poll() is None:
        print("  Stopping Streamlit...")
        dashboard_process.terminate()
        try:
            dashboard_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            dashboard_process.kill()
    
    print("  ✅ All services stopped")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Received interrupt signal...")
    cleanup_processes()
    sys.exit(0)

def monitor_processes():
    """Monitor processes and restart if needed"""
    global api_process, dashboard_process
    
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        # Check API process
        if api_process and api_process.poll() is not None:
            print("⚠️  FastAPI process died, attempting restart...")
            if start_fastapi():
                wait_for_api()
        
        # Check Streamlit process
        if dashboard_process and dashboard_process.poll() is not None:
            print("⚠️  Streamlit process died, attempting restart...")
            start_streamlit()

def main():
    """Main startup function"""
    print("🏥 Health Monitoring System - Complete Startup")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Load env/dev.env if present
    load_env_file(project_dir / "env" / "dev.env")
    
    # Apply compatibility fixes
    patch_imghdr()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return 1
    
    # Check database
    check_database()
    
    # Start FastAPI
    if not start_fastapi():
        print("\n❌ Failed to start FastAPI backend")
        return 1
    
    # Wait for API to be ready
    if not wait_for_api():
        print("\n❌ API did not become ready")
        cleanup_processes()
        return 1
    
    # Start Streamlit
    if not start_streamlit():
        print("\n❌ Failed to start Streamlit dashboard")
        cleanup_processes()
        return 1
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 Health Monitoring System is now running!")
    print("=" * 60)
    print("🌐 Services:")
    print("  • FastAPI Backend: http://localhost:8000")
    print("  • API Documentation: http://localhost:8000/docs")
    print("  • Streamlit Dashboard: http://localhost:8501")
    print("  • Health Check: http://localhost:8000/health")
    print("\n📊 Demo Scripts:")
    print("  • Run demo: python scripts/demo.py")
    print("  • Health check: ./scripts/health_check.sh")
    print("  • Data simulator: ./scripts/data_simulator.sh")
    print("\n🛑 Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes()
    
    return 0

if __name__ == "__main__":
    exit(main())
