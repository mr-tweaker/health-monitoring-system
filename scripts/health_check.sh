#!/bin/bash

# Health Check Script for Health Monitoring System
# Day 3: Alerts & UNIX Automation

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/health_check.log"
API_URL="http://localhost:8000"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Function to check if API is responding
check_api_health() {
    log_message "Checking API health..."
    
    if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
        log_message "✅ API is healthy and responding"
        return 0
    else
        log_message "❌ API is not responding"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    log_message "Checking database connectivity..."
    
    # Check if database file exists
    DB_FILE="$PROJECT_DIR/data/health_monitoring.db"
    if [ -f "$DB_FILE" ]; then
        log_message "✅ Database file exists"
        
        # Check if database is accessible
        if sqlite3 "$DB_FILE" "SELECT 1;" > /dev/null 2>&1; then
            log_message "✅ Database is accessible"
            return 0
        else
            log_message "❌ Database is not accessible"
            return 1
        fi
    else
        log_message "❌ Database file not found"
        return 1
    fi
}

# Function to check system resources
check_system_resources() {
    log_message "Checking system resources..."
    
    # Check disk space
    DISK_USAGE=$(df -h "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 90 ]; then
        log_message "✅ Disk usage: ${DISK_USAGE}% (OK)"
    else
        log_message "⚠️  Disk usage: ${DISK_USAGE}% (HIGH)"
    fi
    
    # Check memory usage
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -lt 90 ]; then
        log_message "✅ Memory usage: ${MEMORY_USAGE}% (OK)"
    else
        log_message "⚠️  Memory usage: ${MEMORY_USAGE}% (HIGH)"
    fi
    
    # Check CPU load
    CPU_LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    log_message "ℹ️  CPU load: $CPU_LOAD"
}

# Function to check Docker containers
check_docker_containers() {
    log_message "Checking Docker containers..."
    
    if command -v docker > /dev/null 2>&1; then
        # Check if containers are running
        CONTAINERS=$(docker ps --filter "name=health-monitoring" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
        
        if [ -n "$CONTAINERS" ]; then
            log_message "✅ Docker containers status:"
            echo "$CONTAINERS" | while read line; do
                log_message "   $line"
            done
        else
            log_message "⚠️  No health monitoring containers found"
        fi
    else
        log_message "ℹ️  Docker not available"
    fi
}

# Function to check log files
check_log_files() {
    log_message "Checking log files..."
    
    LOG_DIR="$PROJECT_DIR/logs"
    if [ -d "$LOG_DIR" ]; then
        # Check log file sizes
        for log_file in "$LOG_DIR"/*.log; do
            if [ -f "$log_file" ]; then
                SIZE=$(du -h "$log_file" | cut -f1)
                log_message "ℹ️  Log file: $(basename "$log_file") - Size: $SIZE"
            fi
        done
    else
        log_message "⚠️  Log directory not found"
    fi
}

# Function to check recent alerts
check_recent_alerts() {
    log_message "Checking recent alerts..."
    
    # Try to get recent alerts from API
    if curl -s -f "$API_URL/api/alerts/statistics/" > /dev/null 2>&1; then
        ALERT_STATS=$(curl -s "$API_URL/api/alerts/statistics/")
        if [ $? -eq 0 ]; then
            log_message "✅ Alert system is responding"
            # Extract critical alerts count (simplified)
            CRITICAL_ALERTS=$(echo "$ALERT_STATS" | grep -o '"critical":[0-9]*' | grep -o '[0-9]*')
            if [ -n "$CRITICAL_ALERTS" ] && [ "$CRITICAL_ALERTS" -gt 0 ]; then
                log_message "⚠️  $CRITICAL_ALERTS critical alerts in last 24 hours"
            else
                log_message "✅ No critical alerts in last 24 hours"
            fi
        fi
    else
        log_message "⚠️  Could not retrieve alert statistics"
    fi
}

# Function to generate health report
generate_health_report() {
    log_message "Generating health report..."
    
    REPORT_FILE="$PROJECT_DIR/logs/health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Health Monitoring System - Health Report"
        echo "Generated: $TIMESTAMP"
        echo "========================================"
        echo ""
        
        echo "System Status:"
        check_api_health && echo "API: HEALTHY" || echo "API: UNHEALTHY"
        check_database && echo "Database: HEALTHY" || echo "Database: UNHEALTHY"
        echo ""
        
        echo "System Resources:"
        check_system_resources
        echo ""
        
        echo "Docker Status:"
        check_docker_containers
        echo ""
        
        echo "Recent Activity:"
        check_recent_alerts
        echo ""
        
    } > "$REPORT_FILE"
    
    log_message "✅ Health report generated: $REPORT_FILE"
}

# Main execution
main() {
    log_message "Starting health check..."
    log_message "Project directory: $PROJECT_DIR"
    
    # Run all health checks
    check_api_health
    check_database
    check_system_resources
    check_docker_containers
    check_log_files
    check_recent_alerts
    
    # Generate comprehensive report
    generate_health_report
    
    log_message "Health check completed"
    log_message "========================================"
}

# Run main function
main "$@"
