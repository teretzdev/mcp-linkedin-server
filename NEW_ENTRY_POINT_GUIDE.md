# New Entry Point Guide - start_auto

## 🎯 Overview

The LinkedIn MCP Server now has a new main entry point: **`start_auto.py`** that provides a comprehensive, intelligent startup system with automatic port detection and dependency management.

## 🚀 New Entry Point: `start_auto.py`

### **What It Does:**
- ✅ **Dependency Check**: Verifies Node.js and npm are installed
- ✅ **Auto-Install**: Installs npm dependencies if missing
- ✅ **Port Management**: Automatically finds available ports
- ✅ **Process Cleanup**: Kills conflicting processes
- ✅ **Multi-Service**: Starts both API Bridge and React frontend
- ✅ **Browser Launch**: Automatically opens the application
- ✅ **Graceful Shutdown**: Handles Ctrl+C properly

### **Usage:**
```bash
# Direct Python execution
python start_auto.py

# Using batch wrapper
start_auto.bat
```

## 📁 Updated File Structure

### **New Files:**
1. **`start_auto.py`** - Main entry point (NEW)
2. **`start_auto.bat`** - Windows batch wrapper (NEW)

### **Updated Files:**
1. **`start_frontend_auto.py`** - Now focuses only on frontend
2. **`start_frontend_auto.bat`** - Updated to use new structure
3. **`auto_startup.py`** - Updated to use new entry point

## 🔧 How It Works

### **Startup Sequence:**
1. **Dependency Check** → Verifies Node.js and npm
2. **Install Dependencies** → Runs `npm install` if needed
3. **Port Detection** → Finds available port (3000-3009)
4. **Process Cleanup** → Kills conflicting processes
5. **API Bridge Start** → Starts backend service
6. **React Start** → Starts frontend on available port
7. **Browser Launch** → Opens application automatically

### **Port Management:**
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

### **Process Management:**
```python
def kill_process_on_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            process = psutil.Process(conn.pid)
            process.terminate()
            process.wait(timeout=5)
```

## 🎯 Usage Examples

### **1. Start Everything (Recommended)**
```bash
# Using Python directly
python start_auto.py

# Using batch file
start_auto.bat
```

### **2. Start Frontend Only**
```bash
# Using Python script
python start_frontend_auto.py

# Using batch file
start_frontend_auto.bat
```

### **3. Legacy Methods (Still Work)**
```bash
# Original automation
python auto_startup.py

# Direct npm start
npm start
```

## 📊 Port Information Storage

### **`service_ports.json`**
The system automatically creates and maintains port information:

```json
{
  "frontend_port": 3000,
  "frontend_url": "http://localhost:3000",
  "started_at": "2025-07-05 05:38:07"
}
```

## 🔍 Troubleshooting

### **Common Issues & Solutions:**

#### **1. "npm not found" Error**
**Solution**: The script now automatically finds npm path using `shutil.which('npm')`

#### **2. Port Conflicts**
**Solution**: Automatic port detection and process cleanup

#### **3. Dependencies Missing**
**Solution**: Automatic `npm install` if `node_modules` doesn't exist

#### **4. API Bridge Not Found**
**Solution**: Falls back from `api_bridge_with_database.py` to `api_bridge.py`

## 🚀 Benefits of New Entry Point

### **For Developers:**
- **Single Command**: One script starts everything
- **Intelligent**: Handles all edge cases automatically
- **Robust**: Multiple fallback mechanisms
- **Informative**: Clear status messages and error reporting

### **For Users:**
- **Simple**: Just run `start_auto.bat` or `python start_auto.py`
- **Reliable**: No manual intervention required
- **Fast**: Automatic dependency installation and port detection
- **Complete**: Starts both frontend and backend services

## 📈 Comparison: Old vs New

### **Before (Manual Process):**
1. Check if Node.js installed
2. Run `npm install` manually
3. Check if port 3000 available
4. Kill processes manually if needed
5. Start API bridge manually
6. Start React app manually
7. Open browser manually

### **After (Automated):**
1. Run `python start_auto.py`
2. Everything happens automatically! 🎉

## 🔮 Future Enhancements

### **Planned Features:**
1. **Health Monitoring**: Automatic restart of failed services
2. **Configuration File**: Customizable port ranges and settings
3. **Docker Support**: Containerized deployment options
4. **Web Dashboard**: Visual service management interface

### **Configuration Options:**
```json
{
  "port_ranges": {
    "frontend": [3000, 3010],
    "api_bridge": [8001, 8010]
  },
  "auto_restart": true,
  "health_check_interval": 30
}
```

## 📝 Summary

The new `start_auto.py` entry point transforms the startup experience from a complex, multi-step process into a single, intelligent command that handles everything automatically.

**Key Advantages:**
- ✅ **One Command**: `python start_auto.py` starts everything
- ✅ **Auto-Port Detection**: No more port conflicts
- ✅ **Dependency Management**: Automatic installation and verification
- ✅ **Process Management**: Intelligent cleanup and startup
- ✅ **Error Handling**: Comprehensive fallback mechanisms
- ✅ **User-Friendly**: Clear status messages and progress indicators

**The system is now production-ready and handles all the edge cases that previously required manual intervention!** 🚀 