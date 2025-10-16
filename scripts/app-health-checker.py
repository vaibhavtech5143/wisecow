#!/usr/bin/env python3
"""
Application Health Checker Script
Monitors application uptime and health by checking HTTP status codes
"""

import requests
import time
import sys
import argparse
from datetime import datetime
import json
import logging

class ApplicationHealthChecker:
    def __init__(self, url, timeout=10, interval=30, log_file=None):
        self.url = url
        self.timeout = timeout
        self.interval = interval
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        if self.log_file:
            logging.basicConfig(
                level=logging.INFO,
                format=log_format,
                handlers=[
                    logging.FileHandler(self.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=log_format,
                handlers=[logging.StreamHandler(sys.stdout)]
            )
        
        self.logger = logging.getLogger(__name__)

    def check_health(self):
        """
        Check application health by making HTTP request
        Returns: dict with status information
        """
        try:
            start_time = time.time()
            response = requests.get(self.url, timeout=self.timeout)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            status_info = {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'status': 'up' if 200 <= response.status_code < 400 else 'down',
                'reason': self.get_status_reason(response.status_code)
            }
            
            return status_info
            
        except requests.exceptions.Timeout:
            return {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'status_code': None,
                'response_time_ms': None,
                'status': 'down',
                'reason': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'status_code': None,
                'response_time_ms': None,
                'status': 'down',
                'reason': 'Connection error'
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'url': self.url,
                'status_code': None,
                'response_time_ms': None,
                'status': 'down',
                'reason': f'Error: {str(e)}'
            }

    def get_status_reason(self, status_code):
        """Get human-readable reason for status code"""
        if 200 <= status_code < 300:
            return 'Success'
        elif 300 <= status_code < 400:
            return 'Redirection'
        elif 400 <= status_code < 500:
            return 'Client Error'
        elif 500 <= status_code < 600:
            return 'Server Error'
        else:
            return 'Unknown Status'

    def log_status(self, status_info):
        """Log the status information"""
        status = status_info['status'].upper()
        
        if status_info['status'] == 'up':
            self.logger.info(
                f"✅ APP {status} - {self.url} - "
                f"Status: {status_info['status_code']} - "
                f"Response Time: {status_info['response_time_ms']}ms"
            )
        else:
            self.logger.error(
                f"❌ APP {status} - {self.url} - "
                f"Reason: {status_info['reason']}"
            )

    def run_single_check(self):
        """Run a single health check"""
        status_info = self.check_health()
        self.log_status(status_info)
        return status_info

    def run_continuous_monitoring(self):
        """Run continuous monitoring with specified interval"""
        self.logger.info(f"🚀 Starting continuous monitoring of {self.url}")
        self.logger.info(f"⏱️  Check interval: {self.interval} seconds")
        self.logger.info(f"⏰ Timeout: {self.timeout} seconds")
        
        try:
            while True:
                status_info = self.check_health()
                self.log_status(status_info)
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description='Application Health Checker - Monitor application uptime and health'
    )
    
    parser.add_argument(
        'url',
        help='URL to monitor (e.g., http://localhost:4499)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds for continuous monitoring (default: 30)'
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
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Create health checker instance
    checker = ApplicationHealthChecker(
        url=args.url,
        timeout=args.timeout,
        interval=args.interval,
        log_file=args.log_file
    )
    
    if args.continuous:
        checker.run_continuous_monitoring()
    else:
        status_info = checker.run_single_check()
        # Exit with appropriate code
        sys.exit(0 if status_info['status'] == 'up' else 1)

if __name__ == '__main__':
    main()