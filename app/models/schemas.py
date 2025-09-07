"""
Pydantic schemas for Health Monitoring System
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class SeverityLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

# Patient schemas
class PatientBase(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    gender: Gender = Field(..., description="Patient gender")
    medical_history: Optional[str] = Field(None, description="Medical history notes")
    emergency_contact: Optional[str] = Field(None, description="Emergency contact information")

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Vital signs schemas
class VitalSignBase(BaseModel):
    heart_rate: Optional[float] = Field(None, ge=30, le=250, description="Heart rate in BPM")
    spo2: Optional[float] = Field(None, ge=70, le=100, description="Blood oxygen saturation percentage")
    glucose: Optional[float] = Field(None, ge=50, le=500, description="Blood glucose level in mg/dL")
    blood_pressure_systolic: Optional[float] = Field(None, ge=60, le=250, description="Systolic blood pressure")
    blood_pressure_diastolic: Optional[float] = Field(None, ge=40, le=150, description="Diastolic blood pressure")
    temperature: Optional[float] = Field(None, ge=95, le=110, description="Body temperature in Fahrenheit")
    device_id: Optional[str] = Field(None, description="Device identifier")

class VitalSignCreate(VitalSignBase):
    pass

class VitalSignResponse(VitalSignBase):
    id: int
    patient_id: str
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Anomaly schemas
class AnomalyBase(BaseModel):
    anomaly_type: str = Field(..., description="Type of anomaly detected")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of anomaly detection")
    severity: SeverityLevel = Field(..., description="Severity level of the anomaly")
    description: Optional[str] = Field(None, description="Description of the anomaly")
    recommendation: Optional[str] = Field(None, description="Recommended action")

class AnomalyResponse(AnomalyBase):
    id: int
    patient_id: str
    timestamp: datetime
    is_acknowledged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Alert schemas
class AlertBase(BaseModel):
    alert_type: str = Field(..., description="Type of alert")
    severity: SeverityLevel = Field(..., description="Severity level of the alert")
    message: str = Field(..., description="Alert message")

class AlertResponse(AlertBase):
    id: int
    patient_id: str
    timestamp: datetime
    is_sent: bool
    is_acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertAcknowledge(BaseModel):
    acknowledged_by: str = Field(..., description="Person acknowledging the alert")

# Alert configuration schemas
class AlertConfigurationBase(BaseModel):
    patient_id: str = Field(..., description="Patient ID for configuration")
    metric_name: str = Field(..., description="Metric name to configure")
    min_threshold: Optional[float] = Field(None, description="Minimum threshold value")
    max_threshold: Optional[float] = Field(None, description="Maximum threshold value")
    is_active: bool = Field(True, description="Whether configuration is active")
    notification_email: Optional[str] = Field(None, description="Email for notifications")

class AlertConfigurationCreate(AlertConfigurationBase):
    pass

class AlertConfigurationResponse(AlertConfigurationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Patient status schema
class PatientStatus(BaseModel):
    patient_id: str
    name: str
    status: str = Field(..., description="Current patient status")
    latest_vitals: Optional[VitalSignResponse] = None
    recent_anomalies: List[AnomalyResponse] = []
    last_updated: Optional[datetime] = None

# Dashboard schemas
class DashboardOverview(BaseModel):
    total_patients: int
    recent_vitals_count: int
    recent_anomalies_count: int
    recent_alerts_count: int
    critical_alerts_count: int
    unacknowledged_alerts_count: int
    time_range_hours: int
    generated_at: datetime

class VitalsTrend(BaseModel):
    timestamp: str
    value: float

class VitalsTrends(BaseModel):
    heart_rate: List[VitalsTrend]
    spo2: List[VitalsTrend]
    glucose: List[VitalsTrend]
    blood_pressure_systolic: List[VitalsTrend]
    blood_pressure_diastolic: List[VitalsTrend]
    temperature: List[VitalsTrend]

# System health schema
class SystemHealth(BaseModel):
    system_status: str
    database_status: str
    ml_models_status: str
    alert_system_status: str
    generated_at: datetime

# API response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# OAuth token schemas
class OAuthTokenCreate(BaseModel):
    provider: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None

class OAuthTokenResponse(OAuthTokenCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
