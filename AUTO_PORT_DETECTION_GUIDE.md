# Auto-Port Detection System Guide

## Overview

The LinkedIn MCP Server now includes an intelligent auto-port detection system that automatically handles port conflicts and finds available ports for all services. This eliminates the need for manual intervention when ports are already in use.

## 🚀 Key Features

### Automatic Port Detection
- **Smart Port Finding**: Automatically finds the next available port in a predefined range
- **Conflict Resolution**: Kills existing processes on conflicting ports
- **Port Persistence**: Remembers previously used ports for faster startup
- **Fallback Support**: Multiple fallback mechanisms if primary methods fail

### Service Port Ranges
- **React Frontend**: 3000-3009
- **API Bridge**: 8001-8010
- **MCP Backend**: 8101-8110
- **LLM Controller**: 8201-8210

## 📁 New Files Created

### 1. `start_frontend_auto.py`
**Purpose**: Intelligent React frontend startup with auto-port detection

**Features**:
- Finds available ports automatically
- Kills conflicting processes
- Saves port information to `service_ports.json`
- Handles startup failures gracefully
- Supports Ctrl+C graceful shutdown

**Usage**:
```bash
python start_frontend_auto.py
```

### 2. `start_frontend_auto.bat`
**Purpose**: Windows batch file wrapper for the Python auto-start script

**Features**:
- Checks for Python installation
- Falls back to regular npm start if auto-script fails
- Provides clear error messages

**Usage**:
```bash
start_frontend_auto.bat
```

### 3. `start_frontend_auto.ps1`
**Purpose**: PowerShell script with advanced port management

**Features**:
- Uses PowerShell's native networking capabilities
- More robust process termination
- Better error handling

**Usage**:
```powershell
.\start_frontend_auto.ps1
```

## 🔧 Updated Files

### 1. `auto_startup.py`
**Changes**:
- Updated `start_react_frontend()` method to use auto-start script
- Improved port conflict handling
- Better error recovery
- Uses root directory instead of legacy directory

### 2. `start_frontend.bat`
**Changes**:
- Added automatic port conflict resolution
- Kills existing processes on ports 3000-3002
- Tries multiple ports automatically
- Better error handling

## 🎯 How It Works

### Port Detection Algorithm
1. **Check Last Used Port**: First tries to use the last successfully used port
2. **Scan Port Range**: If last port is busy, scans through the port range
3. **Kill Conflicts**: Automatically terminates processes on conflicting ports
4. **Start Service**: Launches the service on the available port
5. **Save Port**: Records the successful port for future use

### Process Management
```python
def find_available_port(start_port=3000, max_attempts=10):
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None
```

### Conflict Resolution
```python
def kill_process_on_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            process = psutil.Process(conn.pid)
            process.terminate()
            process.wait(timeout=5)
```

## 📊 Port Information Storage

### `service_ports.json`
The system automatically creates and maintains a `service_ports.json` file:

```json
{
  "api_bridge": 8002,
  "mcp_backend": 8101,
  "llm_controller": 8201,
  "react_frontend": 3000
}
```

This file is used to:
- Remember successful port assignments
- Speed up subsequent startups
- Provide port information to other scripts

## 🧪 Testing

### Test Script: `test_port_conflict.py`
Run comprehensive tests of the port conflict resolution:

```bash
python test_port_conflict.py
```

**Tests Include**:
- Port availability detection
- Process termination
- Multiple concurrent starts
- Cleanup verification

## 🚀 Usage Examples

### 1. Start Frontend with Auto-Port Detection
```bash
# Using Python script
python start_frontend_auto.py

# Using batch file
start_frontend_auto.bat

# Using PowerShell
.\start_frontend_auto.ps1
```

### 2. Start All Services with Auto-Port Detection
```bash
python auto_startup.py
```

### 3. Manual Port Management
```bash
# Kill processes on specific ports
python -c "from start_frontend_auto import kill_process_on_port; kill_process_on_port(3000)"

# Find available port
python -c "from start_frontend_auto import find_available_port; print(find_available_port(3000))"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Still in Use
**Symptoms**: "Address already in use" error
**Solution**: The auto-script should handle this automatically, but you can manually kill processes:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /F /PID <PID>

# Or use the built-in function
python -c "from start_frontend_auto import kill_process_on_port; kill_process_on_port(3000)"
```

#### 2. Python Script Not Found
**Symptoms**: "start_frontend_auto.py not found"
**Solution**: Ensure you're in the correct directory or use the batch file which has fallback logic.

#### 3. Permission Denied
**Symptoms**: "Access denied" when killing processes
**Solution**: Run as administrator or use the PowerShell script which has better permission handling.

### Debug Mode
Enable debug logging by setting the environment variable:
```bash
set DEBUG=1
python start_frontend_auto.py
```

## 📈 Benefits

### For Developers
- **No More Manual Intervention**: Automatically handles port conflicts
- **Faster Development**: No need to manually find and kill processes
- **Consistent Behavior**: Same behavior across different environments
- **Better Error Handling**: Graceful fallbacks and clear error messages

### For Users
- **Seamless Experience**: Just run the script and it works
- **No Technical Knowledge Required**: Handles all port management automatically
- **Reliable Startup**: Multiple fallback mechanisms ensure success

## 🔮 Future Enhancements

### Planned Features
1. **Dynamic Port Ranges**: Configurable port ranges per service
2. **Health Monitoring**: Automatic restart of failed services
3. **Load Balancing**: Distribute services across multiple ports
4. **Docker Integration**: Support for containerized deployments
5. **Web Interface**: Visual port management dashboard

### Configuration Options
```json
{
  "port_ranges": {
    "react_frontend": [3000, 3010],
    "api_bridge": [8001, 8010]
  },
  "auto_restart": true,
  "health_check_interval": 30
}
```

## 📝 Summary

The auto-port detection system transforms the startup experience from a manual, error-prone process into a smooth, automated operation. It eliminates the most common startup issues and provides a robust foundation for the LinkedIn MCP Server's development and deployment workflows.

**Key Takeaways**:
- ✅ Automatic port conflict resolution
- ✅ Intelligent port finding and persistence
- ✅ Multiple startup methods (Python, Batch, PowerShell)
- ✅ Comprehensive error handling and fallbacks
- ✅ Easy testing and debugging tools
- ✅ Seamless integration with existing automation

The system is now production-ready and handles all the edge cases that previously required manual intervention! 