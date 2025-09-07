"""
Dashboard API endpoints for Health Monitoring System
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.database import get_db, Patient, VitalSign, Anomaly, Alert

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get dashboard overview data"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get basic counts
        total_patients = db.query(Patient).count()
        
        # Get recent vital signs count
        recent_vitals = db.query(VitalSign).filter(
            VitalSign.timestamp >= start_time
        ).count()
        
        # Get anomalies count
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.timestamp >= start_time
        ).count()
        
        # Get alerts count
        recent_alerts = db.query(Alert).filter(
            Alert.timestamp >= start_time
        ).count()
        
        # Get critical alerts count
        critical_alerts = db.query(Alert).filter(
            Alert.timestamp >= start_time,
            Alert.severity == "CRITICAL"
        ).count()
        
        # Get unacknowledged alerts
        unacknowledged_alerts = db.query(Alert).filter(
            Alert.timestamp >= start_time,
            Alert.is_acknowledged == False
        ).count()
        
        return {
            "summary": {
                "total_patients": total_patients,
                "recent_vitals_count": recent_vitals,
                "recent_anomalies_count": recent_anomalies,
                "recent_alerts_count": recent_alerts,
                "critical_alerts_count": critical_alerts,
                "unacknowledged_alerts_count": unacknowledged_alerts
            },
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard overview"
        )

@router.get("/patients-status")
async def get_patients_status(
    db: Session = Depends(get_db)
):
    """Get status of all patients"""
    try:
        patients = db.query(Patient).all()
        patients_status = []
        
        for patient in patients:
            # Get latest vital signs
            latest_vitals = db.query(VitalSign).filter(
                VitalSign.patient_id == patient.patient_id
            ).order_by(VitalSign.timestamp.desc()).first()
            
            # Get recent anomalies (last 24 hours)
            recent_anomalies = db.query(Anomaly).filter(
                Anomaly.patient_id == patient.patient_id,
                Anomaly.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).all()
            
            # Determine status
            status = "NORMAL"
            if recent_anomalies:
                critical_anomalies = [a for a in recent_anomalies if a.severity == "CRITICAL"]
                warning_anomalies = [a for a in recent_anomalies if a.severity == "WARNING"]
                
                if critical_anomalies:
                    status = "CRITICAL"
                elif warning_anomalies:
                    status = "WARNING"
                else:
                    status = "INFO"
            
            patients_status.append({
                "patient_id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "status": status,
                "latest_vitals": latest_vitals,
                "anomalies_count": len(recent_anomalies),
                "last_updated": latest_vitals.timestamp if latest_vitals else None
            })
        
        return {
            "patients": patients_status,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching patients status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patients status"
        )

@router.get("/vitals-trends")
async def get_vitals_trends(
    patient_id: str = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get vital signs trends for visualization"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build query
        query = db.query(VitalSign).filter(
            VitalSign.timestamp >= start_time,
            VitalSign.timestamp <= end_time
        )
        
        if patient_id:
            query = query.filter(VitalSign.patient_id == patient_id)
        
        # Get vital signs
        vitals = query.order_by(VitalSign.timestamp.asc()).all()
        
        # Organize data for charts
        trends = {
            "heart_rate": [],
            "spo2": [],
            "glucose": [],
            "blood_pressure_systolic": [],
            "blood_pressure_diastolic": [],
            "temperature": []
        }
        
        for vital in vitals:
            timestamp = vital.timestamp.isoformat()
            
            if vital.heart_rate is not None:
                trends["heart_rate"].append({"timestamp": timestamp, "value": vital.heart_rate})
            
            if vital.spo2 is not None:
                trends["spo2"].append({"timestamp": timestamp, "value": vital.spo2})
            
            if vital.glucose is not None:
                trends["glucose"].append({"timestamp": timestamp, "value": vital.glucose})
            
            if vital.blood_pressure_systolic is not None:
                trends["blood_pressure_systolic"].append({"timestamp": timestamp, "value": vital.blood_pressure_systolic})
            
            if vital.blood_pressure_diastolic is not None:
                trends["blood_pressure_diastolic"].append({"timestamp": timestamp, "value": vital.blood_pressure_diastolic})
            
            if vital.temperature is not None:
                trends["temperature"].append({"timestamp": timestamp, "value": vital.temperature})
        
        return {
            "trends": trends,
            "patient_id": patient_id,
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching vitals trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vitals trends"
        )

@router.get("/anomalies-summary")
async def get_anomalies_summary(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get anomalies summary for dashboard"""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get anomalies
        anomalies = db.query(Anomaly).filter(
            Anomaly.timestamp >= start_time,
            Anomaly.timestamp <= end_time
        ).all()
        
        # Group by severity
        severity_counts = {
            "CRITICAL": 0,
            "WARNING": 0,
            "INFO": 0
        }
        
        # Group by anomaly type
        type_counts = {}
        
        # Group by patient
        patient_counts = {}
        
        for anomaly in anomalies:
            # Count by severity
            severity_counts[anomaly.severity] += 1
            
            # Count by type
            if anomaly.anomaly_type not in type_counts:
                type_counts[anomaly.anomaly_type] = 0
            type_counts[anomaly.anomaly_type] += 1
            
            # Count by patient
            if anomaly.patient_id not in patient_counts:
                patient_counts[anomaly.patient_id] = 0
            patient_counts[anomaly.patient_id] += 1
        
        return {
            "total_anomalies": len(anomalies),
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "patient_breakdown": patient_counts,
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching anomalies summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch anomalies summary"
        )

@router.get("/system-health")
async def get_system_health(
    db: Session = Depends(get_db)
):
    """Get system health metrics"""
    try:
        # Get recent data counts
        recent_vitals = db.query(VitalSign).filter(
            VitalSign.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        recent_alerts = db.query(Alert).filter(
            Alert.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        # Calculate system status
        system_status = "HEALTHY"
        if recent_alerts > 10:  # High alert rate
            system_status = "WARNING"
        if recent_alerts > 20:  # Very high alert rate
            system_status = "CRITICAL"
        
        return {
            "system_status": system_status,
            "metrics": {
                "vitals_per_hour": recent_vitals,
                "anomalies_per_hour": recent_anomalies,
                "alerts_per_hour": recent_alerts
            },
            "database_status": "CONNECTED",
            "ml_models_status": "ACTIVE",
            "alert_system_status": "ACTIVE",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system health"
        )
