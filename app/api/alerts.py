"""
Alert API endpoints for Health Monitoring System
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db, Alert, AlertConfiguration
from app.models.schemas import (
    AlertResponse, AlertConfigurationCreate, AlertConfigurationResponse,
    AlertAcknowledge
)
from app.services.alert_service import send_alert_notification

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    patient_id: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build query
        query = db.query(Alert).filter(
            Alert.timestamp >= start_time,
            Alert.timestamp <= end_time
        )
        
        # Apply filters
        if patient_id:
            query = query.filter(Alert.patient_id == patient_id)
        
        if severity:
            query = query.filter(Alert.severity == severity.upper())
        
        # Execute query
        alerts = query.order_by(Alert.timestamp.desc()).all()
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alerts"
        )

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific alert by ID"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert"
        )

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    acknowledge_data: AlertAcknowledge,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        if alert.is_acknowledged:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert already acknowledged"
            )
        
        # Update alert
        alert.is_acknowledged = True
        alert.acknowledged_by = acknowledge_data.acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledge_data.acknowledged_by}")
        return {"message": "Alert acknowledged successfully", "alert": alert}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )

@router.post("/send-test")
async def send_test_alert(
    patient_id: str,
    severity: str = "INFO",
    message: str = "Test alert message",
    db: Session = Depends(get_db)
):
    """Send a test alert for demonstration purposes"""
    try:
        # Create test alert
        test_alert = Alert(
            patient_id=patient_id,
            alert_type="TEST",
            severity=severity.upper(),
            message=message,
            timestamp=datetime.utcnow(),
            is_sent=False
        )
        
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)
        
        # Send notification
        try:
            await send_alert_notification(test_alert)
            test_alert.is_sent = True
            db.commit()
        except Exception as e:
            logger.error(f"Failed to send test alert notification: {e}")
        
        logger.info(f"Test alert sent for patient {patient_id}")
        return {"message": "Test alert sent successfully", "alert": test_alert}
        
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test alert"
        )

@router.get("/configurations/", response_model=List[AlertConfigurationResponse])
async def get_alert_configurations(
    patient_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alert configurations"""
    try:
        query = db.query(AlertConfiguration)
        
        if patient_id:
            query = query.filter(AlertConfiguration.patient_id == patient_id)
        
        configurations = query.all()
        return configurations
        
    except Exception as e:
        logger.error(f"Error fetching alert configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert configurations"
        )

@router.post("/configurations/", response_model=AlertConfigurationResponse)
async def create_alert_configuration(
    config: AlertConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create or update alert configuration"""
    try:
        # Check if configuration already exists
        existing = db.query(AlertConfiguration).filter(
            AlertConfiguration.patient_id == config.patient_id,
            AlertConfiguration.metric_name == config.metric_name
        ).first()
        
        if existing:
            # Update existing configuration
            existing.min_threshold = config.min_threshold
            existing.max_threshold = config.max_threshold
            existing.is_active = config.is_active
            existing.notification_email = config.notification_email
            existing.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new configuration
            new_config = AlertConfiguration(**config.dict())
            db.add(new_config)
            db.commit()
            db.refresh(new_config)
            return new_config
        
    except Exception as e:
        logger.error(f"Error creating alert configuration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert configuration"
        )

@router.get("/statistics/")
async def get_alert_statistics(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get alerts in time range
        alerts = db.query(Alert).filter(
            Alert.timestamp >= start_time,
            Alert.timestamp <= end_time
        ).all()
        
        # Calculate statistics
        total_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.severity == "CRITICAL"])
        warning_alerts = len([a for a in alerts if a.severity == "WARNING"])
        info_alerts = len([a for a in alerts if a.severity == "INFO"])
        
        acknowledged_alerts = len([a for a in alerts if a.is_acknowledged])
        sent_alerts = len([a for a in alerts if a.is_sent])
        
        # Group by patient
        patient_alerts = {}
        for alert in alerts:
            if alert.patient_id not in patient_alerts:
                patient_alerts[alert.patient_id] = 0
            patient_alerts[alert.patient_id] += 1
        
        return {
            "time_range_hours": hours,
            "total_alerts": total_alerts,
            "severity_breakdown": {
                "critical": critical_alerts,
                "warning": warning_alerts,
                "info": info_alerts
            },
            "acknowledged_alerts": acknowledged_alerts,
            "sent_alerts": sent_alerts,
            "alerts_by_patient": patient_alerts,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching alert statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert statistics"
        )
