#!/usr/bin/env python3
"""
Streamlit Dashboard Runner with Python 3.13 Compatibility Fix
"""

# Apply the imghdr fix before importing streamlit
import sys
import types

def create_mock_imghdr():
    """Create a mock imghdr module for Python 3.13 compatibility"""
    imghdr = types.ModuleType('imghdr')
    
    def mock_what(file, h=None):
        return None
    
    imghdr.what = mock_what
    imghdr.test_jpeg = lambda h, f: None
    imghdr.test_png = lambda h, f: None
    imghdr.test_gif = lambda h, f: None
    imghdr.test_bmp = lambda h, f: None
    
    return imghdr

# Install the mock module
if 'imghdr' not in sys.modules:
    sys.modules['imghdr'] = create_mock_imghdr()

# Now we can safely import streamlit
import streamlit as st
import subprocess
import os

def main():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Health Monitoring Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔧 Applied Python 3.13 compatibility fix")
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0

if __name__ == "__main__":
    exit(main())
