"""
Database configuration and models for Health Monitoring System
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/health_monitoring.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class Patient(Base):
    """Patient information model"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    medical_history = Column(Text, nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VitalSign(Base):
    """Vital signs data model"""
    __tablename__ = "vital_signs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    glucose = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Float, nullable=True)
    blood_pressure_diastolic = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    device_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    """Anomaly detection results model"""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    anomaly_type = Column(String(50), nullable=False)  # heart_rate, spo2, glucose, etc.
    confidence_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # INFO, WARNING, CRITICAL
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    """Alert system model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_sent = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertConfiguration(Base):
    """Alert configuration model"""
    __tablename__ = "alert_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    metric_name = Column(String(50), nullable=False)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    notification_email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OAuthToken(Base):
    """OAuth token storage for external integrations"""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), index=True, nullable=False)  # fitbit, withings, etc.
    user_id = Column(String(100), index=True, nullable=False)  # maps to patient_id or admin
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    """Initialize database tables"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default alert configurations
    create_default_alert_configs()

def create_default_alert_configs():
    """Create default alert configurations for common metrics"""
    db = SessionLocal()
    try:
        # Check if configurations already exist
        existing = db.query(AlertConfiguration).first()
        if existing:
            return
        
        # Default thresholds for common metrics
        default_configs = [
            {
                "patient_id": "DEFAULT",
                "metric_name": "heart_rate",
                "min_threshold": 50.0,
                "max_threshold": 120.0,
                "is_active": True
            },
            {
                "patient_id": "DEFAULT",
                "metric_name": "spo2",
                "min_threshold": 90.0,
                "max_threshold": 100.0,
                "is_active": True
            },
            {
                "patient_id": "DEFAULT",
                "metric_name": "glucose",
                "min_threshold": 70.0,
                "max_threshold": 200.0,
                "is_active": True
            },
            {
                "patient_id": "DEFAULT",
                "metric_name": "blood_pressure_systolic",
                "min_threshold": 90.0,
                "max_threshold": 140.0,
                "is_active": True
            },
            {
                "patient_id": "DEFAULT",
                "metric_name": "temperature",
                "min_threshold": 97.0,
                "max_threshold": 99.5,
                "is_active": True
            }
        ]
        
        for config in default_configs:
            alert_config = AlertConfiguration(**config)
            db.add(alert_config)
        
        db.commit()
        print("Default alert configurations created successfully")
        
    except Exception as e:
        print(f"Error creating default alert configurations: {e}")
        db.rollback()
    finally:
        db.close()
