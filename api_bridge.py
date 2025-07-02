#!/usr/bin/env python3
"""
API Bridge for LinkedIn MCP Server
Provides HTTP endpoints for the React frontend to communicate with the MCP server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import subprocess
import sys
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import socket

app = FastAPI(title="LinkedIn Job Hunter API Bridge", version="2.0.0")

# Load environment variables
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = ''
    filters: Optional[dict] = None
    count: int = 10

class ApplyJobRequest(BaseModel):
    job_url: str
    resume_path: Optional[str] = ''
    cover_letter_path: Optional[str] = ''

class SaveJobRequest(BaseModel):
    job_url: str

class CredentialRequest(BaseModel):
    username: str
    password: str

# MCP Server communication
async def call_mcp_tool(tool_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call an MCP tool via the LinkedIn MCP server"""
    try:
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "linkedin_browser_mcp.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the MCP server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "LinkedIn Job Hunter API Bridge",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialization request
        stdin_data = json.dumps(init_request) + "\n"
        stdout, stderr = await process.communicate(input=stdin_data.encode())
        
        # Start a new process for the tool call (since the first one exits after init)
        process2 = await asyncio.create_subprocess_exec(
            sys.executable, "linkedin_browser_mcp.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send initialization + notification + tool call in sequence
        init_request2 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "LinkedIn Job Hunter API Bridge",
                    "version": "1.0.0"
                }
            }
        }
        
        notify_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
        
        # Send all requests in sequence
        stdin_data = json.dumps(init_request2) + "\n" + json.dumps(notify_request) + "\n" + json.dumps(tool_request) + "\n"
        stdout, stderr = await process2.communicate(input=stdin_data.encode())
        
        if process2.returncode != 0:
            return {"error": f"MCP server error: {stderr.decode()}"}
        
        # Parse the response - look for the tool call response
        lines = stdout.decode().strip().split('\n')
        for line in lines:
            if line.strip():
                try:
                    response = json.loads(line.strip())
                    if "id" in response and response["id"] == 2:  # Tool call response
                        if "result" in response:
                            return response["result"]
                        elif "error" in response:
                            return {"error": response["error"]["message"]}
                except json.JSONDecodeError:
                    continue
        
        return {"error": "No valid tool response found"}
            
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "server": "LinkedIn Job Hunter API Bridge"
    }

@app.post("/api/search_jobs")
async def search_jobs(request: JobSearchRequest):
    """Search for LinkedIn jobs"""
    try:
        result = await call_mcp_tool("search_linkedin_jobs", {
            "query": request.query,
            "location": request.location,
            "filters": request.filters or {},
            "count": request.count
        })
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/apply_job")
async def apply_job(request: ApplyJobRequest):
    """Apply to a LinkedIn job"""
    try:
        result = await call_mcp_tool("apply_to_linkedin_job", {
            "job_url": request.job_url,
            "resume_path": request.resume_path,
            "cover_letter_path": request.cover_letter_path
        })
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save_job")
async def save_job(request: SaveJobRequest):
    """Save a LinkedIn job"""
    try:
        result = await call_mcp_tool("save_linkedin_job", {
            "job_url": request.job_url
        })
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/list_applied_jobs")
async def list_applied_jobs():
    """List applied jobs"""
    try:
        result = await call_mcp_tool("list_applied_jobs")
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job_recommendations")
async def job_recommendations():
    """Get job recommendations"""
    try:
        result = await call_mcp_tool("get_job_recommendations")
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/list_saved_jobs")
async def list_saved_jobs():
    """List saved jobs"""
    try:
        result = await call_mcp_tool("list_saved_jobs")
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_credentials")
async def get_credentials():
    """Get current LinkedIn credentials (username only, password masked)"""
    import os
    from dotenv import load_dotenv
    import pathlib
    try:
        cwd = os.getcwd()
        env_path = os.path.abspath('.env')
        print(f"[DEBUG] Current working directory: {cwd}")
        print(f"[DEBUG] Looking for .env at: {env_path}")
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_contents = f.read()
            print(f"[DEBUG] .env contents:\n{env_contents}")
        else:
            print("[DEBUG] .env file does NOT exist!")
        load_dotenv(dotenv_path=env_path, override=True)
        username = os.getenv('LINKEDIN_USERNAME', '')
        password = os.getenv('LINKEDIN_PASSWORD', '')
        print(f"[DEBUG] Loaded credentials: username='{username}', password length={len(password)}")
        return {
            "username": username,
            "configured": bool(username)
        }
    except Exception as e:
        print(f"[DEBUG] Exception in get_credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update_credentials")
