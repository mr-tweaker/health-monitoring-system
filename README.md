# 🏥 AI-Powered Health Monitoring System

A comprehensive health monitoring system with real-time anomaly detection, alert management, and UNIX automation for academic demonstration.

## 📋 Project Overview

This project demonstrates a complete health monitoring system built for a 4-day sprint, featuring:

- **Real-time Health Monitoring**: Continuous monitoring of vital signs
- **AI-Powered Anomaly Detection**: Machine learning models for detecting health anomalies
- **Alert System**: Automated alerts with email notifications
- **UNIX Automation**: Cron jobs and shell scripts for system automation
- **Web Dashboard**: Interactive dashboard for visualization and monitoring
- **REST API**: Complete API for data ingestion and retrieval

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher (tested with Python 3.13)
- Docker (optional)
- Git

### One-Command Setup

```bash
# Start everything with one command
./start.sh --setup    # Linux/macOS
start.bat --setup     # Windows
```

**See [STARTUP_GUIDE.md](STARTUP_GUIDE.md) for detailed instructions.**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-monitoring-system
   ```

2. **Quick Start (Recommended)**
   ```bash
   # Linux/macOS
   ./start.sh --setup
   
   # Windows
   start.bat --setup
   
   # Or using Python directly
   python start_system.py
   ```

3. **Manual Setup (Alternative)**
   ```bash
   # Run the setup script
   python setup.py
   
   # Start the system
   ./start.sh  # Linux/macOS
   start.bat   # Windows
   ```

4. **Generate sample data**
   ```bash
   python scripts/generate_sample_data.py
   ```

5. **Access the system**
   - API Documentation: http://localhost:8000/docs
   - Dashboard: http://localhost:8501
   - Health Check: http://localhost:8000/health

## 🏗️ Architecture

```
health-monitoring-system/
├── app/                        # Main FastAPI application
│   ├── api/                    # API endpoints
│   │   ├── patients.py         # Patient management
│   │   ├── alerts.py           # Alert system
│   │   └── dashboard.py        # Dashboard data
│   ├── models/                 # Data models and schemas
│   ├── services/               # Business logic
│   │   ├── anomaly_detection.py # ML anomaly detection
│   │   └── alert_service.py    # Alert management
│   ├── database.py             # Database configuration
│   └── main.py                 # FastAPI application
├── scripts/                    # UNIX automation scripts
│   ├── health_check.sh         # System health monitoring
│   ├── data_simulator.sh       # Continuous data generation
│   └── backup_data.sh          # Data backup automation
├── frontend/                   # Streamlit dashboard
├── data/                       # Database and data files
├── ml/                         # Machine learning models
├── docker/                     # Docker configuration
└── docs/                       # Documentation
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database for development
- **Pydantic**: Data validation using Python type annotations

### Machine Learning
- **TensorFlow/Keras**: Deep learning framework
- **Scikit-learn**: Machine learning library
- **NumPy/Pandas**: Data manipulation and analysis

### Frontend
- **Streamlit**: Interactive web dashboard
- **Plotly**: Interactive data visualization

### Automation
- **Bash Scripts**: UNIX automation
- **Cron Jobs**: Scheduled task automation
- **Docker**: Containerization

## 📊 Features

### Core Features
- ✅ **Patient Management**: Add, view, and manage patients
- ✅ **Vital Signs Monitoring**: Real-time vital signs tracking
- ✅ **Anomaly Detection**: AI-powered anomaly detection
- ✅ **Alert System**: Automated alerts with notifications
- ✅ **Dashboard**: Interactive web dashboard
- ✅ **REST API**: Complete API for all operations

### Automation Features
- ✅ **Health Checks**: Automated system health monitoring
- ✅ **Data Simulation**: Continuous synthetic data generation
- ✅ **Backup System**: Automated data backup
- ✅ **Cron Jobs**: Scheduled automation tasks

### Demo Features
- ✅ **Sample Data**: Realistic synthetic health data
- ✅ **Visualization**: Interactive charts and graphs
- ✅ **Real-time Updates**: Live data updates
- ✅ **Alert Notifications**: Console and email alerts

## 🎯 4-Day Implementation Plan

### Day 1: Foundation & Data Pipeline
- [x] Project setup and structure
- [x] Database configuration
- [x] Basic FastAPI application
- [x] Synthetic data generation
- [x] Docker setup

### Day 2: ML Models & Core API
- [x] Anomaly detection models
- [x] ML pipeline implementation
- [x] Core API endpoints
- [x] Alert logic implementation

### Day 3: Alerts & UNIX Automation
- [x] Alert system with notifications
- [x] UNIX automation scripts
- [x] Cron job setup
- [x] Integration testing

### Day 4: Demo Dashboard & Documentation
- [x] Interactive dashboard
- [x] Data visualization
- [x] Documentation
- [x] Demo preparation

## 🚨 Alert System

