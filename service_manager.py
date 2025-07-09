#!/usr/bin/env python3
"""
Comprehensive Service Manager for LinkedIn Job Automation
Handles service startup, health checks, port management, and process monitoring
"""

import os
import sys
import time
import json
import socket
import subprocess
import threading
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import psutil
import requests
import asyncio
import aiohttp
from datetime import datetime

import centralized_logging

logger = centralized_logging.get_logger("service_manager")

class ServiceManager:
    """Manages all services for the LinkedIn job automation system"""
    
    def __init__(self):
        self.services = {
            'api_bridge': {
                'script': 'api_bridge_with_database.py',
                'port': 8002,
                'health_path': '/api/health',
                'expected_response': {'status': 'ok'},
                'process': None,
                'pid': None,
                'status': 'stopped'
            },
            'mcp_backend': {
                'script': 'linkedin_browser_mcp.py',
                'port': 8101,
                'health_path': '/health',
                'expected_response': {'status': 'ok'},
                'process': None,
                'pid': None,
                'status': 'stopped'
            },
            'llm_controller': {
                'script': 'llm_controller.py',
                'port': 8201,
                'health_path': '/health',
                'expected_response': {'status': 'ok'},
                'process': None,
                'pid': None,
                'status': 'stopped'
            },
            'react_frontend': {
                'script': 'npm start',
                'port': 3000,
                'health_path': '/',
                'expected_response': None,  # Just check 200 status
                'process': None,
                'pid': None,
                'status': 'stopped',
                'working_dir': '.'
            }
        }
        
        self.config_file = Path('service_ports.json')
        self.load_config()
        
    def load_config(self):
        """Load service configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Update service ports from config
                for service_name, service_info in self.services.items():
                    if service_name in config:
                        service_info['port'] = config[service_name]
                        
                logger.log_info("Service configuration loaded successfully")
            except Exception as e:
                logger.log_error(f"Failed to load service configuration: {e}")
                
    def save_config(self):
        """Save current service configuration to file"""
        try:
            config = {
                service_name: service_info['port'] 
                for service_name, service_info in self.services.items()
            }
            config['started_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.log_info("Service configuration saved successfully")
        except Exception as e:
            logger.log_error(f"Failed to save service configuration: {e}")
            
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('localhost', port))
                return True
        except (socket.error, OSError):
            return False
            
    def kill_process_on_port(self, port: int):
        """Kill any process running on the specified port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if conn.laddr.port == port:
                                logger.log_info(f"Killing process {proc.info['pid']} on port {port}")
                                proc.kill()
                                time.sleep(1)
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.log_error(f"Error killing process on port {port}: {e}")
        return False
        
    def check_service_health(self, service_name: str, timeout: int = 5) -> bool:
        """Check if a service is healthy"""
        service_info = self.services.get(service_name)
        if not service_info:
            return False
            
        port = service_info['port']
        health_path = service_info['health_path']
        expected_response = service_info['expected_response']
        
        try:
            url = f"http://localhost:{port}{health_path}"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                if expected_response:
                    try:
                        json_response = response.json()
                        return json_response.get('status') == expected_response.get('status')
                    except:
                        return False
                else:
                    return True
            return False
        except Exception as e:
            logger.log_debug(f"Health check failed for {service_name}: {e}")
            return False
            
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        service_info = self.services.get(service_name)
        if not service_info:
            logger.log_error(f"Unknown service: {service_name}")
            return False
            
        port = service_info['port']
        script = service_info['script']
        
        # Check if already running and healthy
        if self.check_service_health(service_name):
            logger.log_info(f"{service_name} is already running and healthy on port {port}")
            service_info['status'] = 'running'
            return True
            
        # Kill any existing process on the port
        if not self.is_port_available(port):
            logger.log_info(f"Port {port} is occupied, killing existing process")
            self.kill_process_on_port(port)
            time.sleep(2)
            
        # Start the service
        try:
            logger.log_info(f"Starting {service_name} on port {port}...")
            
            if service_name == 'react_frontend':
                # Special handling for React frontend
                working_dir = service_info.get('working_dir', '.')
                process = subprocess.Popen(
                    ['npm', 'start'],
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env={**os.environ, 'PORT': str(port)}
                )
            else:
                # Python services
                process = subprocess.Popen(
                    [sys.executable, script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            service_info['process'] = process
            service_info['pid'] = process.pid
            service_info['status'] = 'starting'
            
            # Wait for service to start
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_service_health(service_name):
                    service_info['status'] = 'running'
                    logger.log_info(f"{service_name} started successfully on port {port}")
                    return True
                    
                time.sleep(1)
                wait_time += 1
                
                # Check if process is still running
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.log_error(f"{service_name} process exited with code {process.returncode}")
                    logger.log_error(f"stdout: {stdout.decode()}")
                    logger.log_error(f"stderr: {stderr.decode()}")
                    service_info['status'] = 'failed'
                    return False
                    
            logger.log_error(f"{service_name} failed to start within {max_wait} seconds")
            service_info['status'] = 'failed'
            return False
            
        except Exception as e:
            logger.log_error(f"Failed to start {service_name}: {e}")
            service_info['status'] = 'failed'
            return False
            
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        service_info = self.services.get(service_name)
        if not service_info:
            logger.log_error(f"Unknown service: {service_name}")
            return False
            
        try:
            process = service_info.get('process')
            if process and process.poll() is None:
                logger.log_info(f"Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.log_info(f"Force killing {service_name}...")
                    process.kill()
                    
            # Also kill any process on the port
            port = service_info['port']
            self.kill_process_on_port(port)
            
            service_info['process'] = None
            service_info['pid'] = None
            service_info['status'] = 'stopped'
            
            logger.log_info(f"{service_name} stopped successfully")
            return True
            
        except Exception as e:
            logger.log_error(f"Failed to stop {service_name}: {e}")
            return False
            
    def start_all_services(self) -> Dict[str, bool]:
        """Start all services in the correct order"""
        results = {}
        
        # Start services in dependency order
        service_order = ['api_bridge', 'mcp_backend', 'llm_controller', 'react_frontend']
        
        for service_name in service_order:
            logger.log_info(f"Starting {service_name}...")
            results[service_name] = self.start_service(service_name)
            
            if not results[service_name]:
                logger.log_error(f"Failed to start {service_name}, stopping startup process")
                break
                
            # Brief pause between services
            time.sleep(2)
            
        # Save configuration
        self.save_config()
        
        return results
        
    def stop_all_services(self) -> Dict[str, bool]:
        """Stop all services"""
        results = {}
        
        # Stop in reverse order
        service_order = ['react_frontend', 'llm_controller', 'mcp_backend', 'api_bridge']
        
        for service_name in service_order:
            results[service_name] = self.stop_service(service_name)
            
        return results
        
    def get_service_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        status = {}
        
        for service_name, service_info in self.services.items():
            is_healthy = self.check_service_health(service_name)
            
            status[service_name] = {
                'port': service_info['port'],
                'status': service_info['status'],
                'healthy': is_healthy,
                'pid': service_info.get('pid'),
                'script': service_info['script']
            }
            
        return status
        
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        logger.log_info(f"Restarting {service_name}...")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
        
    def monitor_services(self, interval: int = 30):
        """Monitor services and restart if they fail"""
        logger.log_info(f"Starting service monitoring with {interval}s interval")
        
        while True:
            try:
                for service_name in self.services:
                    if not self.check_service_health(service_name):
                        logger.log_warning(f"{service_name} is unhealthy, restarting...")
                        self.restart_service(service_name)
                        
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.log_info("Service monitoring stopped")
                break
            except Exception as e:
                logger.log_error(f"Error in service monitoring: {e}")
                time.sleep(interval)

def main():
    """Main entry point for service management"""
    if len(sys.argv) < 2:
        print("Usage: python service_manager.py <command>")
        print("Commands: start, stop, restart, status, monitor")
        sys.exit(1)
        
    command = sys.argv[1]
    service_manager = ServiceManager()
    
    if command == 'start':
        print("Starting all services...")
        results = service_manager.start_all_services()
        
        print("\nStartup Results:")
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            port = service_manager.services[service]['port']
            print(f"  {service} (port {port}): {status}")
            
    elif command == 'stop':
        print("Stopping all services...")
        results = service_manager.stop_all_services()
        
        print("\nStop Results:")
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {service}: {status}")
            
    elif command == 'restart':
        print("Restarting all services...")
        service_manager.stop_all_services()
        time.sleep(3)
        results = service_manager.start_all_services()
        
        print("\nRestart Results:")
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            port = service_manager.services[service]['port']
            print(f"  {service} (port {port}): {status}")
            
    elif command == 'status':
        print("Service Status:")
        status = service_manager.get_service_status()
        
        for service, info in status.items():
            health = "✅ HEALTHY" if info['healthy'] else "❌ UNHEALTHY"
            print(f"  {service} (port {info['port']}): {info['status']} - {health}")
            
    elif command == 'monitor':
        service_manager.monitor_services()
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 