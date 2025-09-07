"""
Alert Service for Health Monitoring System
Day 3: Alerts & UNIX Automation
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import Alert, AlertConfiguration, Patient
from app.models.schemas import SeverityLevel

logger = logging.getLogger(__name__)

class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "health.monitoring.demo@gmail.com",  # Demo email
            "sender_password": "demo_password_123"  # Demo password
        }
    
    async def check_and_create_alerts(self, patient_id: str, anomalies: List, db: Session) -> List[Alert]:
        """Check anomalies and create alerts if necessary"""
        alerts = []
        
        try:
            for anomaly in anomalies:
                # Determine if alert should be created based on severity
                if anomaly.severity in [SeverityLevel.WARNING, SeverityLevel.CRITICAL]:
                    # Check if similar alert already exists recently (within 1 hour)
                    recent_alert = db.query(Alert).filter(
                        Alert.patient_id == patient_id,
                        Alert.alert_type == anomaly.anomaly_type,
                        Alert.timestamp >= datetime.utcnow() - timedelta(hours=1)
                    ).first()
                    
                    if not recent_alert:
                        # Create new alert
                        alert = Alert(
                            patient_id=patient_id,
                            alert_type=anomaly.anomaly_type,
                            severity=anomaly.severity,
                            message=self._generate_alert_message(anomaly),
                            timestamp=datetime.utcnow()
                        )
                        
                        db.add(alert)
                        alerts.append(alert)
            
            if alerts:
                db.commit()
                logger.info(f"Created {len(alerts)} alerts for patient {patient_id}")
                
                # Send notifications for new alerts
                for alert in alerts:
                    await self.send_alert_notification(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error creating alerts: {e}")
            db.rollback()
            return []
    
    def _generate_alert_message(self, anomaly) -> str:
        """Generate alert message from anomaly data"""
        severity_text = {
            SeverityLevel.INFO: "Information",
            SeverityLevel.WARNING: "Warning",
            SeverityLevel.CRITICAL: "Critical Alert"
        }
        
        message = f"{severity_text[anomaly.severity]}: {anomaly.description}"
        if anomaly.recommendation:
            message += f" Recommendation: {anomaly.recommendation}"
        
        return message
    
    async def send_alert_notification(self, alert: Alert) -> bool:
        """Send alert notification via email and console"""
        try:
            # Send console notification
            self._send_console_notification(alert)
            
            # Send email notification
            await self._send_email_notification(alert)
            
            # Mark alert as sent
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
            return False
    
    def _send_console_notification(self, alert: Alert):
        """Send notification to console (for demo purposes)"""
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Color coding for different severities
        color_codes = {
            SeverityLevel.INFO: "\033[94m",      # Blue
            SeverityLevel.WARNING: "\033[93m",   # Yellow
            SeverityLevel.CRITICAL: "\033[91m"   # Red
        }
        
        reset_code = "\033[0m"
        color = color_codes.get(alert.severity, "")
        
        print(f"\n{color}🚨 ALERT NOTIFICATION 🚨{reset_code}")
        print(f"Time: {timestamp}")
        print(f"Patient: {alert.patient_id}")
        print(f"Type: {alert.alert_type}")
        print(f"Severity: {alert.severity}")
        print(f"Message: {alert.message}")
        print(f"{color}{'='*50}{reset_code}\n")
        
        # Also log to file
        logger.warning(f"ALERT: {alert.patient_id} - {alert.alert_type} - {alert.severity} - {alert.message}")
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification (demo implementation)"""
        try:
            # Get patient information
            from app.database import get_db
            db = next(get_db())
            patient = db.query(Patient).filter(Patient.patient_id == alert.patient_id).first()
            
            if not patient:
                logger.error(f"Patient {alert.patient_id} not found for email notification")
                return
            
            # Get notification email from configuration
            config = db.query(AlertConfiguration).filter(
                AlertConfiguration.patient_id == alert.patient_id,
                AlertConfiguration.metric_name == alert.alert_type
            ).first()
            
            notification_email = config.notification_email if config else None
            
            if not notification_email:
                logger.info(f"No notification email configured for patient {alert.patient_id}")
                return
            
            # Create email content
            subject = f"Health Alert - {alert.severity} - Patient {patient.name}"
            
            body = f"""
Health Monitoring System Alert

Patient Information:
- Name: {patient.name}
- Patient ID: {alert.patient_id}
- Age: {patient.age}
- Gender: {patient.gender}

Alert Details:
- Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- Type: {alert.alert_type}
- Severity: {alert.severity}
- Message: {alert.message}

Please take appropriate action based on the severity level.

This is an automated message from the Health Monitoring System.
            """
            
            # In a real implementation, you would send the email here
            # For demo purposes, we'll just log it
            logger.info(f"EMAIL NOTIFICATION (Demo):")
            logger.info(f"To: {notification_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body}")
            
            # Mark alert as sent
            alert.is_sent = True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def send_test_alert(self, patient_id: str, severity: str = "INFO", message: str = "Test alert") -> bool:
        """Send a test alert for demonstration"""
        try:
            # Create test alert object
            test_alert = Alert(
                patient_id=patient_id,
                alert_type="TEST",
                severity=severity,
                message=message,
                timestamp=datetime.utcnow()
            )
            
            # Send notification
            await self.send_alert_notification(test_alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending test alert: {e}")
            return False
    
    def get_alert_statistics(self, db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics for dashboard"""
        try:
            from datetime import timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get alerts in time range
            alerts = db.query(Alert).filter(
                Alert.timestamp >= start_time,
                Alert.timestamp <= end_time
            ).all()
            
            # Calculate statistics
            stats = {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.severity == SeverityLevel.CRITICAL]),
                "warning_alerts": len([a for a in alerts if a.severity == SeverityLevel.WARNING]),
                "info_alerts": len([a for a in alerts if a.severity == SeverityLevel.INFO]),
                "acknowledged_alerts": len([a for a in alerts if a.is_acknowledged]),
                "sent_alerts": len([a for a in alerts if a.is_sent]),
                "alerts_by_type": {},
                "alerts_by_patient": {}
            }
            
            # Group by type and patient
            for alert in alerts:
                # By type
                if alert.alert_type not in stats["alerts_by_type"]:
                    stats["alerts_by_type"][alert.alert_type] = 0
                stats["alerts_by_type"][alert.alert_type] += 1
                
                # By patient
                if alert.patient_id not in stats["alerts_by_patient"]:
                    stats["alerts_by_patient"][alert.patient_id] = 0
                stats["alerts_by_patient"][alert.patient_id] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {}

# Global alert service instance
alert_service = AlertService()

# Convenience functions
async def check_and_create_alerts(patient_id: str, anomalies: List, db: Session) -> List[Alert]:
    """Check anomalies and create alerts"""
    return await alert_service.check_and_create_alerts(patient_id, anomalies, db)

async def send_alert_notification(alert: Alert) -> bool:
    """Send alert notification"""
    return await alert_service.send_alert_notification(alert)

async def send_test_alert(patient_id: str, severity: str = "INFO", message: str = "Test alert") -> bool:
    """Send test alert"""
    return await alert_service.send_test_alert(patient_id, severity, message)
