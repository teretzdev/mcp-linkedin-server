# Automation Guide - LinkedIn Job Hunter

> **Note:** Docker is **NOT** required or used for this automation system. All automation is handled with native scripts and Python—no containerization is involved.

This guide explains how to use the automated startup and management features to avoid manual intervention.

## Overview

The LinkedIn Job Hunter application now includes several automation features that handle common scenarios that previously required manual intervention:

- **Port Conflicts**: Automatically finds available ports when the default ports are in use
- **Process Management**: Automatically kills conflicting processes and manages service lifecycle
- **Service Dependencies**: Ensures services start in the correct order and wait for dependencies
- **Error Recovery**: Handles common startup errors and provides detailed logging
- **Graceful Shutdown**: Properly terminates all services when stopping the application

## Automation Scripts

### 1. `start_auto.bat` (Recommended)
The main automation script that handles everything automatically.

**Features:**
- Checks Python installation
- Installs missing dependencies
- Runs the Python automation script
- Provides detailed logging

**Usage:**
```bash
start_auto.bat
```

### 2. `auto_startup.py`
The core Python automation script that manages all services.

**Features:**
- Automatic port detection and assignment
- Process cleanup and management
- Service health monitoring
- Graceful shutdown handling
- Comprehensive logging

**Usage:**
```bash
python auto_startup.py
```

### 3. `start_all_auto.bat`
Enhanced batch script with automation features.

**Features:**
- Automatic port conflict resolution
- Process cleanup
- Service verification
- Browser auto-launch

**Usage:**
```bash
start_all_auto.bat
```

### 4. `start_frontend_auto.bat`
Automated frontend startup with port detection.

**Features:**
- Finds available port starting from 3000
- Sets PORT environment variable
- No manual intervention required

**Usage:**
```bash
start_frontend_auto.bat
```

## How Automation Works

### Port Conflict Resolution

When a port is in use, the automation system:

1. **Detects** the conflict using socket binding
2. **Finds** the next available port
3. **Updates** environment variables accordingly
4. **Starts** the service on the new port
5. **Logs** the port change for user awareness

```python
def find_available_port(self, start_port: int) -> int:
    port = start_port
    attempts = 0
    
    while attempts < self.max_port_attempts:
        if self.check_port_available(port):
            return port
        port += 1
        attempts += 1
```

### Process Management

The system automatically:

1. **Scans** for processes using required ports
2. **Terminates** conflicting processes gracefully
3. **Waits** for ports to be released
4. **Starts** new services
5. **Monitors** service health

```python
def kill_process_on_port(self, port: int) -> bool:
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        # Find and terminate process using the port
        proc.terminate()
        proc.wait(timeout=5)
```

### Service Dependencies

Services start in the correct order:

1. **API Bridge** (port 8001) - Core API service
2. **MCP Backend** (port 8002) - LinkedIn automation
3. **LLM Controller** (port 8003) - AI services
4. **React Frontend** (port 3000+) - User interface

Each service waits for the previous one to be ready before starting.

### Health Monitoring

The system continuously monitors service health:

```python
def wait_for_service(self, url: str, timeout: int = 30) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False
```

## Common Scenarios Handled

### Scenario 1: Port 3000 Already in Use
**Before:** Manual intervention required to choose different port
**After:** Automatically finds next available port (3001, 3002, etc.)

### Scenario 2: Previous Session Not Cleaned Up
**Before:** Manual process termination required
**After:** Automatically kills conflicting processes

### Scenario 3: Missing .env File
**Before:** Manual creation required
**After:** Automatically creates .env file if missing

### Scenario 4: Service Startup Failure
**Before:** Manual troubleshooting required
**After:** Detailed logging and automatic retry logic

### Scenario 5: Graceful Shutdown
**Before:** Manual process termination required
**After:** Ctrl+C properly terminates all services

## Logging and Monitoring

### Log Files
- `startup.log` - Detailed startup process logging
- Console output - Real-time status updates

### Log Levels
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures

### Example Log Output
```
2024-01-15 10:30:15 - INFO - Starting LinkedIn Job Hunter - Automated Mode
2024-01-15 10:30:15 - INFO - Creating .env file...
2024-01-15 10:30:16 - INFO - Successfully created .env file
2024-01-15 10:30:16 - INFO - Port 3000 is in use, using port 3001
2024-01-15 10:30:16 - INFO - Starting API Bridge on port 8001...
2024-01-15 10:30:19 - INFO - API Bridge started successfully
2024-01-15 10:30:19 - INFO - Starting React frontend on port 3001...
2024-01-15 10:30:25 - INFO - React frontend started successfully on port 3001
2024-01-15 10:30:25 - INFO - All services started successfully!
```

## Troubleshooting

### Common Issues

1. **Python Not Found**
   - Ensure Python 3.7+ is installed and in PATH
   - Run `python --version` to verify

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - The automation script will attempt to install missing packages

3. **Permission Issues**
   - Run as administrator if needed
   - Check firewall settings

4. **Service Startup Failures**
   - Check `startup.log` for detailed error messages
   - Verify all required files exist
   - Check network connectivity

### Manual Override

If automation fails, you can still use manual startup:

```bash
# Manual startup (requires manual intervention)
start_all.bat

# Or individual services
start_api_bridge.bat
start_frontend.bat
```

## Best Practices

1. **Use `start_auto.bat`** for the best automation experience
2. **Check logs** if issues occur
3. **Keep dependencies updated** with `pip install -r requirements.txt`
4. **Use Ctrl+C** for graceful shutdown
5. **Monitor startup.log** for detailed information

## Future Enhancements

Planned automation improvements:

- **Auto-restart** on service failure
- **Configuration validation** before startup
- **Performance monitoring** and optimization
- **Docker containerization** for consistent environments
- **CI/CD integration** for automated testing

## Support

For issues with automation:

1. Check the `startup.log` file
2. Review this guide
3. Try manual startup to isolate the issue
4. Check system requirements and dependencies

The automation system is designed to handle most common scenarios automatically, reducing the need for manual intervention and improving the user experience. 