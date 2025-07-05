# LinkedIn Job Hunter - Refactored Project

## 🎯 Overview

This project has been refactored to provide a clean separation between the legacy LinkedIn Job Hunter codebase and the new enhanced MCP server, while maintaining shared resources and allowing for gradual migration.

## 📁 Project Structure

```
linkedin-job-hunter/
├── enhanced-mcp-server/           # New enhanced MCP server
│   ├── mcp_server/               # Enhanced MCP server core
│   │   ├── core/
│   │   │   ├── server.py         # Main MCP server
│   │   │   ├── browser_manager.py # Browser session management
│   │   │   ├── auth_manager.py   # Authentication handling
│   │   │   └── error_handler.py  # Error handling
│   │   ├── tools/                # MCP tools (to be implemented)
│   │   ├── models/               # Data models (to be implemented)
│   │   ├── database/             # Database layer (to be implemented)
│   │   └── utils/                # Utilities (to be implemented)
│   ├── config/
│   │   └── mcp_config.json       # Enhanced server configuration
│   ├── scripts/
│   │   ├── start_enhanced_mcp_server.py # Enhanced server startup
│   │   └── health_check.py       # Health monitoring
│   └── requirements.txt          # Enhanced dependencies
│
├── legacy/                       # Original codebase
│   ├── linkedin_browser_mcp.py   # Original MCP server
│   ├── api_bridge.py             # Original API bridge
│   ├── mcp_client.py             # Original MCP client
│   ├── database/                 # Original database
│   ├── src/                      # Original React frontend
│   ├── config.json               # Legacy configuration
│   └── requirements.txt          # Original dependencies
│
├── shared/                       # Shared resources
│   ├── database/                 # Shared database files
│   │   └── linkedin_jobs.db      # Main database
│   ├── sessions/                 # Shared session storage
│   ├── logs/                     # Shared log files
│   └── config/                   # Shared configuration
│
├── scripts/                      # Project-wide scripts
│   └── migrate_data.py           # Data migration script
│
├── docs/                         # Project documentation
│   ├── legacy/                   # Legacy documentation
│   ├── enhanced/                 # Enhanced documentation
│   └── migration/                # Migration guides
│
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

**NOTE:** This project uses a very specific set of dependencies. It is recommended to use a virtual environment. The dependencies in `legacy/requirements.txt` have been updated to work with Python 3.13, but some packages might still have issues on different OSes.

#### Enhanced Server
```bash
cd enhanced-mcp-server
pip install -r requirements.txt
```

#### Legacy Server & API Bridge
```bash
pip install -r legacy/requirements.txt
```

### 2. Run the Legacy System

The legacy system consists of two parts: the `linkedin_browser_mcp.py` server and the `api_bridge.py` server.

#### Start the MCP Server
```bash
cd legacy
python linkedin_browser_mcp.py
```

#### Start the API Bridge
In a separate terminal:
```bash
cd legacy
python api_bridge.py
```

### 3. Start Enhanced Server
```bash
cd enhanced-mcp-server
python scripts/start_enhanced_mcp_server.py
```

## 🔄 Migration

### Data Migration
If you have existing data, run the migration script:
```bash
python scripts/migrate_data.py
```

This will:
- Create a backup of your original files
- Move database to shared location
- Move sessions to shared location
- Move logs to shared location
- Validate the migration

### Gradual Migration Strategy
1. **Phase 1**: Run both systems simultaneously
2. **Phase 2**: Migrate tools from legacy to enhanced
3. **Phase 3**: Switch frontend to use enhanced server
4. **Phase 4**: Deprecate legacy server

## 📊 Benefits of This Structure

### 1. **Clear Separation**
- No conflicts between legacy and enhanced code
- Easy to maintain both systems
- Clear migration path

### 2. **Shared Resources**
- Database shared between both systems
- Sessions can be migrated between systems
- Logs centralized for monitoring

### 3. **Gradual Migration**
- Can run both systems simultaneously
- Easy to switch between systems
- No downtime during migration

### 4. **Production Ready**
- Docker support for both systems
- Clear deployment strategy
- Easy rollback if needed

## 🔧 Configuration

### Enhanced Server Configuration
Located at `enhanced-mcp-server/config/mcp_config.json`:
```json
{
  "database": {
    "url": "sqlite:///../../shared/database/linkedin_jobs.db"
  },
  "sessions": {
    "path": "../../shared/sessions"
  },
  "logging": {
    "file": "../../shared/logs/enhanced_mcp_server.log"
  }
}
```

### Legacy Server Configuration
Located at `legacy/config.json`:
```json
{
  "database": {
    "url": "sqlite:///../shared/database/linkedin_jobs.db"
  },
  "sessions": {
    "path": "../shared/sessions"
  }
}
```

## 🐳 Docker Support

### Enhanced Server
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY enhanced-mcp-server/ .
RUN pip install -r requirements.txt
RUN playwright install chromium
VOLUME ["/shared/database", "/shared/sessions", "/shared/logs"]
EXPOSE 8000
CMD ["python", "scripts/start_enhanced_mcp_server.py"]
```

### Legacy Server
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY legacy/ .
RUN pip install -r requirements.txt
RUN playwright install chromium
VOLUME ["/shared/database", "/shared/sessions"]
EXPOSE 8001
CMD ["python", "linkedin_browser_mcp.py"]
```

## 📈 Monitoring

### Health Checks
- Enhanced server: `enhanced-mcp-server/scripts/health_check.py`
- Checks directory structure, dependencies, configuration, and server status

### Logs
- Enhanced server: `shared/logs/enhanced_mcp_server.log`
- Legacy server: `shared/logs/legacy_mcp_server.log`

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   cd enhanced-mcp-server
   pip install -r requirements.txt
   ```

2. **Directory Structure Issues**
   ```bash
   python scripts/migrate_data.py
   ```

3. **Permission Issues**
   ```bash
   # On Windows
   icacls shared /grant Everyone:F /T
   
   # On Linux/Mac
   chmod -R 755 shared/
   ```

4. **Database Issues**
   ```bash
   # Check if database exists
   ls shared/database/linkedin_jobs.db
   
   # If not, run migration
   python scripts/migrate_data.py
   ```

## 📚 Documentation

- **Enhanced Server**: See `enhanced-mcp-server/` directory
- **Legacy Server**: See `legacy/` directory
- **Migration Guide**: See `docs/migration/`
- **API Documentation**: See `docs/enhanced/`

## 🤝 Contributing

1. **For Enhanced Server**: Work in `enhanced-mcp-server/`
2. **For Legacy Server**: Work in `legacy/`
3. **For Shared Resources**: Work in `shared/`
4. **For Documentation**: Work in `docs/`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Project Status**: Refactored with a functional legacy system and a foundational Enhanced MCP Server.
**Last Updated**: 2025-07-05
**Next Review**: 2025-07-12 