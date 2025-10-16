# Monitoring Scripts

This directory contains monitoring and health check scripts for system and application monitoring.

## Scripts

### 1. Application Health Checker (`app-health-checker.py`)

Monitors application uptime and health by checking HTTP status codes.

**Features:**
- Single health check or continuous monitoring
- HTTP status code validation
- Response time measurement
- Configurable timeout and intervals
- Logging to file and console
- Exit codes for automation

**Usage:**
```bash
# Single check
python3 app-health-checker.py http://localhost:4499

# Continuous monitoring
python3 app-health-checker.py http://localhost:4499 --continuous --interval 30

# With logging
python3 app-health-checker.py http://localhost:4499 --continuous --log-file health.log

# Custom timeout
python3 app-health-checker.py http://localhost:4499 --timeout 5
```

**Options:**
- `--timeout`: Request timeout in seconds (default: 10)
- `--interval`: Check interval for continuous monitoring (default: 30)
- `--continuous`: Run continuous monitoring
- `--log-file`: Log file path

### 2. System Health Monitor (`system-health-monitor.py`)

Monitors system resources including CPU, memory, disk space, and processes.

**Features:**
- CPU usage monitoring
- Memory usage tracking
- Disk space monitoring
- Top processes by CPU usage
- Configurable thresholds
- Alert generation
- JSON alert logging

**Usage:**
```bash
# Single check
python3 system-health-monitor.py

# Continuous monitoring
python3 system-health-monitor.py --continuous

# Custom thresholds
python3 system-health-monitor.py --cpu-threshold 90 --memory-threshold 85 --disk-threshold 75

# With logging and alerts
python3 system-health-monitor.py --continuous --log-file system.log --alert-file alerts.json
```

**Options:**
- `--cpu-threshold`: CPU usage threshold percentage (default: 80)
- `--memory-threshold`: Memory usage threshold percentage (default: 80)
- `--disk-threshold`: Disk usage threshold percentage (default: 80)
- `--interval`: Check interval for continuous monitoring (default: 60)
- `--continuous`: Run continuous monitoring
- `--log-file`: Log file path
- `--alert-file`: Alert file path for JSON alerts

## Installation

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Make scripts executable:
```bash
chmod +x app-health-checker.py system-health-monitor.py
```

## Integration with Wisecow

These scripts can be used to monitor the Wisecow application:

```bash
# Monitor Wisecow application health
python3 app-health-checker.py http://localhost:4499 --continuous

# Monitor system resources while running Wisecow
python3 system-health-monitor.py --continuous --cpu-threshold 70
```

## Automation

Both scripts return appropriate exit codes for use in automation:
- Exit code 0: Success/Healthy
- Exit code 1: Failure/Unhealthy

Example in shell scripts:
```bash
#!/bin/bash
if python3 app-health-checker.py http://localhost:4499; then
    echo "Application is healthy"
else
    echo "Application is down - taking action..."
    # Restart application or send notification
fi
```