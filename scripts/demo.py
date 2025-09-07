#!/usr/bin/env python3
"""
Demo Script for Health Monitoring System
Day 4: Demo Dashboard & Documentation
"""

import requests
import time
import json
import random
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n🔹 Step {step}: {description}")
    print("-" * 40)

def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and responding")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not responding: {e}")
        return False

def get_patients():
    """Get list of patients"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/patients/")
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Found {len(patients)} patients")
            return patients
        else:
            print(f"❌ Failed to get patients: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting patients: {e}")
        return []

def get_dashboard_overview():
    """Get dashboard overview"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/overview")
        if response.status_code == 200:
            overview = response.json()
            print("✅ Dashboard overview retrieved")
            return overview
        else:
            print(f"❌ Failed to get dashboard overview: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting dashboard overview: {e}")
        return None

def get_recent_alerts():
    """Get recent alerts"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/alerts/?hours=24")
        if response.status_code == 200:
            alerts = response.json()
            print(f"✅ Found {len(alerts)} recent alerts")
            return alerts
        else:
            print(f"❌ Failed to get alerts: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting alerts: {e}")
        return []

def get_anomalies_summary():
    """Get anomalies summary"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/anomalies-summary?hours=24")
        if response.status_code == 200:
            summary = response.json()
            print("✅ Anomalies summary retrieved")
            return summary
        else:
            print(f"❌ Failed to get anomalies summary: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting anomalies summary: {e}")
        return None

