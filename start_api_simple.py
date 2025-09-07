#!/usr/bin/env python3
"""
Simple API startup script that bypasses the virtual environment issues
"""

import sys
import os
import subprocess
import time

def main():
    print("🚀 Starting Health Monitoring System API...")
    
    # Add current directory and venv packages to Python path
    current_dir = os.getcwd()
    venv_site_packages = os.path.join(current_dir, 'venv', 'lib', 'python3.13', 'site-packages')
    
    sys.path.insert(0, current_dir)
    sys.path.insert(0, venv_site_packages)
    
    try:
        # Import and run the app
        from app.main import app
        import uvicorn
        
        print("✅ FastAPI app imported successfully")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs available at http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Start the server
        uvicorn.run(
            app, 
            host='0.0.0.0', 
            port=8000, 
            log_level='info',
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
