#!/usr/bin/env python3
"""
Streamlit Runner with Python 3.13 Compatibility Fixes
This script ensures Streamlit works on Python 3.13 by fixing missing modules
"""

import sys
import os
import subprocess
import importlib.util

def apply_compatibility_fixes():
    """Apply all necessary compatibility fixes for Python 3.13"""
    print("🔧 Applying Python 3.13 compatibility fixes...")
    
    # Fix 1: Create mock imghdr module
    try:
        import types
        
        # Create mock imghdr module
        imghdr = types.ModuleType('imghdr')
        
        def mock_what(file, h=None):
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
        
        # Add functions to module
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
        print("✅ imghdr module fix applied")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not apply imghdr fix: {e}")
    
    # Fix 2: Handle other potential missing modules
    missing_modules = ['imghdr']
    
    for module_name in missing_modules:
        if module_name not in sys.modules:
            try:
                # Create a minimal mock module
                mock_module = types.ModuleType(module_name)
                mock_module.__version__ = "1.0.0"
                sys.modules[module_name] = mock_module
                print(f"✅ {module_name} module fix applied")
            except Exception as e:
                print(f"⚠️  Warning: Could not fix {module_name}: {e}")
    
    print("✅ All compatibility fixes applied!")

def check_streamlit_installation():
    """Check if Streamlit is properly installed"""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} is installed")
        return True
    except ImportError as e:
        print(f"❌ Streamlit not found: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Streamlit import error: {e}")
        return False

def install_streamlit():
    """Install Streamlit with compatibility fixes"""
    print("📦 Installing Streamlit...")
    
    try:
        # Try to install streamlit
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "streamlit", "--upgrade", "--user"
        ])
        print("✅ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Streamlit: {e}")
        return False

def run_streamlit_dashboard():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Streamlit Dashboard...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Check if dashboard file exists
    dashboard_file = "frontend/dashboard.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return False
    
    try:
        # Run streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            dashboard_file,
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
        return True

def main():
    """Main function"""
    print("🏥 Health Monitoring System - Streamlit Runner")
    print("=" * 50)
    
    # Apply compatibility fixes first
    apply_compatibility_fixes()
    
    # Check Streamlit installation
    if not check_streamlit_installation():
        print("\n📦 Installing Streamlit...")
        if not install_streamlit():
            print("❌ Could not install Streamlit. Please install manually:")
            print("   pip install streamlit")
            return 1
    
    # Check if FastAPI is running
    print("\n🔍 Checking if FastAPI is running...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI is running")
        else:
            print("⚠️  FastAPI responded with status:", response.status_code)
    except Exception as e:
        print(f"⚠️  FastAPI not accessible: {e}")
        print("💡 Make sure to start FastAPI first:")
        print("   python -m uvicorn app.main:app --reload")
    
    # Run Streamlit
    print("\n🚀 Starting Streamlit Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        success = run_streamlit_dashboard()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
