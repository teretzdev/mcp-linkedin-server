# LinkedIn Job Hunter - Refactoring Plan for Enhanced MCP Server

## 🎯 Overview

This plan outlines how to refactor the codebase to create a clean separation between the existing LinkedIn Job Hunter and the new enhanced MCP server, avoiding conflicts and maintaining both systems.

## 🏗️ Proposed Filesystem Structure

### Option 1: Separate Project Structure (Recommended)
```
linkedin-job-hunter/                    # Main project directory
├── legacy/                            # Existing codebase
│   ├── linkedin_browser_mcp.py        # Original MCP server
│   ├── api_bridge.py                  # Original API bridge
│   ├── mcp_client.py                  # Original MCP client
│   ├── database/                      # Original database
│   ├── src/                           # Original React frontend
│   ├── requirements.txt               # Original dependencies
│   └── ...                            # All other existing files
│
├── enhanced-mcp-server/               # New enhanced MCP server
│   ├── mcp_server/                    # Enhanced MCP server core
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── server.py
│   │   │   ├── browser_manager.py
│   │   │   ├── auth_manager.py
│   │   │   └── error_handler.py
│   │   ├── tools/
│   │   ├── models/
│   │   ├── database/
│   │   └── utils/
│   ├── config/
│   ├── tests/
│   ├── scripts/
│   ├── docs/
│   ├── requirements.txt
│   └── README.md
│
├── shared/                            # Shared resources
│   ├── database/                      # Shared database files
│   ├── sessions/                      # Shared session storage
│   ├── logs/                          # Shared log files
│   └── config/                        # Shared configuration
│
├── docker/                            # Docker configurations
│   ├── legacy/
│   ├── enhanced/
│   └── docker-compose.yml
│
├── scripts/                           # Project-wide scripts
│   ├── start_legacy.bat
│   ├── start_enhanced.bat
│   ├── migrate_data.py
│   └── health_check.py
│
├── docs/                              # Project documentation
│   ├── legacy/
│   ├── enhanced/
│   └── migration/
│
└── README.md                          # Main project README
```

### Option 2: Monorepo with Clear Separation
```
linkedin-job-hunter/
├── packages/
│   ├── legacy-server/                 # Existing MCP server
│   │   ├── linkedin_browser_mcp.py
│   │   ├── api_bridge.py
│   │   ├── mcp_client.py
│   │   └── requirements.txt
│   │
│   ├── enhanced-server/               # Enhanced MCP server
│   │   ├── mcp_server/
│   │   ├── config/
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   ├── frontend/                      # React frontend
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   │
│   └── shared/                        # Shared utilities
│       ├── database/
│       ├── utils/
│       └── config/
│
├── infrastructure/
│   ├── docker/
│   ├── scripts/
│   └── docs/
│
└── README.md
```

## 🔄 Refactoring Strategy

### Phase 1: Create New Structure (Week 1)

#### 1.1 Create Enhanced Server Directory
```bash
# Create new enhanced server structure
mkdir enhanced-mcp-server
cd enhanced-mcp-server

# Move existing enhanced files
mv ../mcp_server ./
mv ../config ./
mv ../scripts ./
mv ../tests ./
mv ../docs ./
mv ../requirements_enhanced.txt ./requirements.txt
```

#### 1.2 Create Legacy Directory
```bash
# Create legacy directory and move existing files
mkdir ../legacy
cd ../legacy

# Move existing files (excluding enhanced ones)
mv ../linkedin_browser_mcp.py ./
mv ../api_bridge.py ./
mv ../mcp_client.py ./
mv ../database ./
mv ../src ./
mv ../requirements.txt ./
# ... move other existing files
```

#### 1.3 Create Shared Resources
```bash
# Create shared directories
mkdir ../shared
mkdir ../shared/database
mkdir ../shared/sessions
mkdir ../shared/logs
mkdir ../shared/config

# Move shared files
mv ../linkedin_jobs.db ../shared/database/
mv ../sessions/* ../shared/sessions/
mv ../logs/* ../shared/logs/
```

### Phase 2: Update Configuration (Week 1)

#### 2.1 Enhanced Server Configuration
```json
// enhanced-mcp-server/config/mcp_config.json
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

#### 2.2 Legacy Server Configuration
```json
// legacy/config.json
{
  "database": {
    "url": "sqlite:///../shared/database/linkedin_jobs.db"
  },
  "sessions": {
    "path": "../shared/sessions"
  }
}
```

### Phase 3: Update Scripts (Week 1)

#### 3.1 Enhanced Server Startup
```python
# enhanced-mcp-server/scripts/start_server.py
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the enhanced server to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set shared paths
os.environ['SHARED_DATABASE_PATH'] = str(project_root.parent / 'shared' / 'database')
os.environ['SHARED_SESSIONS_PATH'] = str(project_root.parent / 'shared' / 'sessions')
os.environ['SHARED_LOGS_PATH'] = str(project_root.parent / 'shared' / 'logs')

