#!/bin/bash

# Data Simulator Script for Health Monitoring System
# Day 3: Alerts & UNIX Automation

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/data_simulator.log"
API_URL="http://localhost:8000"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Function to generate random vital signs data
generate_vital_signs() {
    local patient_id=$1
    
    # Generate realistic vital signs with some randomness
    local heart_rate=$((60 + RANDOM % 40))  # 60-100 BPM
    local spo2=$((95 + RANDOM % 5))         # 95-100%
    local glucose=$((80 + RANDOM % 40))     # 80-120 mg/dL
    local bp_sys=$((90 + RANDOM % 50))      # 90-140 mmHg
    local bp_dia=$((60 + RANDOM % 30))      # 60-90 mmHg
    local temperature=$(echo "scale=1; 97.5 + $(($RANDOM % 20)) / 10" | bc)  # 97.5-99.5°F
    
    # Occasionally add anomalies for demonstration
    if [ $((RANDOM % 20)) -eq 0 ]; then  # 5% chance of anomaly
        case $((RANDOM % 4)) in
            0) heart_rate=$((130 + RANDOM % 50)) ;;  # High heart rate
            1) spo2=$((85 + RANDOM % 10)) ;;         # Low SpO2
            2) glucose=$((200 + RANDOM % 100)) ;;    # High glucose
            3) bp_sys=$((160 + RANDOM % 40)) ;;      # High blood pressure
        esac
        log_message "⚠️  Generated anomaly for patient $patient_id"
    fi
    
    # Create JSON payload
    cat << EOF
{
    "heart_rate": $heart_rate,
    "spo2": $spo2,
    "glucose": $glucose,
    "blood_pressure_systolic": $bp_sys,
    "blood_pressure_diastolic": $bp_dia,
    "temperature": $temperature,
    "device_id": "DEVICE_$patient_id"
}
EOF
}

# Function to send vital signs to API
send_vital_signs() {
    local patient_id=$1
    local vital_data=$2
    
    log_message "Sending vital signs for patient $patient_id..."
    
    # Send POST request to API
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$vital_data" \
        "$API_URL/api/patients/$patient_id/vitals")
    
    http_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        log_message "✅ Successfully sent vital signs for patient $patient_id"
        return 0
    else
        log_message "❌ Failed to send vital signs for patient $patient_id (HTTP: $http_code)"
        log_message "Response: $response_body"
        return 1
    fi
}

# Function to check if API is available
check_api_availability() {
    log_message "Checking API availability..."
    
    if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
        log_message "✅ API is available"
        return 0
    else
        log_message "❌ API is not available"
        return 1
    fi
}

# Function to get list of patients
get_patients() {
    log_message "Getting list of patients..."
    
    patients_response=$(curl -s "$API_URL/api/patients/")
    
    if [ $? -eq 0 ]; then
        # Extract patient IDs using simple text processing
        echo "$patients_response" | grep -o '"patient_id":"[^"]*"' | sed 's/"patient_id":"//g' | sed 's/"//g'
    else
        log_message "❌ Failed to get patients list"
        return 1
    fi
}

# Function to simulate data for all patients
simulate_data_for_all_patients() {
    log_message "Starting data simulation for all patients..."
    
    # Get list of patients
    patients=$(get_patients)
    
    if [ -z "$patients" ]; then
        log_message "❌ No patients found. Please run generate_sample_data.py first."
        return 1
    fi
    
    local success_count=0
    local total_count=0
    
    # Simulate data for each patient
    for patient_id in $patients; do
        log_message "Simulating data for patient: $patient_id"
        
        # Generate vital signs
        vital_data=$(generate_vital_signs "$patient_id")
        
        # Send to API
        if send_vital_signs "$patient_id" "$vital_data"; then
            ((success_count++))
        fi
        
        ((total_count++))
        
        # Small delay between patients
        sleep 1
    done
    
    log_message "Data simulation completed: $success_count/$total_count successful"
}

# Function to simulate data for a specific patient
simulate_data_for_patient() {
    local patient_id=$1
    
    if [ -z "$patient_id" ]; then
        log_message "❌ Patient ID is required"
        return 1
    fi
    
    log_message "Simulating data for patient: $patient_id"
    
    # Generate vital signs
    vital_data=$(generate_vital_signs "$patient_id")
    
    # Send to API
    if send_vital_signs "$patient_id" "$vital_data"; then
        log_message "✅ Data simulation successful for patient $patient_id"
        return 0
    else
        log_message "❌ Data simulation failed for patient $patient_id"
        return 1
    fi
}

# Function to run continuous simulation
run_continuous_simulation() {
    local interval=${1:-60}  # Default 60 seconds
    
    log_message "Starting continuous data simulation (interval: ${interval}s)"
    log_message "Press Ctrl+C to stop"
    
    while true; do
        simulate_data_for_all_patients
        log_message "Waiting ${interval} seconds before next simulation..."
        sleep "$interval"
    done
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PATIENT_ID]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --continuous [SEC]  Run continuous simulation (default: 60 seconds)"
    echo "  -a, --all               Simulate data for all patients (default)"
    echo "  -p, --patient ID        Simulate data for specific patient"
    echo ""
    echo "Examples:"
    echo "  $0                      # Simulate data for all patients once"
    echo "  $0 -c 30                # Run continuous simulation every 30 seconds"
    echo "  $0 -p PAT001            # Simulate data for patient PAT001"
    echo "  $0 --continuous 120     # Run continuous simulation every 2 minutes"
}

# Main execution
main() {
    # Check if API is available
    if ! check_api_availability; then
        log_message "❌ Cannot proceed without API. Please start the health monitoring system first."
        exit 1
    fi
    
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -c|--continuous)
            local interval=${2:-60}
            run_continuous_simulation "$interval"
            ;;
        -p|--patient)
            local patient_id=$2
            simulate_data_for_patient "$patient_id"
            ;;
        -a|--all|"")
            simulate_data_for_all_patients
            ;;
        *)
            # Assume it's a patient ID
            simulate_data_for_patient "$1"
            ;;
    esac
}

# Run main function
main "$@"