def send_test_alert(patient_id):
    """Send a test alert"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/alerts/send-test",
            params={
                "patient_id": patient_id,
                "severity": "WARNING",
                "message": "Demo test alert - this is a demonstration"
            }
        )
        if response.status_code == 200:
            print(f"✅ Test alert sent for patient {patient_id}")
            return True
        else:
            print(f"❌ Failed to send test alert: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending test alert: {e}")
        return False

def simulate_vital_signs(patient_id):
    """Simulate vital signs for a patient"""
    # Generate realistic vital signs with some randomness
    heart_rate = random.randint(60, 100)
    spo2 = random.randint(95, 100)
    glucose = random.randint(80, 120)
    bp_sys = random.randint(90, 140)
    bp_dia = random.randint(60, 90)
    temperature = round(97.5 + random.uniform(0, 2), 1)
    
    # Occasionally add anomalies for demonstration
    if random.random() < 0.2:  # 20% chance of anomaly
        anomaly_type = random.choice(["heart_rate", "spo2", "glucose", "blood_pressure_systolic"])
        if anomaly_type == "heart_rate":
            heart_rate = random.randint(130, 180)  # High heart rate
        elif anomaly_type == "spo2":
            spo2 = random.randint(85, 92)  # Low SpO2
        elif anomaly_type == "glucose":
            glucose = random.randint(200, 300)  # High glucose
        elif anomaly_type == "blood_pressure_systolic":
            bp_sys = random.randint(160, 200)  # High blood pressure
        
        print(f"⚠️  Generated anomaly: {anomaly_type}")
    
    vital_data = {
        "heart_rate": heart_rate,
        "spo2": spo2,
        "glucose": glucose,
        "blood_pressure_systolic": bp_sys,
        "blood_pressure_diastolic": bp_dia,
        "temperature": temperature,
        "device_id": f"DEMO_DEVICE_{patient_id}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/patients/{patient_id}/vitals",
            json=vital_data
        )
        if response.status_code == 200:
            print(f"✅ Vital signs recorded for patient {patient_id}")
            print(f"   Heart Rate: {heart_rate} BPM")
            print(f"   SpO2: {spo2}%")
            print(f"   Glucose: {glucose} mg/dL")
            print(f"   BP: {bp_sys}/{bp_dia} mmHg")
            print(f"   Temperature: {temperature}°F")
            return True
        else:
            print(f"❌ Failed to record vital signs: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error recording vital signs: {e}")
        return False

def display_dashboard_summary(overview):
    """Display dashboard summary"""
    if not overview:
        return
    
    summary = overview.get("summary", {})
    
    print("\n📊 Dashboard Summary:")
    print(f"   Total Patients: {summary.get('total_patients', 0)}")
    print(f"   Recent Vitals: {summary.get('recent_vitals_count', 0)}")
    print(f"   Recent Anomalies: {summary.get('recent_anomalies_count', 0)}")
    print(f"   Recent Alerts: {summary.get('recent_alerts_count', 0)}")
    print(f"   Critical Alerts: {summary.get('critical_alerts_count', 0)}")
    print(f"   Unacknowledged Alerts: {summary.get('unacknowledged_alerts_count', 0)}")

def display_alerts_summary(alerts):
    """Display alerts summary"""
    if not alerts:
        print("\n🚨 No recent alerts found")
        return
    
    print(f"\n🚨 Recent Alerts ({len(alerts)}):")
    
    for alert in alerts[:5]:  # Show first 5 alerts
        timestamp = datetime.fromisoformat(alert["timestamp"].replace("Z", "+00:00"))
        severity_icon = {
            "CRITICAL": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵"
        }.get(alert["severity"], "⚪")
        
        print(f"   {severity_icon} {alert['severity']} - {alert['patient_id']}")
        print(f"      Type: {alert['alert_type']}")
        print(f"      Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Message: {alert['message']}")
        print(f"      Status: {'✅ Acknowledged' if alert['is_acknowledged'] else '⚠️ Unacknowledged'}")
        print()

def display_anomalies_summary(summary):
    """Display anomalies summary"""
    if not summary:
        return
    
    print("\n🔍 Anomalies Summary:")
    print(f"   Total Anomalies: {summary.get('total_anomalies', 0)}")
    
    severity_breakdown = summary.get("severity_breakdown", {})
    print(f"   Critical: {severity_breakdown.get('CRITICAL', 0)}")
    print(f"   Warning: {severity_breakdown.get('WARNING', 0)}")
    print(f"   Info: {severity_breakdown.get('INFO', 0)}")
    
    type_breakdown = summary.get("type_breakdown", {})
    if type_breakdown:
        print("   By Type:")
        for anomaly_type, count in type_breakdown.items():
            print(f"      {anomaly_type}: {count}")

def run_demo_scenario(scenario_name, description):
    """Run a demo scenario"""
    print_header(f"Demo Scenario: {scenario_name}")
    print(f"Description: {description}")
    
    # Check API health
    print_step(1, "Checking API Health")
    if not check_api_health():
        print("❌ Cannot proceed - API is not available")
        return False
    
    # Get patients
    print_step(2, "Getting Patients")
    patients = get_patients()
    if not patients:
        print("❌ No patients found. Please run generate_sample_data.py first")
        return False
    
    # Get dashboard overview
    print_step(3, "Getting Dashboard Overview")
    overview = get_dashboard_overview()
    display_dashboard_summary(overview)
    
    # Get recent alerts
    print_step(4, "Getting Recent Alerts")
    alerts = get_recent_alerts()
    display_alerts_summary(alerts)
    
    # Get anomalies summary
    print_step(5, "Getting Anomalies Summary")
    anomalies = get_anomalies_summary()
    display_anomalies_summary(anomalies)
    
    return True

def run_interactive_demo():
    """Run interactive demo"""
    print_header("Interactive Demo")
    
    # Check API health
    if not check_api_health():
        print("❌ Cannot proceed - API is not available")
        return
    
    # Get patients
    patients = get_patients()
    if not patients:
        print("❌ No patients found. Please run generate_sample_data.py first")
        return
    
    print(f"\n📋 Available Patients:")
    for i, patient in enumerate(patients):
        print(f"   {i+1}. {patient['name']} ({patient['patient_id']})")
    
    while True:
        print("\n" + "=" * 40)
        print("🎮 Interactive Demo Options:")
        print("1. Simulate vital signs for a patient")
        print("2. Send test alert")
        print("3. Show dashboard overview")
        print("4. Show recent alerts")
        print("5. Show anomalies summary")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            try:
                patient_idx = int(input(f"Select patient (1-{len(patients)}): ")) - 1
                if 0 <= patient_idx < len(patients):
                    patient = patients[patient_idx]
                    print(f"\n🔹 Simulating vital signs for {patient['name']}...")
                    simulate_vital_signs(patient['patient_id'])
                    time.sleep(2)  # Wait for processing
                else:
                    print("❌ Invalid patient selection")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == "2":
            try:
                patient_idx = int(input(f"Select patient (1-{len(patients)}): ")) - 1
                if 0 <= patient_idx < len(patients):
                    patient = patients[patient_idx]
                    print(f"\n🔹 Sending test alert for {patient['name']}...")
                    send_test_alert(patient['patient_id'])
                else:
                    print("❌ Invalid patient selection")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == "3":
            print("\n🔹 Getting dashboard overview...")
            overview = get_dashboard_overview()
            display_dashboard_summary(overview)
        
        elif choice == "4":
            print("\n🔹 Getting recent alerts...")
            alerts = get_recent_alerts()
            display_alerts_summary(alerts)
        
        elif choice == "5":
            print("\n🔹 Getting anomalies summary...")
            anomalies = get_anomalies_summary()
            display_anomalies_summary(anomalies)
        
        elif choice == "6":
            print("\n👋 Thank you for using the Health Monitoring System demo!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def main():
    """Main demo function"""
    print_header("Health Monitoring System - Demo")
    print("This demo showcases the key features of the Health Monitoring System")
    
    # Check if API is available
    if not check_api_health():
        print("\n❌ API is not available. Please start the system first:")
        print("   python -m uvicorn app.main:app --reload")
        print("\nOr run the setup script:")
        print("   python setup.py")
        return
    
    print("\n🎯 Demo Options:")
    print("1. Run Normal Monitoring Scenario")
    print("2. Run Anomaly Detection Scenario")
    print("3. Run Alert Management Scenario")
    print("4. Run Interactive Demo")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            run_demo_scenario(
                "Normal Monitoring",
                "Demonstrates normal patient monitoring and dashboard overview"
            )
        
        elif choice == "2":
            run_demo_scenario(
                "Anomaly Detection",
                "Demonstrates anomaly detection and alert generation"
            )
        
        elif choice == "3":
            run_demo_scenario(
                "Alert Management",
                "Demonstrates alert system and notification management"
            )
        
        elif choice == "4":
            run_interactive_demo()
        
        elif choice == "5":
            print("\n👋 Thank you for using the Health Monitoring System demo!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
