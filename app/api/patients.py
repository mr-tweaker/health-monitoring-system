"""
Patient API endpoints for Health Monitoring System
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db, Patient, VitalSign, Anomaly
from app.models.schemas import (
    PatientCreate, PatientResponse, VitalSignCreate, VitalSignResponse,
    AnomalyResponse, PatientStatus
)
from app.services.anomaly_detection import detect_anomalies
from app.services.alert_service import check_and_create_alerts

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient"""
    try:
        # Check if patient already exists
        existing_patient = db.query(Patient).filter(
            Patient.patient_id == patient.patient_id
        ).first()
        
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this ID already exists"
            )
        
        # Create new patient
        db_patient = Patient(**patient.dict())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        logger.info(f"Created new patient: {patient.patient_id}")
        return db_patient
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all patients"""
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        return patients
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patients"
        )

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific patient by ID"""
    try:
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient"
        )

@router.post("/{patient_id}/vitals", response_model=VitalSignResponse)
async def record_vital_signs(
    patient_id: str,
    vitals: VitalSignCreate,
    db: Session = Depends(get_db)
):
    """Record vital signs for a patient"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Create vital signs record
        vitals_data = vitals.dict()
        vitals_data["patient_id"] = patient_id
        vitals_data["timestamp"] = datetime.utcnow()
        
        db_vitals = VitalSign(**vitals_data)
        db.add(db_vitals)
        db.commit()
        db.refresh(db_vitals)
        
        # Run anomaly detection
        try:
            anomalies = await detect_anomalies(patient_id, vitals_data, db)
            if anomalies:
                logger.info(f"Detected {len(anomalies)} anomalies for patient {patient_id}")
                
                # Check for alerts
                await check_and_create_alerts(patient_id, anomalies, db)
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
        
        logger.info(f"Recorded vital signs for patient {patient_id}")
        return db_vitals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording vital signs: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record vital signs"
        )

@router.get("/{patient_id}/vitals", response_model=List[VitalSignResponse])
async def get_vital_signs(
    patient_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get vital signs for a patient within specified hours"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get vital signs
        vitals = db.query(VitalSign).filter(
            VitalSign.patient_id == patient_id,
            VitalSign.timestamp >= start_time,
            VitalSign.timestamp <= end_time
        ).order_by(VitalSign.timestamp.desc()).all()
        
        return vitals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vital signs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vital signs"
        )

@router.get("/{patient_id}/current-status", response_model=PatientStatus)
async def get_current_status(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get current status of a patient"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get latest vital signs
        latest_vitals = db.query(VitalSign).filter(
            VitalSign.patient_id == patient_id
        ).order_by(VitalSign.timestamp.desc()).first()
        
        # Get recent anomalies (last 24 hours)
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.patient_id == patient_id,
            Anomaly.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(Anomaly.timestamp.desc()).all()
        
        # Determine overall status
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
        
        return PatientStatus(
            patient_id=patient_id,
            name=patient.name,
            status=status,
            latest_vitals=latest_vitals,
            recent_anomalies=recent_anomalies,
            last_updated=latest_vitals.timestamp if latest_vitals else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient status"
        )

@router.get("/{patient_id}/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    patient_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get anomalies for a patient within specified hours"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get anomalies
        anomalies = db.query(Anomaly).filter(
            Anomaly.patient_id == patient_id,
            Anomaly.timestamp >= start_time,
            Anomaly.timestamp <= end_time
        ).order_by(Anomaly.timestamp.desc()).all()
        
        return anomalies
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch anomalies"
        )
