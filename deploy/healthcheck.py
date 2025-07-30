#!/usr/bin/env python3
"""
Production Health Check Script for SERP Strategist API
Enterprise-grade health monitoring with comprehensive checks
"""

import sys
import json
import time
import psutil
import requests
from datetime import datetime

class HealthChecker:
    def __init__(self):
        self.checks = {}
        self.overall_healthy = True
        
    def check_api_endpoint(self):
        """Check if API is responding"""
        try:
            response = requests.get('http://localhost:5000/health', timeout=10)
            if response.status_code == 200:
                self.checks['api_endpoint'] = {'status': 'healthy', 'response_time': response.elapsed.total_seconds()}
            else:
                self.checks['api_endpoint'] = {'status': 'unhealthy', 'error': f'HTTP {response.status_code}'}
                self.overall_healthy = False
        except Exception as e:
            self.checks['api_endpoint'] = {'status': 'unhealthy', 'error': str(e)}
            self.overall_healthy = False
    
    def check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            self.checks['system_resources'] = {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
            
            # Alert thresholds
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
                self.checks['system_resources']['status'] = 'warning'
                if cpu_percent > 95 or memory_percent > 95 or disk_percent > 98:
                    self.checks['system_resources']['status'] = 'critical'
                    self.overall_healthy = False
                    
        except Exception as e:
            self.checks['system_resources'] = {'status': 'unhealthy', 'error': str(e)}
            self.overall_healthy = False
    
    def check_database(self):
        """Check database connectivity"""
        try:
            # Simple database check - file exists and is accessible
            import sqlite3
            conn = sqlite3.connect('/app/data/serp_strategist_prod.db', timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.checks['database'] = {'status': 'healthy'}
            else:
                self.checks['database'] = {'status': 'unhealthy', 'error': 'No response from database'}
                self.overall_healthy = False
                
        except Exception as e:
            self.checks['database'] = {'status': 'unhealthy', 'error': str(e)}
            self.overall_healthy = False
    
    def check_google_apis(self):
        """Check Google APIs connectivity"""
        try:
            # Check if we can make a simple API call
            response = requests.get('http://localhost:5000/api/status', timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('google_apis_status', {}).get('enabled'):
                    self.checks['google_apis'] = {'status': 'healthy'}
                else:
                    self.checks['google_apis'] = {'status': 'warning', 'message': 'APIs not enabled'}
            else:
                self.checks['google_apis'] = {'status': 'unhealthy', 'error': f'Status check failed: {response.status_code}'}
                self.overall_healthy = False
                
        except Exception as e:
            self.checks['google_apis'] = {'status': 'unhealthy', 'error': str(e)}
            self.overall_healthy = False
    
    def run_all_checks(self):
        """Run all health checks"""
        print(f"🏥 Running health checks at {datetime.now()}")
        
        self.check_api_endpoint()
        self.check_system_resources() 
        self.check_database()
        self.check_google_apis()
        
        # Generate health report
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if self.overall_healthy else 'unhealthy',
            'checks': self.checks
        }
        
        # Print summary
        print(f"🎯 Overall Status: {'✅ HEALTHY' if self.overall_healthy else '❌ UNHEALTHY'}")
        
        for check_name, result in self.checks.items():
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌',
                'critical': '🚨'
            }.get(result['status'], '❓')
            
            print(f"{status_emoji} {check_name}: {result['status']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        return health_report

if __name__ == '__main__':
    checker = HealthChecker()
    health_report = checker.run_all_checks()
    
    # Exit with proper code for Docker health check
    if health_report['overall_status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)