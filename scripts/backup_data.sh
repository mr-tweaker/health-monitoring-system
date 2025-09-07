#!/bin/bash

# Data Backup Script for Health Monitoring System
# Day 3: Alerts & UNIX Automation

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/logs/backup.log"
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$PROJECT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to backup database
backup_database() {
    log_message "Starting database backup..."
    
    DB_FILE="$PROJECT_DIR/data/health_monitoring.db"
    BACKUP_FILE="$BACKUP_DIR/health_monitoring_$TIMESTAMP.db"
    
    if [ -f "$DB_FILE" ]; then
        # Create database backup
        if cp "$DB_FILE" "$BACKUP_FILE"; then
            log_message "✅ Database backed up to: $BACKUP_FILE"
            
            # Compress the backup
            if gzip "$BACKUP_FILE"; then
                log_message "✅ Database backup compressed: ${BACKUP_FILE}.gz"
                echo "${BACKUP_FILE}.gz"
            else
                log_message "⚠️  Failed to compress database backup"
                echo "$BACKUP_FILE"
            fi
        else
            log_message "❌ Failed to backup database"
            return 1
        fi
    else
        log_message "❌ Database file not found: $DB_FILE"
        return 1
    fi
}

# Function to backup log files
backup_logs() {
    log_message "Starting log files backup..."
    
    LOG_DIR="$PROJECT_DIR/logs"
    BACKUP_FILE="$BACKUP_DIR/logs_$TIMESTAMP.tar.gz"
    
    if [ -d "$LOG_DIR" ]; then
        # Create tar.gz archive of log files
        if tar -czf "$BACKUP_FILE" -C "$PROJECT_DIR" logs/; then
            log_message "✅ Log files backed up to: $BACKUP_FILE"
            echo "$BACKUP_FILE"
        else
            log_message "❌ Failed to backup log files"
            return 1
        fi
    else
        log_message "⚠️  Log directory not found: $LOG_DIR"
        return 1
    fi
}

# Function to backup configuration files
backup_configs() {
    log_message "Starting configuration backup..."
    
    CONFIG_FILES=(
        "docker-compose.yml"
        "requirements.txt"
        "scripts/*.sh"
    )
    
    BACKUP_FILE="$BACKUP_DIR/configs_$TIMESTAMP.tar.gz"
    TEMP_DIR="/tmp/health_monitoring_configs_$TIMESTAMP"
    
    # Create temporary directory
    mkdir -p "$TEMP_DIR"
    
    # Copy configuration files
    for pattern in "${CONFIG_FILES[@]}"; do
        if ls $PROJECT_DIR/$pattern > /dev/null 2>&1; then
            cp -r $PROJECT_DIR/$pattern "$TEMP_DIR/" 2>/dev/null
        fi
    done
    
    # Create archive
    if tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .; then
        log_message "✅ Configuration files backed up to: $BACKUP_FILE"
        echo "$BACKUP_FILE"
    else
        log_message "❌ Failed to backup configuration files"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Clean up temporary directory
    rm -rf "$TEMP_DIR"
}

# Function to backup data files
backup_data_files() {
    log_message "Starting data files backup..."
    
    DATA_DIR="$PROJECT_DIR/data"
    BACKUP_FILE="$BACKUP_DIR/data_files_$TIMESTAMP.tar.gz"
    
    if [ -d "$DATA_DIR" ]; then
        # Create tar.gz archive of data files (excluding database)
        if tar -czf "$BACKUP_FILE" -C "$PROJECT_DIR" data/ --exclude="*.db"; then
            log_message "✅ Data files backed up to: $BACKUP_FILE"
            echo "$BACKUP_FILE"
        else
            log_message "❌ Failed to backup data files"
            return 1
        fi
    else
        log_message "⚠️  Data directory not found: $DATA_DIR"
        return 1
    fi
}

# Function to create full system backup
create_full_backup() {
    log_message "Creating full system backup..."
    
    BACKUP_FILE="$BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz"
    
    # Create full backup excluding certain directories
    if tar -czf "$BACKUP_FILE" \
        -C "$PROJECT_DIR" \
        --exclude="backups" \
        --exclude=".git" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude="node_modules" \
        .; then
        log_message "✅ Full system backup created: $BACKUP_FILE"
        echo "$BACKUP_FILE"
    else
        log_message "❌ Failed to create full system backup"
        return 1
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    local days_to_keep=${1:-7}  # Default: keep backups for 7 days
    
    log_message "Cleaning up backups older than $days_to_keep days..."
    
    if [ -d "$BACKUP_DIR" ]; then
        # Find and remove old backup files
        find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$days_to_keep -delete
        find "$BACKUP_DIR" -name "*.db" -type f -mtime +$days_to_keep -delete
        
        log_message "✅ Cleaned up old backups"
    else
        log_message "⚠️  Backup directory not found"
    fi
}

# Function to list available backups
list_backups() {
    log_message "Available backups:"
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -la "$BACKUP_DIR" | while read line; do
            log_message "  $line"
        done
    else
        log_message "  No backup directory found"
    fi
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_message "❌ Backup file path is required"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_message "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    log_message "Restoring from backup: $backup_file"
    
    # Extract backup
    if tar -xzf "$backup_file" -C "$PROJECT_DIR"; then
        log_message "✅ Successfully restored from backup"
        return 0
    else
        log_message "❌ Failed to restore from backup"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -d, --database          Backup database only"
    echo "  -l, --logs              Backup log files only"
    echo "  -c, --configs           Backup configuration files only"
    echo "  -f, --data-files        Backup data files only"
    echo "  -a, --all               Create full system backup (default)"
    echo "  -r, --restore FILE      Restore from backup file"
    echo "  -s, --list              List available backups"
    echo "  --cleanup [DAYS]        Clean up old backups (default: 7 days)"
    echo ""
    echo "Examples:"
    echo "  $0                      # Create full system backup"
    echo "  $0 -d                   # Backup database only"
    echo "  $0 -a                   # Create full system backup"
    echo "  $0 -s                   # List available backups"
    echo "  $0 --cleanup 14         # Clean up backups older than 14 days"
    echo "  $0 -r backup.tar.gz     # Restore from backup"
}

# Main execution
main() {
    log_message "Starting backup process..."
    
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--database)
            backup_database
            ;;
        -l|--logs)
            backup_logs
            ;;
        -c|--configs)
            backup_configs
            ;;
        -f|--data-files)
            backup_data_files
            ;;
        -a|--all|"")
            create_full_backup
            ;;
        -r|--restore)
            restore_backup "$2"
            ;;
        -s|--list)
            list_backups
            ;;
        --cleanup)
            cleanup_old_backups "$2"
            ;;
        *)
            log_message "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    log_message "Backup process completed"
}

# Run main function
main "$@"
