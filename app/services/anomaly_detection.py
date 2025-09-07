"""
Anomaly Detection Service for Health Monitoring System
Day 2: ML Models & Core API
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from app.database import Anomaly, VitalSign, AlertConfiguration
from app.models.schemas import SeverityLevel

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Simple anomaly detection using statistical methods"""
    
    def __init__(self):
        self.thresholds = {
            "heart_rate": {"min": 50, "max": 120},
            "spo2": {"min": 90, "max": 100},
            "glucose": {"min": 70, "max": 200},
            "blood_pressure_systolic": {"min": 90, "max": 140},
            "blood_pressure_diastolic": {"min": 60, "max": 90},
            "temperature": {"min": 97, "max": 99.5}
        }
    
    def detect_threshold_anomalies(self, vitals_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies based on threshold violations"""
        anomalies = []
        
        for metric, value in vitals_data.items():
            if value is None or metric not in self.thresholds:
                continue
            
            threshold = self.thresholds[metric]
            
            # Check for threshold violations
            if value < threshold["min"] or value > threshold["max"]:
                severity = self._determine_severity(metric, value, threshold)
                confidence = self._calculate_confidence(metric, value, threshold)
                
                anomaly = {
                    "anomaly_type": metric,
                    "confidence_score": confidence,
                    "severity": severity,
                    "description": self._generate_description(metric, value, threshold),
                    "recommendation": self._generate_recommendation(metric, severity)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_statistical_anomalies(self, patient_id: str, vitals_data: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods (Z-score)"""
        anomalies = []
        
        # Get historical data for the patient (last 7 days)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        historical_vitals = db.query(VitalSign).filter(
            VitalSign.patient_id == patient_id,
            VitalSign.timestamp >= start_time,
            VitalSign.timestamp <= end_time
        ).all()
        
        if len(historical_vitals) < 10:  # Need sufficient data for statistical analysis
            return anomalies
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'heart_rate': v.heart_rate,
            'spo2': v.spo2,
            'glucose': v.glucose,
            'blood_pressure_systolic': v.blood_pressure_systolic,
            'blood_pressure_diastolic': v.blood_pressure_diastolic,
            'temperature': v.temperature
        } for v in historical_vitals])
        
        # Check each metric for statistical anomalies
        for metric, current_value in vitals_data.items():
            if current_value is None or metric not in df.columns:
                continue
            
            # Remove null values
            metric_data = df[metric].dropna()
            
            if len(metric_data) < 5:  # Need at least 5 data points
                continue
            
            # Calculate Z-score
            mean = metric_data.mean()
            std = metric_data.std()
            
            if std == 0:  # No variation in data
                continue
            
            z_score = abs((current_value - mean) / std)
            
            # Anomaly if Z-score > 2.5 (99% confidence)
            if z_score > 2.5:
                severity = self._determine_statistical_severity(z_score)
                confidence = min(0.99, z_score / 3.0)  # Normalize to 0-1
                
                anomaly = {
                    "anomaly_type": f"{metric}_statistical",
                    "confidence_score": confidence,
                    "severity": severity,
                    "description": f"Statistical anomaly detected in {metric}. Z-score: {z_score:.2f}, Current: {current_value:.1f}, Mean: {mean:.1f}",
                    "recommendation": self._generate_recommendation(metric, severity)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _determine_severity(self, metric: str, value: float, threshold: Dict[str, float]) -> str:
        """Determine severity based on how far the value is from normal range"""
        min_val, max_val = threshold["min"], threshold["max"]
        normal_range = max_val - min_val
        
        if value < min_val:
            deviation = (min_val - value) / normal_range
        else:
            deviation = (value - max_val) / normal_range
        
        if deviation > 0.5:  # More than 50% outside normal range
            return SeverityLevel.CRITICAL
        elif deviation > 0.2:  # More than 20% outside normal range
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.INFO
    
    def _determine_statistical_severity(self, z_score: float) -> str:
        """Determine severity based on Z-score"""
        if z_score > 3.0:
            return SeverityLevel.CRITICAL
        elif z_score > 2.5:
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.INFO
    
    def _calculate_confidence(self, metric: str, value: float, threshold: Dict[str, float]) -> float:
        """Calculate confidence score for anomaly detection"""
        min_val, max_val = threshold["min"], threshold["max"]
        normal_range = max_val - min_val
        
        if value < min_val:
            deviation = (min_val - value) / normal_range
        else:
            deviation = (value - max_val) / normal_range
        
        # Confidence increases with deviation from normal range
        confidence = min(0.99, 0.5 + (deviation * 0.5))
        return confidence
    
    def _generate_description(self, metric: str, value: float, threshold: Dict[str, float]) -> str:
        """Generate human-readable description of the anomaly"""
        min_val, max_val = threshold["min"], threshold["max"]
        
        if value < min_val:
            return f"{metric} is {min_val - value:.1f} units below normal range (normal: {min_val}-{max_val})"
        else:
            return f"{metric} is {value - max_val:.1f} units above normal range (normal: {min_val}-{max_val})"
    
    def _generate_recommendation(self, metric: str, severity: str) -> str:
        """Generate recommendation based on metric and severity"""
        recommendations = {
            "heart_rate": {
                SeverityLevel.INFO: "Monitor heart rate closely",
                SeverityLevel.WARNING: "Consider immediate medical attention",
                SeverityLevel.CRITICAL: "Seek immediate medical attention"
            },
            "spo2": {
                SeverityLevel.INFO: "Monitor oxygen saturation",
                SeverityLevel.WARNING: "Check oxygen levels and breathing",
                SeverityLevel.CRITICAL: "Immediate medical attention required - low oxygen"
            },
            "glucose": {
                SeverityLevel.INFO: "Monitor blood glucose levels",
                SeverityLevel.WARNING: "Check blood sugar and consider medication adjustment",
                SeverityLevel.CRITICAL: "Immediate medical attention required - blood sugar emergency"
            },
            "blood_pressure_systolic": {
                SeverityLevel.INFO: "Monitor blood pressure",
                SeverityLevel.WARNING: "Consider blood pressure medication review",
                SeverityLevel.CRITICAL: "Immediate medical attention required - blood pressure emergency"
            },
            "blood_pressure_diastolic": {
                SeverityLevel.INFO: "Monitor blood pressure",
                SeverityLevel.WARNING: "Consider blood pressure medication review",
                SeverityLevel.CRITICAL: "Immediate medical attention required - blood pressure emergency"
            },
            "temperature": {
                SeverityLevel.INFO: "Monitor body temperature",
                SeverityLevel.WARNING: "Check for fever or hypothermia",
                SeverityLevel.CRITICAL: "Immediate medical attention required - temperature emergency"
            }
        }
        
        return recommendations.get(metric, {}).get(severity, "Monitor closely and consult healthcare provider")

# Global anomaly detector instance
anomaly_detector = AnomalyDetector()

async def detect_anomalies(patient_id: str, vitals_data: Dict[str, Any], db: Session) -> List[Anomaly]:
    """Main function to detect anomalies for a patient's vital signs"""
    try:
        anomalies = []
        
        # Get custom thresholds for patient if available
        custom_configs = db.query(AlertConfiguration).filter(
            AlertConfiguration.patient_id == patient_id,
            AlertConfiguration.is_active == True
        ).all()
        
        # Update detector thresholds with custom configurations
        for config in custom_configs:
            if config.metric_name in anomaly_detector.thresholds:
                if config.min_threshold is not None:
                    anomaly_detector.thresholds[config.metric_name]["min"] = config.min_threshold
                if config.max_threshold is not None:
                    anomaly_detector.thresholds[config.metric_name]["max"] = config.max_threshold
        
        # Detect threshold-based anomalies
        threshold_anomalies = anomaly_detector.detect_threshold_anomalies(vitals_data)
        
        # Detect statistical anomalies
        statistical_anomalies = anomaly_detector.detect_statistical_anomalies(patient_id, vitals_data, db)
        
        # Combine all anomalies
        all_anomalies = threshold_anomalies + statistical_anomalies
        
        # Save anomalies to database
        for anomaly_data in all_anomalies:
            anomaly = Anomaly(
                patient_id=patient_id,
                timestamp=datetime.utcnow(),
                **anomaly_data
            )
            db.add(anomaly)
            anomalies.append(anomaly)
        
        if anomalies:
            db.commit()
            logger.info(f"Detected {len(anomalies)} anomalies for patient {patient_id}")
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}")
        db.rollback()
        return []
