# 🚀 Quick Start Guide

## Get Started in 5 Minutes

### 1. One-Command Setup & Start (3 minutes)
```bash
# Navigate to project directory
cd health-monitoring-system

# Start everything with one command (includes setup, data generation, and startup)
./start.sh --setup    # Linux/macOS
start.bat --setup     # Windows
```

### 2. Alternative: Manual Setup (5 minutes)
```bash
# Run setup script (creates virtual environment, installs dependencies, initializes database)
python setup.py

# Generate sample data
python scripts/generate_sample_data.py

# Start the complete system
python start_system.py
```

### 3. Access the System (1 minute)
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### 4. Run Demo (1 minute)
```bash
# Run interactive demo
python scripts/demo.py

# Or run UNIX automation scripts
./scripts/health_check.sh
./scripts/data_simulator.sh
```

## 🎯 Demo Scenarios

### Scenario 1: Normal Monitoring
1. Open dashboard at http://localhost:8501
2. View "Dashboard Overview" page
3. Check patient status and vital signs trends

### Scenario 2: Anomaly Detection
1. Run data simulator: `./scripts/data_simulator.sh`
2. Watch for anomaly detection in console
3. Check alerts in dashboard

### Scenario 3: UNIX Automation
1. Run health check: `./scripts/health_check.sh`
2. Start continuous data simulation: `./scripts/data_simulator.sh -c 30`
3. Check logs in `logs/` directory

## 🔧 Key Commands

```bash
# Setup
python setup.py

# Start API
python -m uvicorn app.main:app --reload

# Start Dashboard
streamlit run frontend/dashboard.py

# Generate Data
python scripts/generate_sample_data.py

# Run Demo
python scripts/demo.py

# Health Check
./scripts/health_check.sh

# Data Simulation
./scripts/data_simulator.sh

# Backup
./scripts/backup_data.sh

# Docker (optional)
docker-compose up -d
```

## 📊 What You'll See

### Dashboard Features
- Real-time patient monitoring
- Vital signs visualization
- Anomaly detection alerts
- System health status

### API Features
- Patient management
- Vital signs recording
- Alert system
- Anomaly detection

### Automation Features
- Health monitoring scripts
- Data simulation
- Automated backups
- Cron job scheduling

## 🚨 Troubleshooting

### API Not Responding
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API
python -m uvicorn app.main:app --reload
```

### No Data
```bash
# Generate sample data
python scripts/generate_sample_data.py

# Check database
ls -la data/
```

### Dashboard Issues
```bash
# Restart dashboard
streamlit run frontend/dashboard.py

# Check API connection
curl http://localhost:8000/api/patients/
```

## 🎓 Academic Presentation Points

1. **Architecture**: Modern microservices with FastAPI
2. **AI/ML**: Real-time anomaly detection
3. **Automation**: UNIX scripts and cron jobs
4. **Visualization**: Interactive dashboard
5. **Scalability**: Docker containerization
6. **Monitoring**: Health checks and alerting

## 📈 Performance Metrics

- **API Response Time**: < 1 second
- **ML Inference**: < 1 second
- **Data Processing**: 1000+ records/hour
- **Concurrent Patients**: 10+ patients
- **Uptime**: 95%+ during demo

---

**Ready to demo in 5 minutes! 🎉**
