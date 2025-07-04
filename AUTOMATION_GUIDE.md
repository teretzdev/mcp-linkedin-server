# 🤖 Automation Guide - LinkedIn Job Hunter

> **Note:** Docker is **NOT** required or used for this automation system. All automation is handled with native scripts and Python—no containerization is involved.

This guide explains how to use the automated startup and management features to avoid manual intervention and ensure reliable operation.

## 🎯 Overview

The LinkedIn Job Hunter application now includes comprehensive automation features that handle common scenarios that previously required manual intervention:

- **Port Conflicts**: Automatically finds available ports when the default ports are in use
- **Process Management**: Automatically kills conflicting processes and manages service lifecycle
- **Service Dependencies**: Ensures services start in the correct order and wait for dependencies
- **Error Recovery**: Handles common startup errors and provides detailed logging
- **Graceful Shutdown**: Properly terminates all services when stopping the application
- **Health Monitoring**: Continuous monitoring of service health and automatic recovery
- **Dependency Management**: Automatic installation and verification of required dependencies

## 🚀 Automation Scripts

### 1. `start_auto.bat` (Recommended)
The main automation script that handles everything automatically.

**Features:**
- ✅ Checks Python installation and version
- ✅ Installs missing dependencies automatically
- ✅ Runs the Python automation script with comprehensive logging
- ✅ Provides detailed status updates
- ✅ Handles errors gracefully

**Usage:**
```bash
start_auto.bat
```

**Example Output:**
```
Starting LinkedIn Job Hunter - Automated Mode
✅ Python 3.9.7 detected
✅ Virtual environment activated
✅ Dependencies verified
✅ Port conflicts resolved
✅ Services starting...
✅ All services running successfully!
```

### 2. `auto_startup.py`
The core Python automation script that manages all services.

**Features:**
- 🔄 Automatic port detection and assignment
- 🧹 Process cleanup and management
- 📊 Service health monitoring
- 🛡️ Graceful shutdown handling
- 📝 Comprehensive logging
- 🔧 Dependency verification
- 🚨 Error recovery mechanisms

**Usage:**
```bash
python auto_startup.py
```

**Advanced Options:**
```bash
# Run with specific configuration
python auto_startup.py --config production.json

# Run with verbose logging
python auto_startup.py --verbose

# Run with health monitoring
python auto_startup.py --monitor

# Run with automatic recovery
python auto_startup.py --auto-recover
```

### 3. `start_all_auto.bat`
Enhanced batch script with advanced automation features.

**Features:**
- 🔄 Automatic port conflict resolution
- 🧹 Intelligent process cleanup
- ✅ Service verification and health checks
- 🌐 Browser auto-launch
- 📊 Real-time status monitoring
- 🚨 Error notification system

**Usage:**
```bash
start_all_auto.bat
```

### 4. `start_frontend_auto.bat`
Automated frontend startup with intelligent port detection.

**Features:**
- 🔍 Finds available port starting from 3000
- 🔧 Sets PORT environment variable automatically
- 🚀 No manual intervention required
- 📊 Status reporting

**Usage:**
```bash
start_frontend_auto.bat
```

## 🔧 How Automation Works

### Port Conflict Resolution

When a port is in use, the automation system:

1. **Detects** the conflict using socket binding
2. **Finds** the next available port automatically
3. **Updates** environment variables accordingly
4. **Starts** the service on the new port
5. **Logs** the port change for user awareness
6. **Notifies** the user of the change

```python
def find_available_port(self, start_port: int) -> int:
    port = start_port
    attempts = 0
    
    while attempts < self.max_port_attempts:
        if self.check_port_available(port):
            self.logger.info(f"Found available port: {port}")
            return port
        port += 1
        attempts += 1
    
    raise RuntimeError(f"No available ports found after {self.max_port_attempts} attempts")
```

### Process Management

The system automatically:

1. **Scans** for processes using required ports
2. **Identifies** conflicting processes
3. **Terminates** processes gracefully
4. **Waits** for ports to be released
5. **Starts** new services
6. **Monitors** service health continuously