The system includes a comprehensive alert system with:

### Alert Types
- **INFO**: Informational alerts
- **WARNING**: Warning-level alerts requiring attention
- **CRITICAL**: Critical alerts requiring immediate action

### Alert Triggers
- **Threshold Violations**: Values outside normal ranges
- **Statistical Anomalies**: Unusual patterns in data
- **System Issues**: System health problems

### Notification Methods
- **Console Alerts**: Real-time console notifications
- **Email Notifications**: Email alerts (demo implementation)
- **Dashboard Alerts**: Visual alerts in the dashboard

## 🔄 UNIX Automation

### Automation Scripts

1. **Health Check Script** (`scripts/health_check.sh`)
   - Monitors system health
   - Checks API availability
   - Verifies database connectivity
   - Generates health reports

2. **Data Simulator Script** (`scripts/data_simulator.sh`)
   - Generates continuous synthetic data
   - Simulates real-time vital signs
   - Includes anomaly generation for testing

3. **Backup Script** (`scripts/backup_data.sh`)
   - Automated data backup
   - Database backup
   - Log file backup
   - Configuration backup

### Cron Jobs
```bash
# Health check every 5 minutes
*/5 * * * * cd /path/to/project && ./scripts/health_check.sh

# Data simulation every minute
* * * * * cd /path/to/project && ./scripts/data_simulator.sh

# Daily backup at 2 AM
0 2 * * * cd /path/to/project && ./scripts/backup_data.sh --cleanup 7
```

## 📈 API Endpoints

### Patient Management
- `GET /api/patients/` - Get all patients
- `POST /api/patients/` - Create new patient
- `GET /api/patients/{id}` - Get specific patient
- `POST /api/patients/{id}/vitals` - Record vital signs
- `GET /api/patients/{id}/vitals` - Get vital signs history

### Alert System
- `GET /api/alerts/` - Get alerts
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `GET /api/alerts/statistics/` - Get alert statistics

### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/patients-status` - Patients status
- `GET /api/dashboard/vitals-trends` - Vital signs trends

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services
- **API**: FastAPI application (port 8000)
- **Dashboard**: Streamlit dashboard (port 8501)
- **Redis**: Caching and queuing (port 6379)
- **NGINX**: Reverse proxy (port 80)

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Test Data
```bash
# Generate test data
python scripts/generate_sample_data.py

# Run data simulation
./scripts/data_simulator.sh

# Test health check
./scripts/health_check.sh
```

## 📊 Sample Data

The system includes realistic synthetic data:

### Patient Data
- 5 sample patients with different profiles
- Realistic medical histories
- Emergency contact information

### Vital Signs Data
- 48 hours of data per patient
- 15-minute intervals
- Realistic circadian rhythms
- Built-in anomalies for testing

### Anomaly Examples
- High/low heart rate
- Low oxygen saturation
- High/low blood glucose
- Hypertension episodes

## 🎯 Demo Scenarios

### Scenario 1: Normal Monitoring
1. Start the system
2. View dashboard overview
3. Check patient status
4. Monitor vital signs trends

### Scenario 2: Anomaly Detection
1. Generate sample data with anomalies
2. Observe anomaly detection in action
3. Check alert generation
4. View anomaly details

### Scenario 3: Alert Management
1. Trigger test alerts
2. View alert notifications
3. Acknowledge alerts
4. Check alert statistics

### Scenario 4: UNIX Automation
1. Run health check script
2. Start data simulation
3. Check cron job logs
4. Verify backup system

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./data/health_monitoring.db
LOG_LEVEL=INFO
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

### Alert Thresholds
```python
DEFAULT_THRESHOLDS = {
    "heart_rate": {"min": 50, "max": 120},
    "spo2": {"min": 90, "max": 100},
    "glucose": {"min": 70, "max": 200},
    "blood_pressure_systolic": {"min": 90, "max": 140},
    "temperature": {"min": 97, "max": 99.5}
}
```

## 📚 Documentation

### API Documentation
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

### Code Documentation
- Inline code comments
- Type hints throughout
- Docstrings for all functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is created for academic demonstration purposes.

## 🎓 Academic Context

This project demonstrates:
- **Modern Software Development**: FastAPI, Docker, CI/CD
- **AI/ML Integration**: Real-time anomaly detection
- **UNIX Automation**: Shell scripts and cron jobs
- **System Architecture**: Microservices, APIs, databases
- **Data Visualization**: Interactive dashboards
- **DevOps Practices**: Automation, monitoring, backup

## 🚀 Future Enhancements

- Real Fitbit API integration
- Advanced ML models (LSTM, CNN)
- Mobile application
- Real-time WebSocket updates
- Advanced alert escalation
- Machine learning model training pipeline
- Multi-tenant support
- Advanced analytics and reporting

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review the API docs
3. Check the logs in `logs/` directory
4. Run health check script

---

**Built with ❤️ for academic demonstration**
