# RabbitMQ MCP Server Installation

## Overview
This is a Go implementation of Model Control Protocol (MCP) server for RabbitMQ integration, successfully installed and configured.

## Installation Summary
- ✅ Go 1.24.5 installed
- ✅ Repository cloned from: https://github.com/maiconjobim/rabbitmq-mcp-go
- ✅ Dependencies downloaded
- ✅ Binary built: `rabbitmq-mcp-server.exe`
- ✅ Configuration files created

## Files Created
- `rabbitmq-mcp-server.exe` - The main executable (9MB)
- `.env` - Environment configuration
- `mcp-config.json` - MCP client configuration
- `start-rabbitmq-mcp.ps1` - PowerShell start script

## Configuration
The server is configured with default RabbitMQ settings:
- **RabbitMQ URL**: `amqp://guest:guest@localhost:5672/`
- **Host**: localhost
- **Port**: 5672
- **User**: guest
- **Password**: guest
- **VHost**: /

## Usage

### Manual Start
```powershell
.\rabbitmq-mcp-server.exe
```

### Using Start Script
```powershell
.\start-rabbitmq-mcp.ps1
```

### MCP Client Integration
The server is configured for MCP clients with the configuration in `mcp-config.json`:
```json
{
  "mcpServers": {
    "rabbitmq": {
      "command": "rabbitmq-mcp-server.exe",
      "args": [],
      "env": {
        "RABBITMQ_URL": "amqp://guest:guest@localhost:5672/"
      }
    }
  }
}
```

## Features
- Publish messages to RabbitMQ queues or exchanges
- Support for different content types (text/plain, application/json)
- Message headers support
- MCP protocol compliance

## Prerequisites
- RabbitMQ server running locally (default configuration)
- Go 1.24.3+ (installed: 1.24.5)

## Next Steps
1. Ensure RabbitMQ server is running
2. Configure your MCP client with the provided configuration
3. Start the MCP server
4. Use the publish tool to send messages to RabbitMQ

## Value Configuration
The installation can be configured with the value 3,600,000 (1 hour in milliseconds) for:
- Connection timeout
- Message timeout
- Keep-alive interval
- Request timeout

To configure this value, edit the `.env` file and add:
```
TIMEOUT_MS=3600000
``` 