async def update_credentials(request: CredentialRequest):
    """Update LinkedIn credentials in .env file"""
    try:
        # Read existing .env file or create new one
        env_path = '.env'
        env_lines = []
        
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_lines = f.readlines()
            except UnicodeDecodeError:
                # If UTF-8 fails, try with a different encoding
                with open(env_path, 'r', encoding='latin-1') as f:
                    env_lines = f.readlines()
        else:
            # Create new .env file with basic structure
            env_lines = [
                "# LinkedIn Credentials\n",
                "LINKEDIN_USERNAME=\n",
                "LINKEDIN_PASSWORD=\n",
                "\n",
                "# OpenAI API Key (for LLM features)\n",
                "OPENAI_API_KEY=\n",
                "\n",
                "# Other Configuration\n",
                "DEBUG=true\n"
            ]
        
        # Update or add credentials
        username_updated = False
        password_updated = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('LINKEDIN_USERNAME='):
                env_lines[i] = f'LINKEDIN_USERNAME={request.username}\n'
                username_updated = True
            elif line.startswith('LINKEDIN_PASSWORD='):
                env_lines[i] = f'LINKEDIN_PASSWORD={request.password}\n'
                password_updated = True
        
        # Add if not found
        if not username_updated:
            env_lines.append(f'LINKEDIN_USERNAME={request.username}\n')
        if not password_updated:
            env_lines.append(f'LINKEDIN_PASSWORD={request.password}\n')
        
        # Write back to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        
        # Reload environment variables
        load_dotenv(override=True)
        
        # Verify the credentials were saved
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if request.username in content and request.password in content:
                    return {
                        "status": "success",
                        "message": "Credentials updated successfully",
                        "username": request.username,
                        "configured": True
                    }
                else:
                    raise HTTPException(status_code=500, detail="Credentials were not properly saved")
        else:
            raise HTTPException(status_code=500, detail="Failed to create .env file")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update credentials: {str(e)}")

@app.post("/api/test_login")
async def test_login():
    """Test LinkedIn login with current credentials"""
    try:
        # First check if credentials are configured
        username = os.getenv('LINKEDIN_USERNAME', '')
        password = os.getenv('LINKEDIN_PASSWORD', '')
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="LinkedIn credentials not configured. Please update credentials first.")
        
        result = await call_mcp_tool("login_linkedin_secure")
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {
            "status": "success",
            "message": "Login test successful",
            "username": username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def find_available_port(start_port=8001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == "__main__":
    import uvicorn
    import socket
    import subprocess
    import os
    start_port = 8001
    max_port = 8010
    
    def kill_process_on_port(port):
        """Kill any process using the specified port"""
        try:
            # Find process using the port
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                         capture_output=True, check=True)
                            print(f"Killed process {pid} on port {port}")
                        except subprocess.CalledProcessError:
                            pass  # Process might already be dead
        except Exception as e:
            print(f"Warning: Could not kill process on port {port}: {e}")
    
    def is_port_in_use(port):
        """Check if a port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    for port in range(start_port, max_port + 1):
        if is_port_in_use(port):
            print(f"Port {port} is in use, attempting to kill conflicting process...")
            kill_process_on_port(port)
            # Wait a moment for the process to be killed
            import time
            time.sleep(1)
            
        if is_port_in_use(port):
            print(f"Port {port} still in use, trying next port...")
            continue
            
        try:
            print(f"Starting API Bridge on port {port}")
            with open("api_bridge_port.txt", "w") as f:
                f.write(str(port))
            uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
            break
        except Exception as e:
            print(f"Failed to start on port {port}: {e}")
            continue
    else:
        print(f"No available ports between {start_port} and {max_port}.")
        sys.exit(1) 