#!/usr/bin/env python3
"""
Setup script for Health Monitoring System
Day 1: Foundation & Data Pipeline
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthMonitoringSetup:
    """Setup class for Health Monitoring System"""
    
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or Path(__file__).parent
        self.venv_dir = self.project_dir / "venv"
        self.requirements_file = self.project_dir / "requirements.txt"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        logger.info("Checking Python version...")
        
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            return False
        
        logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        logger.info("Creating virtual environment...")
        
        if self.venv_dir.exists():
            logger.info("Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
            logger.info("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_python_executable(self):
        """Get Python executable path"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            return self.venv_dir / "bin" / "python"
    
    def get_pip_executable(self):
        """Get pip executable path"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            return self.venv_dir / "bin" / "pip"
    
    def install_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing dependencies...")
        
        if not self.requirements_file.exists():
            logger.error("Requirements file not found")
            return False
        
        pip_executable = self.get_pip_executable()
        
        try:
            subprocess.run([
                str(pip_executable), "install", "-r", str(self.requirements_file)
            ], check=True)
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("Creating project directories...")
        
        directories = [
            "data",
            "logs",
            "ml/models",
            "backups",
            "frontend/static",
            "frontend/templates"
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        
        return True
    
    def setup_database(self):
        """Initialize database"""
        logger.info("Setting up database...")
        
        python_executable = self.get_python_executable()
        
        try:
            # Import and initialize database
            import sys
            sys.path.insert(0, str(self.project_dir))
            
            from app.database import init_db
            init_db()
            
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def generate_sample_data(self):
        """Generate sample data"""
        logger.info("Generating sample data...")
        
        python_executable = self.get_python_executable()
        script_path = self.project_dir / "scripts" / "generate_sample_data.py"
        
        try:
            subprocess.run([
                str(python_executable), str(script_path)
            ], check=True, cwd=str(self.project_dir))
            
            logger.info("✅ Sample data generated successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate sample data: {e}")
            return False
    
    def setup_cron_jobs(self):
        """Setup cron jobs for automation"""
        logger.info("Setting up cron jobs...")
        
        if os.name == 'nt':  # Windows
            logger.info("⚠️  Cron jobs not supported on Windows. Use Task Scheduler instead.")
            return True
        
        # Create cron job entries
        cron_entries = [
            "# Health Monitoring System - Health Check (every 5 minutes)",
            "*/5 * * * * cd {} && ./scripts/health_check.sh >> logs/health_check.log 2>&1",
            "",
            "# Health Monitoring System - Data Simulation (every minute)",
            "* * * * * cd {} && ./scripts/data_simulator.sh >> logs/data_simulator.log 2>&1",
            "",
            "# Health Monitoring System - Daily Backup (at 2 AM)",
            "0 2 * * * cd {} && ./scripts/backup_data.sh --cleanup 7 >> logs/backup.log 2>&1"
        ]
        
        # Format cron entries with project directory
        formatted_entries = []
        for entry in cron_entries:
            if entry.startswith("#") or entry == "":
                formatted_entries.append(entry)
            else:
                formatted_entries.append(entry.format(self.project_dir))
        
        cron_content = "\n".join(formatted_entries)
        
        # Write to temporary file
        cron_file = self.project_dir / "health_monitoring_cron.txt"
        with open(cron_file, 'w') as f:
            f.write(cron_content)
        
        logger.info(f"✅ Cron job configuration written to: {cron_file}")
        logger.info("To install cron jobs, run: crontab health_monitoring_cron.txt")
        
        return True
    
    def create_startup_script(self):
        """Create startup script"""
        logger.info("Creating startup script...")
        
        python_executable = self.get_python_executable()
        
        if os.name == 'nt':  # Windows
            startup_script = self.project_dir / "start.bat"
            script_content = f"""@echo off
echo Starting Health Monitoring System...
cd /d "{self.project_dir}"
"{python_executable}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
"""
        else:  # Unix/Linux/macOS
            startup_script = self.project_dir / "start.sh"
            script_content = f"""#!/bin/bash
echo "Starting Health Monitoring System..."
cd "{self.project_dir}"
"{python_executable}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
        
        with open(startup_script, 'w') as f:
            f.write(script_content)
        
        if os.name != 'nt':  # Make executable on Unix systems
            os.chmod(startup_script, 0o755)
        
        logger.info(f"✅ Startup script created: {startup_script}")
        return True
    
    def run_tests(self):
        """Run basic tests"""
        logger.info("Running basic tests...")
        
        python_executable = self.get_python_executable()
        
        try:
            # Test database connection
            subprocess.run([
                str(python_executable), "-c", 
                "from app.database import init_db; init_db(); print('Database test passed')"
            ], check=True, cwd=str(self.project_dir))
            
            # Test API import
            subprocess.run([
                str(python_executable), "-c", 
                "from app.main import app; print('API test passed')"
            ], check=True, cwd=str(self.project_dir))
            
            logger.info("✅ Basic tests passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Tests failed: {e}")
            return False
    
    def setup_complete(self):
        """Complete setup process"""
        logger.info("=" * 50)
        logger.info("HEALTH MONITORING SYSTEM SETUP COMPLETE")
        logger.info("=" * 50)
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the system:")
        if os.name == 'nt':
            print("   - Run: start.bat")
        else:
            print("   - Run: ./start.sh")
        print("   - Or: python -m uvicorn app.main:app --reload")
        print("\n2. Access the system:")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
        print("   - Dashboard: http://localhost:8000")
        print("\n3. Generate sample data:")
        print("   - Run: python scripts/generate_sample_data.py")
        print("\n4. Setup automation (optional):")
        print("   - Install cron jobs: crontab health_monitoring_cron.txt")
        print("\n5. Docker deployment (optional):")
        print("   - Run: docker-compose up -d")
        print("\n" + "=" * 50)

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup Health Monitoring System")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-data", action="store_true", help="Skip sample data generation")
    parser.add_argument("--skip-cron", action="store_true", help="Skip cron job setup")
    parser.add_argument("--test-only", action="store_true", help="Run tests only")
    
    args = parser.parse_args()
    
    setup = HealthMonitoringSetup()
    
    if args.test_only:
        return setup.run_tests()
    
    logger.info("Starting Health Monitoring System setup...")
    
    # Run setup steps
    steps = [
        ("Check Python version", setup.check_python_version),
        ("Create virtual environment", setup.create_virtual_environment),
        ("Create directories", setup.create_directories),
    ]
    
    if not args.skip_deps:
        steps.append(("Install dependencies", setup.install_dependencies))
    
    steps.extend([
        ("Setup database", setup.setup_database),
    ])
    
    if not args.skip_data:
        steps.append(("Generate sample data", setup.generate_sample_data))
    
    steps.extend([
        ("Create startup script", setup.create_startup_script),
    ])
    
    if not args.skip_cron:
        steps.append(("Setup cron jobs", setup.setup_cron_jobs))
    
    steps.append(("Run tests", setup.run_tests))
    
    # Execute setup steps
    for step_name, step_func in steps:
        logger.info(f"Step: {step_name}")
        if not step_func():
            logger.error(f"Setup failed at step: {step_name}")
            return False
    
    setup.setup_complete()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
