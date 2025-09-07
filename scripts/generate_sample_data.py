"""
Synthetic Health Data Generator for Health Monitoring System
Day 1: Foundation & Data Pipeline
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sys
from typing import List, Dict, Any
import logging

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db, Patient, VitalSign
from app.models.schemas import PatientCreate, VitalSignCreate, Gender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthDataGenerator:
    """Generate realistic synthetic health data"""
    
    def __init__(self):
        self.patients = []
        self.vital_signs_data = []
        
        # Define normal ranges for different age groups and genders
        self.normal_ranges = {
            "heart_rate": {"min": 60, "max": 100},
            "spo2": {"min": 95, "max": 100},
            "glucose": {"min": 80, "max": 120},
            "blood_pressure_systolic": {"min": 90, "max": 140},
            "blood_pressure_diastolic": {"min": 60, "max": 90},
            "temperature": {"min": 97.5, "max": 99.5}
        }
        
        # Sample patient data
        self.sample_patients = [
            {
                "patient_id": "PAT001",
                "name": "John Smith",
                "age": 45,
                "gender": Gender.MALE,
                "medical_history": "Hypertension, Type 2 Diabetes",
                "emergency_contact": "+1-555-0101"
            },
            {
                "patient_id": "PAT002",
                "name": "Sarah Johnson",
                "age": 32,
                "gender": Gender.FEMALE,
                "medical_history": "Asthma, Allergies",
                "emergency_contact": "+1-555-0102"
            },
            {
                "patient_id": "PAT003",
                "name": "Michael Brown",
                "age": 67,
                "gender": Gender.MALE,
                "medical_history": "Heart Disease, High Cholesterol",
                "emergency_contact": "+1-555-0103"
            },
            {
                "patient_id": "PAT004",
                "name": "Emily Davis",
                "age": 28,
                "gender": Gender.FEMALE,
                "medical_history": "None",
                "emergency_contact": "+1-555-0104"
            },
            {
                "patient_id": "PAT005",
                "name": "Robert Wilson",
                "age": 55,
                "gender": Gender.MALE,
                "medical_history": "Type 1 Diabetes, Hypertension",
                "emergency_contact": "+1-555-0105"
            }
        ]
    
    def generate_patients(self, db) -> List[Patient]:
        """Generate and save sample patients"""
        logger.info("Generating sample patients...")
        
        patients = []
        for patient_data in self.sample_patients:
            try:
                # Check if patient already exists
                existing = db.query(Patient).filter(
                    Patient.patient_id == patient_data["patient_id"]
                ).first()
                
                if existing:
                    logger.info(f"Patient {patient_data['patient_id']} already exists, skipping...")
                    patients.append(existing)
                    continue
                
                # Create new patient
                patient = Patient(**patient_data)
                db.add(patient)
                patients.append(patient)
                logger.info(f"Created patient: {patient_data['name']} ({patient_data['patient_id']})")
                
            except Exception as e:
                logger.error(f"Error creating patient {patient_data['patient_id']}: {e}")
        
        db.commit()
        logger.info(f"Generated {len(patients)} patients")
        return patients
    
    def generate_vital_signs(self, patient: Patient, hours: int = 48, interval_minutes: int = 15) -> List[Dict[str, Any]]:
        """Generate realistic vital signs for a patient"""
        logger.info(f"Generating vital signs for {patient.name} ({patient.patient_id})")
        
        vital_signs = []
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Adjust normal ranges based on patient characteristics
        ranges = self._adjust_ranges_for_patient(patient)
        
        for i in range(hours * 4):  # Every 15 minutes
            timestamp = start_time + timedelta(minutes=i * interval_minutes)
            
            # Generate realistic vital signs with some variation
            vitals = self._generate_realistic_vitals(patient, ranges, timestamp)
            vitals["patient_id"] = patient.patient_id
            vitals["timestamp"] = timestamp
            vitals["device_id"] = f"DEVICE_{patient.patient_id}"
            
            vital_signs.append(vitals)
        
        # Add some anomalies for demonstration
        vital_signs = self._add_anomalies(vital_signs, patient)
        
        logger.info(f"Generated {len(vital_signs)} vital signs records for {patient.name}")
        return vital_signs
    
    def _adjust_ranges_for_patient(self, patient: Patient) -> Dict[str, Dict[str, float]]:
        """Adjust normal ranges based on patient characteristics"""
        ranges = self.normal_ranges.copy()
        
        # Adjust for age
        if patient.age > 60:
            ranges["heart_rate"]["max"] += 10
            ranges["blood_pressure_systolic"]["max"] += 10
        elif patient.age < 30:
            ranges["heart_rate"]["min"] -= 5
            ranges["blood_pressure_systolic"]["min"] -= 5
        
        # Adjust for medical history
        if "diabetes" in patient.medical_history.lower():
            ranges["glucose"]["min"] = 70
            ranges["glucose"]["max"] = 180
        
        if "hypertension" in patient.medical_history.lower():
            ranges["blood_pressure_systolic"]["max"] += 20
            ranges["blood_pressure_diastolic"]["max"] += 10
        
        if "heart" in patient.medical_history.lower():
            ranges["heart_rate"]["min"] += 10
            ranges["heart_rate"]["max"] += 20
        
        return ranges
    
    def _generate_realistic_vitals(self, patient: Patient, ranges: Dict, timestamp: datetime) -> Dict[str, Any]:
        """Generate realistic vital signs with natural variation"""
        # Add circadian rhythm (lower values at night)
        hour = timestamp.hour
        circadian_factor = 0.8 + 0.4 * np.sin(2 * np.pi * (hour - 6) / 24)
        
        # Add some random variation
        variation = 0.05  # 5% variation
        
        vitals = {}
        
        # Heart rate with circadian rhythm
        hr_base = (ranges["heart_rate"]["min"] + ranges["heart_rate"]["max"]) / 2
        hr_variation = hr_base * variation * random.uniform(-1, 1)
        vitals["heart_rate"] = max(40, hr_base * circadian_factor + hr_variation)
        
        # SpO2 (usually stable)
        spo2_base = (ranges["spo2"]["min"] + ranges["spo2"]["max"]) / 2
        vitals["spo2"] = max(90, spo2_base + random.uniform(-2, 2))
        
        # Glucose (varies with meals)
        glucose_base = (ranges["glucose"]["min"] + ranges["glucose"]["max"]) / 2
        meal_factor = 1.2 if 7 <= hour <= 9 or 12 <= hour <= 14 or 18 <= hour <= 20 else 1.0
        vitals["glucose"] = max(60, glucose_base * meal_factor + random.uniform(-10, 10))
        
        # Blood pressure
        bp_sys_base = (ranges["blood_pressure_systolic"]["min"] + ranges["blood_pressure_systolic"]["max"]) / 2
        vitals["blood_pressure_systolic"] = max(80, bp_sys_base * circadian_factor + random.uniform(-5, 5))
        
        bp_dia_base = (ranges["blood_pressure_diastolic"]["min"] + ranges["blood_pressure_diastolic"]["max"]) / 2
        vitals["blood_pressure_diastolic"] = max(50, bp_dia_base * circadian_factor + random.uniform(-3, 3))
        
        # Temperature (slight variation)
        temp_base = (ranges["temperature"]["min"] + ranges["temperature"]["max"]) / 2
        vitals["temperature"] = temp_base + random.uniform(-0.5, 0.5)
        
        return vitals
    
    def _add_anomalies(self, vital_signs: List[Dict], patient: Patient) -> List[Dict]:
        """Add some anomalies for demonstration purposes"""
        logger.info(f"Adding anomalies for demonstration - Patient {patient.name}")
        
        # Add a few anomalies at random times
        num_anomalies = random.randint(2, 5)
        anomaly_indices = random.sample(range(len(vital_signs)), num_anomalies)
        
        for idx in anomaly_indices:
            vitals = vital_signs[idx]
            
            # Randomly choose which metric to make anomalous
            metric = random.choice(["heart_rate", "spo2", "glucose", "blood_pressure_systolic"])
            
            if metric == "heart_rate":
                # Make heart rate too high or too low
                if random.choice([True, False]):
                    vitals["heart_rate"] = random.uniform(130, 180)  # Tachycardia
                else:
                    vitals["heart_rate"] = random.uniform(40, 55)   # Bradycardia
            
            elif metric == "spo2":
                # Make SpO2 too low
                vitals["spo2"] = random.uniform(85, 92)  # Low oxygen
            
            elif metric == "glucose":
                # Make glucose too high or too low
                if random.choice([True, False]):
                    vitals["glucose"] = random.uniform(200, 300)  # Hyperglycemia
                else:
                    vitals["glucose"] = random.uniform(50, 70)   # Hypoglycemia
            
            elif metric == "blood_pressure_systolic":
                # Make blood pressure too high
                vitals["blood_pressure_systolic"] = random.uniform(160, 200)  # Hypertension
            
            logger.info(f"Added {metric} anomaly at {vitals['timestamp']}: {vitals[metric]}")
        
        return vital_signs
    
    def save_vital_signs_to_db(self, vital_signs: List[Dict], db) -> int:
        """Save vital signs to database"""
        logger.info(f"Saving {len(vital_signs)} vital signs to database...")
        
        saved_count = 0
        for vital_data in vital_signs:
            try:
                vital = VitalSign(**vital_data)
                db.add(vital)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving vital signs: {e}")
        
        db.commit()
        logger.info(f"Successfully saved {saved_count} vital signs records")
        return saved_count
    
    def save_to_csv(self, vital_signs: List[Dict], filename: str = None):
        """Save vital signs to CSV file for backup/analysis"""
        if not filename:
            filename = f"data/vital_signs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        os.makedirs("data", exist_ok=True)
        
        df = pd.DataFrame(vital_signs)
        df.to_csv(filename, index=False)
        logger.info(f"Saved vital signs to {filename}")
        
        return filename

def main():
    """Main function to generate sample data"""
    logger.info("Starting Health Data Generation...")
    
    try:
        # Initialize database
        init_db()
        
        # Get database session
        db = next(get_db())
        
        # Create data generator
        generator = HealthDataGenerator()
        
        # Generate patients
        patients = generator.generate_patients(db)
        
        # Generate vital signs for each patient
        all_vital_signs = []
        for patient in patients:
            vital_signs = generator.generate_vital_signs(patient, hours=48, interval_minutes=15)
            all_vital_signs.extend(vital_signs)
        
        # Save to database
        saved_count = generator.save_vital_signs_to_db(all_vital_signs, db)
        
        # Save to CSV for backup
        csv_file = generator.save_to_csv(all_vital_signs)
        
        logger.info("="*50)
        logger.info("DATA GENERATION COMPLETE")
        logger.info("="*50)
        logger.info(f"Patients created: {len(patients)}")
        logger.info(f"Vital signs records: {saved_count}")
        logger.info(f"CSV backup: {csv_file}")
        logger.info("="*50)
        
        # Print sample data
        print("\nSample Generated Data:")
        print("-" * 30)
        for i, patient in enumerate(patients[:3]):  # Show first 3 patients
            print(f"Patient {i+1}: {patient.name} ({patient.patient_id})")
            print(f"  Age: {patient.age}, Gender: {patient.gender}")
            print(f"  Medical History: {patient.medical_history}")
        
        print(f"\nTotal vital signs records generated: {saved_count}")
        print(f"Data saved to: {csv_file}")
        
    except Exception as e:
        logger.error(f"Error in data generation: {e}")
        raise

if __name__ == "__main__":
    main()