```python
def kill_process_on_port(self, port: int) -> bool:
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                # Windows-compatible process checking
                if hasattr(proc, 'connections'):
                    connections = proc.connections()
                else:
                    # Fallback for older psutil versions
                    connections = []
                
                for conn in connections:
                    if conn.laddr.port == port:
                        self.logger.info(f"Terminating process {proc.pid} using port {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        self.logger.error(f"Error killing process on port {port}: {e}")
        return False
```

### Service Dependencies

Services start in the correct order with dependency checking:

1. **API Bridge** (port 8001) - Core API service
2. **MCP Backend** (port 8002) - LinkedIn automation
3. **LLM Controller** (port 8003) - AI services
4. **React Frontend** (port 3000+) - User interface

Each service waits for the previous one to be ready before starting:

```python
def start_services_sequentially(self):
    services = [
        {"name": "API Bridge", "port": 8001, "script": "api_bridge.py"},
        {"name": "MCP Backend", "port": 8002, "script": "linkedin_browser_mcp.py"},
        {"name": "LLM Controller", "port": 8003, "script": "llm_controller.py"},
        {"name": "React Frontend", "port": 3000, "script": "npm start"}
    ]
    
    for service in services:
        self.logger.info(f"Starting {service['name']}...")
        success = self.start_service(service)
        if not success:
            raise RuntimeError(f"Failed to start {service['name']}")
        
        # Wait for service to be ready
        if not self.wait_for_service(f"http://localhost:{service['port']}/health"):
            raise RuntimeError(f"{service['name']} failed to become ready")
```

### Health Monitoring

The system continuously monitors service health:

```python
def wait_for_service(self, url: str, timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                self.logger.info(f"Service at {url} is ready")
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    
    self.logger.error(f"Service at {url} failed to become ready within {timeout}s")
    return False
```

### Dependency Management

Automatic dependency verification and installation:

```python
def verify_dependencies(self):
    """Verify and install required dependencies"""
    required_packages = [
        "fastapi", "uvicorn", "playwright", "psutil", 
        "PyJWT", "requests", "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        self.logger.info(f"Installing missing packages: {missing_packages}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + missing_packages)
```

## 🔄 Common Scenarios Handled

### Scenario 1: Port 3000 Already in Use
**Before:** Manual intervention required to choose different port
**After:** Automatically finds next available port (3001, 3002, etc.)

```bash
# Automatic resolution
Port 3000 is in use, using port 3001
React frontend started successfully on port 3001
```

### Scenario 2: Previous Session Not Cleaned Up
**Before:** Manual process termination required
**After:** Automatically kills conflicting processes

```bash
# Automatic cleanup
Found conflicting process on port 8001 (PID: 1234)
Terminating process 1234
Process terminated successfully
```

### Scenario 3: Missing .env File
**Before:** Manual creation required
**After:** Automatically creates .env file if missing

```bash
# Automatic creation
.env file not found, creating with default configuration
Successfully created .env file
```

### Scenario 4: Service Startup Failure
**Before:** Manual troubleshooting required
**After:** Detailed logging and automatic retry logic

```bash
# Automatic retry
Service startup failed, retrying in 5 seconds...
Retry 1/3: Starting service...
Service started successfully on retry 1
```

### Scenario 5: Graceful Shutdown
**Before:** Manual process termination required
**After:** Ctrl+C properly terminates all services

```bash
# Graceful shutdown
Received shutdown signal
Terminating all services...
Services terminated successfully
```

### Scenario 6: Dependency Issues
**Before:** Manual dependency installation required
**After:** Automatic dependency verification and installation

```bash
# Automatic dependency management
Checking dependencies...
Missing: PyJWT
Installing PyJWT...
Dependencies verified successfully
```

## 📊 Logging and Monitoring

### Log Files
- `startup.log` - Detailed startup process logging
- `automation.log` - Automation-specific events
- `health.log` - Service health monitoring
- Console output - Real-time status updates

### Log Levels
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures
- **DEBUG**: Detailed debugging information

