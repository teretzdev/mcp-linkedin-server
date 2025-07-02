#!/usr/bin/env python3
"""
Performance Monitor for LinkedIn Job Hunter System
Monitors system resources and service health
"""

import psutil
import time
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and service health"""
    
    def __init__(self):
        self.metrics = []
        self.services = {
            'api_bridge': {'port': 8001, 'status': 'unknown'},
            'react_frontend': {'port': 3000, 'status': 'unknown'},
            'mcp_backend': {'process': 'python.exe', 'status': 'unknown'}
        }
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'network_connections': len(psutil.net_connections()),
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def check_service_health(self, port: int) -> bool:
        """Check if a service is responding on a port"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def check_process_running(self, process_name: str) -> bool:
        """Check if a process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception:
            return False
    
    async def check_api_health(self, port: int) -> Dict[str, Any]:
        """Check API health via HTTP request"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'http://localhost:{port}/api/health') as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'response_time': response.headers.get('X-Response-Time', 'unknown'),
                            'data': data
                        }
                    else:
                        return {'status': 'unhealthy', 'status_code': response.status}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        
        for service_name, config in self.services.items():
            if 'port' in config:
                # Check port-based service
                is_healthy = self.check_service_health(config['port'])
                status[service_name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'port': config['port'],
                    'last_check': datetime.now().isoformat()
                }
            elif 'process' in config:
                # Check process-based service
                is_running = self.check_process_running(config['process'])
                status[service_name] = {
                    'status': 'running' if is_running else 'stopped',
                    'process': config['process'],
                    'last_check': datetime.now().isoformat()
                }
        
        return status
    
    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        # Get system metrics
        system_metrics = self.get_system_metrics()
        
        # Get service status
        service_status = self.get_service_status()
        
        # Check API health if available
        api_health = await self.check_api_health(8001)
        
        # Compile report
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': system_metrics,
            'services': service_status,
            'api_health': api_health,
            'alerts': self.check_alerts(system_metrics)
        }
        
        # Store metrics
        self.metrics.append(report)
        
        # Keep only last 100 metrics
        if len(self.metrics) > 100:
            self.metrics = self.metrics[-100:]
        
        return report
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """Check for performance alerts"""
        alerts = []
        
        if metrics.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']}%")
        
        if metrics.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics['memory_percent']}%")
        
        if metrics.get('disk_percent', 0) > self.alert_thresholds['disk_percent']:
            alerts.append(f"High disk usage: {metrics['disk_percent']}%")
        
        return alerts
    
    def save_metrics(self, filename: str = 'performance_metrics.json'):
        """Save metrics to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Metrics saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        # Calculate averages
        cpu_values = [m['system']['cpu_percent'] for m in self.metrics if 'system' in m]
        memory_values = [m['system']['memory_percent'] for m in self.metrics if 'system' in m]
        
        return {
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'avg_memory_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
            'total_metrics': len(self.metrics),
            'last_check': self.metrics[-1]['timestamp'] if self.metrics else None
        }

async def main():
    """Main monitoring loop"""
    monitor = PerformanceMonitor()
    
    print("🔍 LinkedIn Job Hunter Performance Monitor")
    print("=" * 50)
    
    try:
        while True:
            # Run monitoring cycle
            report = await monitor.run_monitoring_cycle()
            
            # Display current status
            print(f"\n📊 Status Update - {datetime.now().strftime('%H:%M:%S')}")
            print(f"CPU: {report['system'].get('cpu_percent', 0):.1f}% | "
                  f"Memory: {report['system'].get('memory_percent', 0):.1f}% | "
                  f"Disk: {report['system'].get('disk_percent', 0):.1f}%")
            
            # Display service status
            for service, status in report['services'].items():
                status_icon = "✅" if status['status'] in ['healthy', 'running'] else "❌"
                print(f"{status_icon} {service}: {status['status']}")
            
            # Display alerts
            if report['alerts']:
                print("\n⚠️  Alerts:")
                for alert in report['alerts']:
                    print(f"  - {alert}")
            
            # Save metrics every 10 cycles
            if len(monitor.metrics) % 10 == 0:
                monitor.save_metrics()
            
            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        monitor.save_metrics()
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
        monitor.save_metrics()

if __name__ == "__main__":
    asyncio.run(main()) 