from mcp_server.core.server import initialize_server, cleanup_server
# ... rest of startup logic
```

#### 3.2 Legacy Server Startup
```python
# legacy/scripts/start_server.py
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the legacy server to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set shared paths
os.environ['SHARED_DATABASE_PATH'] = str(project_root.parent / 'shared' / 'database')
os.environ['SHARED_SESSIONS_PATH'] = str(project_root.parent / 'shared' / 'sessions')

# ... legacy startup logic
```

### Phase 4: Docker Configuration (Week 2)

#### 4.1 Enhanced Server Dockerfile
```dockerfile
# enhanced-mcp-server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy enhanced server code
COPY mcp_server/ ./mcp_server/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
RUN playwright install chromium

# Create shared volume mounts
VOLUME ["/shared/database", "/shared/sessions", "/shared/logs"]

# Set environment variables
ENV SHARED_DATABASE_PATH=/shared/database
ENV SHARED_SESSIONS_PATH=/shared/sessions
ENV SHARED_LOGS_PATH=/shared/logs

EXPOSE 8000
CMD ["python", "scripts/start_server.py"]
```

#### 4.2 Legacy Server Dockerfile
```dockerfile
# legacy/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy legacy server code
COPY linkedin_browser_mcp.py ./
COPY api_bridge.py ./
COPY mcp_client.py ./
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
RUN playwright install chromium

# Create shared volume mounts
VOLUME ["/shared/database", "/shared/sessions"]

# Set environment variables
ENV SHARED_DATABASE_PATH=/shared/database
ENV SHARED_SESSIONS_PATH=/shared/sessions

EXPOSE 8001
CMD ["python", "linkedin_browser_mcp.py"]
```

#### 4.3 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  legacy-server:
    build: ./legacy
    ports:
      - "8001:8001"
    volumes:
      - ./shared/database:/shared/database
      - ./shared/sessions:/shared/sessions
    environment:
      - DATABASE_URL=sqlite:///shared/database/linkedin_jobs.db
    restart: unless-stopped

  enhanced-server:
    build: ./enhanced-mcp-server
    ports:
      - "8000:8000"
    volumes:
      - ./shared/database:/shared/database
      - ./shared/sessions:/shared/sessions
      - ./shared/logs:/shared/logs
    environment:
      - DATABASE_URL=sqlite:///shared/database/linkedin_jobs.db
    restart: unless-stopped
    depends_on:
      - legacy-server

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    restart: unless-stopped

volumes:
  shared_database:
  shared_sessions:
  shared_logs:
```

## 🚀 Migration Scripts

### Data Migration Script
```python
# scripts/migrate_data.py
#!/usr/bin/env python3
"""
Data migration script to move data between legacy and enhanced systems
"""

import sqlite3
import json
import shutil
from pathlib import Path

def migrate_database():
    """Migrate database from legacy to enhanced format"""
    legacy_db = Path("legacy/linkedin_jobs.db")
    enhanced_db = Path("shared/database/linkedin_jobs.db")
    
    if legacy_db.exists():
        shutil.copy2(legacy_db, enhanced_db)
        print("Database migrated successfully")

def migrate_sessions():
    """Migrate session data"""
    legacy_sessions = Path("legacy/sessions")
    shared_sessions = Path("shared/sessions")
    
    if legacy_sessions.exists():
        shutil.copytree(legacy_sessions, shared_sessions, dirs_exist_ok=True)
        print("Sessions migrated successfully")

def main():
    print("Starting data migration...")
    migrate_database()
    migrate_sessions()
    print("Migration completed!")

if __name__ == "__main__":
    main()
```

## 📋 Implementation Steps

### Step 1: Create New Structure
```bash
# Create new directory structure
mkdir enhanced-mcp-server legacy shared docker scripts docs

# Move existing enhanced files
mv mcp_server enhanced-mcp-server/
mv config enhanced-mcp-server/
mv scripts enhanced-mcp-server/
mv requirements_enhanced.txt enhanced-mcp-server/requirements.txt

# Move existing legacy files
mv linkedin_browser_mcp.py legacy/
mv api_bridge.py legacy/
mv mcp_client.py legacy/
mv database legacy/
mv src legacy/
mv requirements.txt legacy/
```

### Step 2: Update Paths
```bash
# Update all file paths in enhanced server
find enhanced-mcp-server -name "*.py" -exec sed -i 's|\.\./|../../shared/|g' {} \;

# Update all file paths in legacy server
find legacy -name "*.py" -exec sed -i 's|\./|../shared/|g' {} \;
```

### Step 3: Test Both Systems
```bash
# Test legacy server
cd legacy
python linkedin_browser_mcp.py

# Test enhanced server
cd ../enhanced-mcp-server
python scripts/start_server.py
```

## 🎯 Benefits of This Approach

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

## 🔧 Next Steps

1. **Choose the structure** (Option 1 or 2)
2. **Create the new directory structure**
3. **Move files to appropriate locations**
4. **Update all file paths and configurations**
5. **Test both systems independently**
6. **Set up Docker configuration**
7. **Create migration scripts**
8. **Document the new structure**

Would you like me to proceed with implementing this refactoring plan? I can start by creating the new directory structure and moving the files accordingly. 