### Example Log Output
```
2024-01-15 10:30:15 - INFO - Starting LinkedIn Job Hunter - Automated Mode
2024-01-15 10:30:15 - INFO - Python 3.9.7 detected
2024-01-15 10:30:15 - INFO - Virtual environment activated
2024-01-15 10:30:16 - INFO - Dependencies verified successfully
2024-01-15 10:30:16 - INFO - Port 3000 is in use, using port 3001
2024-01-15 10:30:16 - INFO - Starting API Bridge on port 8001...
2024-01-15 10:30:19 - INFO - API Bridge started successfully
2024-01-15 10:30:19 - INFO - Starting React frontend on port 3001...
2024-01-15 10:30:25 - INFO - React frontend started successfully on port 3001
2024-01-15 10:30:25 - INFO - All services started successfully!
2024-01-15 10:30:25 - INFO - Opening dashboard in browser...
```

### Health Monitoring Dashboard
```python
def health_dashboard(self):
    """Display real-time health status"""
    services = [
        {"name": "API Bridge", "url": "http://localhost:8001/health"},
        {"name": "MCP Backend", "url": "http://localhost:8002/health"},
        {"name": "React Frontend", "url": "http://localhost:3000"}
    ]
    
    for service in services:
        status = "🟢 Online" if self.check_service_health(service["url"]) else "🔴 Offline"
        print(f"{service['name']}: {status}")
```

## 🔧 Configuration Options

### Automation Configuration
```json
{
  "automation": {
    "max_port_attempts": 10,
    "service_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5,
    "auto_install_dependencies": true,
    "auto_fix_ports": true,
    "health_monitoring": true,
    "graceful_shutdown": true
  }
}
```

### Environment-Specific Settings
```bash
# Development
AUTOMATION_VERBOSE=true
AUTOMATION_AUTO_FIX=true
AUTOMATION_HEALTH_MONITOR=true

# Production
AUTOMATION_VERBOSE=false
AUTOMATION_AUTO_FIX=true
AUTOMATION_HEALTH_MONITOR=true
```

## 🚨 Troubleshooting

### Common Issues

1. **Python Not Found**
   - Ensure Python 3.7+ is installed and in PATH
   - Run `python --version` to verify
   - Check virtual environment activation

2. **Missing Dependencies**
   ```bash
   # Manual dependency installation
   pip install -r requirements.txt
   
   # Or let automation handle it
   python auto_startup.py --auto-install
   ```

3. **Port Conflicts Persist**
   ```bash
   # Manual port cleanup
   netstat -ano | findstr :8001
   taskkill /PID <PID> /F
   
   # Or use automation
   python auto_startup.py --force-cleanup
   ```

4. **Service Startup Failures**
   ```bash
   # Check logs
   tail -f startup.log
   
   # Run with verbose logging
   python auto_startup.py --verbose
   
   # Run with debug mode
   python auto_startup.py --debug
   ```

### Debug Mode
```bash
# Enable debug logging
python auto_startup.py --debug

# Enable verbose output
python auto_startup.py --verbose

# Enable step-by-step execution
python auto_startup.py --step-by-step
```

## 🔄 Advanced Automation Features

### Scheduled Automation
```bash
# Windows Task Scheduler
schtasks /create /tn "LinkedInAutoStart" /tr "python auto_startup.py" /sc onstart

# Or use cron (if available)
@reboot cd /path/to/mcp-linkedin-server && python auto_startup.py
```

### Auto-Recovery
```python
def auto_recovery(self):
    """Automatic recovery from failures"""
    while True:
        try:
            # Check all services
            for service in self.services:
                if not self.check_service_health(service["url"]):
                    self.logger.warning(f"Service {service['name']} is down, restarting...")
                    self.restart_service(service)
            
            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            break
```

### Performance Monitoring
```python
def monitor_performance(self):
    """Monitor system performance"""
    import psutil
    
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    if cpu_percent > 80 or memory_percent > 80:
        self.logger.warning(f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%")
```

## 📚 Additional Resources

### Automation Scripts
- `auto_startup.py` - Main automation script
- `start_auto.bat` - Windows batch automation
- `start_all_auto.bat` - Enhanced automation
- `start_frontend_auto.bat` - Frontend automation

### Configuration Files
- `automation_config.json` - Automation settings
- `service_config.json` - Service configuration
- `health_config.json` - Health monitoring settings

### Documentation
- [Automation API Reference](docs/automation-api.md)
- [Service Management Guide](docs/service-management.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

---

**Remember**: The automation system is designed to handle most common issues automatically. If you encounter persistent problems, check the logs and consider running in debug mode for detailed information. 