#!/usr/bin/env python3
"""
Direct Streamlit Starter with Python 3.13 Compatibility
This script directly patches the missing imghdr module and starts Streamlit
"""

import sys
import types
import os

def patch_imghdr():
    """Patch the missing imghdr module for Python 3.13 compatibility"""
    print("🔧 Patching imghdr module for Python 3.13 compatibility...")
    
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

def main():
    """Main function to start Streamlit"""
    print("🏥 Health Monitoring System - Streamlit Dashboard")
    print("=" * 50)
    
    # Apply the patch
    patch_imghdr()
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Check if dashboard file exists
    dashboard_file = "frontend/dashboard.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return 1
    
    print(f"📊 Starting Streamlit dashboard: {dashboard_file}")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run streamlit directly with imghdr fix
        import streamlit.web.cli as stcli
        
        # Set up the command line arguments for streamlit
        sys.argv = [
            "streamlit", "run", 
            dashboard_file,
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Run streamlit
        stcli.main()
        
    except ImportError as e:
        print(f"❌ Streamlit not found: {e}")
        print("💡 Please install Streamlit:")
        print("   pip install streamlit")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Streamlit stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
