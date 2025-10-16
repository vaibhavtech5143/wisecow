#!/usr/bin/env python3
"""
System Health Monitoring Script
Monitors CPU usage, memory usage, disk space, and running processes
Sends alerts when thresholds are exceeded
"""

import psutil
import time
import sys
import argparse
import logging
from datetime import datetime
import json

class SystemHealthMonitor:
    def __init__(self, cpu_threshold=80, memory_threshold=80, disk_threshold=80, 
                 interval=60, log_file=None, alert_file=None):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.interval = interval
        self.log_file = log_file
        self.alert_file = alert_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        handlers = [logging.StreamHandler(sys.stdout)]
        
        if self.log_file:
            handlers.append(logging.FileHandler(self.log_file))
            
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=handlers
        )
        
        self.logger = logging.getLogger(__name__)

    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """Get current memory usage information"""
        memory = psutil.virtual_memory()
        return {
            'total': round(memory.total / (1024**3), 2),  # GB
            'used': round(memory.used / (1024**3), 2),    # GB
            'available': round(memory.available / (1024**3), 2),  # GB
            'percentage': memory.percent
        }

    def get_disk_usage(self, path='/'):
        """Get disk usage for specified path"""
        try:
            disk = psutil.disk_usage(path)
            return {
                'total': round(disk.total / (1024**3), 2),  # GB
                'used': round(disk.used / (1024**3), 2),    # GB
                'free': round(disk.free / (1024**3), 2),    # GB
                'percentage': round((disk.used / disk.total) * 100, 2)
            }
        except Exception as e:
            self.logger.error(f"Error getting disk usage for {path}: {e}")
            return None

    def get_running_processes(self):
        """Get information about running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage (descending)
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:10]  # Top 10 processes

    def check_thresholds(self, metrics):
        """Check if any metrics exceed thresholds and generate alerts"""
        alerts = []
        
        # CPU threshold check
        if metrics['cpu']['percentage'] > self.cpu_threshold:
            alerts.append({
                'type': 'CPU',
                'current': metrics['cpu']['percentage'],
                'threshold': self.cpu_threshold,
                'message': f"CPU usage ({metrics['cpu']['percentage']}%) exceeds threshold ({self.cpu_threshold}%)"
            })
        
        # Memory threshold check
        if metrics['memory']['percentage'] > self.memory_threshold:
            alerts.append({
                'type': 'MEMORY',
                'current': metrics['memory']['percentage'],
                'threshold': self.memory_threshold,
                'message': f"Memory usage ({metrics['memory']['percentage']}%) exceeds threshold ({self.memory_threshold}%)"
            })
        
        # Disk threshold check
        if metrics['disk'] and metrics['disk']['percentage'] > self.disk_threshold:
            alerts.append({
                'type': 'DISK',
                'current': metrics['disk']['percentage'],
                'threshold': self.disk_threshold,
                'message': f"Disk usage ({metrics['disk']['percentage']}%) exceeds threshold ({self.disk_threshold}%)"
            })
        
        return alerts

    def send_alerts(self, alerts):
        """Send alerts to console and/or log file"""
        if not alerts:
            return
            
        alert_timestamp = datetime.now().isoformat()
        
        for alert in alerts:
            alert_msg = f"🚨 ALERT: {alert['message']}"
            self.logger.warning(alert_msg)
            
            # Write to alert file if specified
            if self.alert_file:
                try:
                    with open(self.alert_file, 'a') as f:
                        alert_data = {
                            'timestamp': alert_timestamp,
                            'alert': alert
                        }
                        f.write(json.dumps(alert_data) + '\n')
                except Exception as e:
                    self.logger.error(f"Failed to write alert to file: {e}")

    def collect_metrics(self):
        """Collect all system metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percentage': self.get_cpu_usage()
            },
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'processes': self.get_running_processes()
        }
        
        return metrics

    def display_metrics(self, metrics):
        """Display metrics in a formatted way"""
        print("\n" + "="*60)
        print(f"📊 SYSTEM HEALTH REPORT - {metrics['timestamp']}")
        print("="*60)
        
        # CPU Information
        cpu_status = "🟢" if metrics['cpu']['percentage'] <= self.cpu_threshold else "🔴"
        print(f"{cpu_status} CPU Usage: {metrics['cpu']['percentage']}%")
        
        # Memory Information
        memory = metrics['memory']
        memory_status = "🟢" if memory['percentage'] <= self.memory_threshold else "🔴"
        print(f"{memory_status} Memory Usage: {memory['percentage']}% "
              f"({memory['used']}GB / {memory['total']}GB)")
        
        # Disk Information
        if metrics['disk']:
            disk = metrics['disk']
            disk_status = "🟢" if disk['percentage'] <= self.disk_threshold else "🔴"
            print(f"{disk_status} Disk Usage: {disk['percentage']}% "
                  f"({disk['used']}GB / {disk['total']}GB)")
        
        # Top Processes
        print(f"\n🔄 Top CPU Processes:")
        for i, proc in enumerate(metrics['processes'][:5], 1):
            cpu_pct = proc['cpu_percent'] or 0
            mem_pct = proc['memory_percent'] or 0
            print(f"  {i}. {proc['name']} (PID: {proc['pid']}) - "
                  f"CPU: {cpu_pct:.1f}%, Memory: {mem_pct:.1f}%")

    def run_single_check(self):
        """Run a single health check"""
        metrics = self.collect_metrics()
        self.display_metrics(metrics)
        
        alerts = self.check_thresholds(metrics)
        self.send_alerts(alerts)
        
        return len(alerts) == 0  # Return True if no alerts

    def run_continuous_monitoring(self):
        """Run continuous monitoring with specified interval"""
        self.logger.info(f"🚀 Starting system health monitoring")
        self.logger.info(f"⚠️  Thresholds - CPU: {self.cpu_threshold}%, "
                        f"Memory: {self.memory_threshold}%, Disk: {self.disk_threshold}%")
        self.logger.info(f"⏱️  Check interval: {self.interval} seconds")
        
        try:
            while True:
                metrics = self.collect_metrics()
                self.display_metrics(metrics)
                
                alerts = self.check_thresholds(metrics)
                self.send_alerts(alerts)
                
                if not alerts:
                    self.logger.info("✅ All systems normal")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description='System Health Monitor - Monitor CPU, memory, disk, and processes'
    )
    
    parser.add_argument(
        '--cpu-threshold',
        type=int,
        default=80,
        help='CPU usage threshold percentage (default: 80)'
    )
    
    parser.add_argument(
        '--memory-threshold',
        type=int,
        default=80,
        help='Memory usage threshold percentage (default: 80)'
    )
    
    parser.add_argument(
        '--disk-threshold',
        type=int,
        default=80,
        help='Disk usage threshold percentage (default: 80)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds for continuous monitoring (default: 60)'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuous monitoring instead of single check'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path (optional)'
    )
    
    parser.add_argument(
        '--alert-file',
        help='Alert file path for JSON alerts (optional)'
    )
    
    args = parser.parse_args()
    
    # Create monitor instance
    monitor = SystemHealthMonitor(
        cpu_threshold=args.cpu_threshold,
        memory_threshold=args.memory_threshold,
        disk_threshold=args.disk_threshold,
        interval=args.interval,
        log_file=args.log_file,
        alert_file=args.alert_file
    )
    
    if args.continuous:
        monitor.run_continuous_monitoring()
    else:
        healthy = monitor.run_single_check()
        sys.exit(0 if healthy else 1)

if __name__ == '__main__':
    main()