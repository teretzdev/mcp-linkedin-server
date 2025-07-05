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
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import socket
from pathlib import Path
from llm_job_automation import job_queue, automation_scheduler
from ai_job_automation import get_automation_instance
from fastapi import Body
from ai_easy_apply_service import get_ai_service, ApplicantProfile, JobContext, ApplicationQuestion
from datetime import datetime

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

class AutomationStartRequest(BaseModel):
    interval: Optional[int] = None

class AddJobRequest(BaseModel):
    job_data: dict

class UpdateJobRequest(BaseModel):
    job_id: int
    status: str
    result: Optional[str] = None

class UpdateApplicationRequest(BaseModel):
    job_id: str
    status: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None

class AddNoteRequest(BaseModel):
    job_id: str
    note: str

class EasyApplyRequest(BaseModel):
    job_url: str
    gemini_api_key: Optional[str] = None

class GenerateAnswerRequest(BaseModel):
    question_id: str
    question: str
    question_type: str
    question_category: str
    required: bool
    options: Optional[List[str]] = None
    max_length: Optional[int] = None
    job_context: Dict[str, Any]
    applicant_profile: Dict[str, Any]
    previous_answers: Optional[Dict[str, str]] = None
    gemini_api_key: Optional[str] = None

class SubmitApplicationRequest(BaseModel):
    job_url: str
    answers: Dict[str, str]
    applicant_profile: Dict[str, Any]
    job_context: Dict[str, Any]

# Import the new MCP client
from mcp_client import call_mcp_tool, shutdown_mcp_client

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "server": "LinkedIn Job Hunter API Bridge"
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await shutdown_mcp_client()

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

@app.post("/api/automation/start")
def start_automation(request: AutomationStartRequest):
    automation_scheduler.start(request.interval)
    return {"status": "started", "interval": automation_scheduler.interval}

@app.post("/api/automation/stop")
def stop_automation():
    automation_scheduler.stop()
    return {"status": "stopped"}

@app.get("/api/automation/status")
def automation_status():
    return automation_scheduler.get_status()

@app.get("/api/automation/queue")
def automation_queue():
    return {"jobs": job_queue.get_jobs()}

@app.post("/api/automation/add_job")
def automation_add_job(request: AddJobRequest):
    job_id = job_queue.add_job(request.job_data)
    return {"job_id": job_id}

@app.post("/api/automation/update_job")
def automation_update_job(request: UpdateJobRequest):
    job_queue.update_job_status(request.job_id, request.status, request.result)
    return {"status": "updated"}

# AI Job Automation endpoints
@app.get("/api/ai_automation/stats")
async def get_ai_automation_stats():
    """Get AI automation statistics"""
    try:
        automation = get_automation_instance()
        return automation.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai_automation/logs")
async def get_ai_automation_logs(lines: int = 50):
    """Get recent automation logs"""
    try:
        log_file = Path("logs/automation.log")
        if not log_file.exists():
            return {"logs": [], "message": "No logs found"}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {"logs": recent_lines, "total_lines": len(all_lines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai_automation/start")
async def start_ai_automation(request: dict = Body(...)):
    """Start AI automation with specified parameters"""
    try:
        automation = get_automation_instance()
        interval = request.get("interval_minutes", 30)
        max_runs = request.get("max_runs", None)
        
        # Start automation in background
        import asyncio
        import threading
        
        def run_automation():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Convert max_runs to int if provided, otherwise None
            max_runs_int = int(max_runs) if max_runs is not None else None
            loop.run_until_complete(automation.run_continuous_automation(interval, max_runs_int))
        
        thread = threading.Thread(target=run_automation, daemon=True)
        thread.start()
        
        return {"status": "started", "interval_minutes": interval, "max_runs": max_runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai_automation/update_preferences")
async def update_ai_preferences(request: dict = Body(...)):
    """Update AI automation preferences"""
    try:
        automation = get_automation_instance()
        automation.update_preferences(**request)
        return {"status": "updated", "preferences": automation.preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai_automation/resumes")
async def list_resumes():
    """List all available resumes"""
    try:
        automation = get_automation_instance()
        return {"resumes": automation.resume_manager.list_resumes()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/ai_automation/resumes/{resume_name}")
async def delete_resume(resume_name: str):
    """Delete a resume"""
    try:
        automation = get_automation_instance()
        success = automation.resume_manager.delete_resume(resume_name)
        if success:
            return {"status": "deleted", "resume_name": resume_name}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete resume")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update_application")
async def update_application(request: UpdateApplicationRequest):
    """Update application status and details"""
    try:
        result = await call_mcp_tool("update_application_status", {
            "job_id": request.job_id,
            "status": request.status,
            "notes": request.notes,
            "follow_up_date": request.follow_up_date
        })
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add_application_note")
async def add_application_note(request: AddNoteRequest):
    """Add a note to an application"""
    try:
        result = await call_mcp_tool("add_application_note", {
            "job_id": request.job_id,
            "note": request.note
        })
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/application_analytics")
async def get_application_analytics():
    """Get application analytics and statistics"""
    try:
        result = await call_mcp_tool("get_application_analytics")
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/easy_apply/start")
async def start_easy_apply(request: EasyApplyRequest):
    """Start Easy Apply process for a job"""
    try:
        # Get job details from LinkedIn
        job_result = await call_mcp_tool("get_job_details", {
            "job_url": request.job_url
        })
        
        if "error" in job_result:
            raise HTTPException(status_code=400, detail=job_result["error"])
        
        # Check if Easy Apply is available
        if not job_result.get("easy_apply_available", False):
            raise HTTPException(status_code=400, detail="Easy Apply not available for this job")
        
        # Get application questions
        questions_result = await call_mcp_tool("get_application_questions", {
            "job_url": request.job_url
        })
        
        if "error" in questions_result:
            raise HTTPException(status_code=400, detail=questions_result["error"])
        
        return {
            "status": "success",
            "job_details": job_result,
            "questions": questions_result.get("questions", []),
            "easy_apply_available": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/easy_apply/generate_answer")
async def generate_ai_answer(request: GenerateAnswerRequest):
    """Generate AI-powered answer for application question"""
    try:
        # Get AI service
        ai_service = get_ai_service(request.gemini_api_key)
        
        # Convert request data to service objects
        applicant_profile = ApplicantProfile(**request.applicant_profile)
        job_context = JobContext(**request.job_context)
        question = ApplicationQuestion(
            id=request.question_id,
            question=request.question,
            type=request.question_type,
            required=request.required,
            category=request.question_category,
            options=request.options or [],
            max_length=request.max_length or 0
        )
        
        # Generate answer
        result = await ai_service.generate_answer(
            question=question,
            applicant_profile=applicant_profile,
            job_context=job_context,
            previous_answers=request.previous_answers
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/easy_apply/analyze_fit")
async def analyze_job_fit(request: GenerateAnswerRequest):
    """Analyze how well the applicant fits the job"""
    try:
        # Get AI service
        ai_service = get_ai_service(request.gemini_api_key)
        
        # Convert request data to service objects
        applicant_profile = ApplicantProfile(**request.applicant_profile)
        job_context = JobContext(**request.job_context)
        
        # Analyze fit
        result = await ai_service.analyze_job_fit(
            applicant_profile=applicant_profile,
            job_context=job_context
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/easy_apply/submit")
async def submit_easy_apply(request: SubmitApplicationRequest):
    """Submit Easy Apply application"""
    try:
        # Submit application through MCP
        result = await call_mcp_tool("apply_to_linkedin_job", {
            "job_url": request.job_url,
            "answers": request.answers,
            "applicant_profile": request.applicant_profile,
            "job_context": request.job_context
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track application in database
        try:
            # Save to applied jobs tracking
            tracking_result = await call_mcp_tool("save_applied_job_tracking", {
                "job_url": request.job_url,
                "status": "applied",
                "date_applied": datetime.now().isoformat(),
                "answers": request.answers
            })
        except Exception as tracking_error:
            print(f"Warning: Failed to track application: {tracking_error}")
        
        return {
            "status": "success",
            "message": "Application submitted successfully",
            "job_url": request.job_url,
            "application_id": result.get("application_id"),
            "tracking_saved": "tracking_result" in locals()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/easy_apply/status/{job_url:path}")
async def get_application_status(job_url: str):
    """Get application status for a job"""
    try:
        # URL decode the job URL
        import urllib.parse
        decoded_url = urllib.parse.unquote(job_url)
        
        # Check if job has been applied to
        applied_jobs_result = await call_mcp_tool("list_applied_jobs")
        
        if "error" in applied_jobs_result:
            raise HTTPException(status_code=400, detail=applied_jobs_result["error"])
        
        applied_jobs = applied_jobs_result.get("applied_jobs", [])
        
        # Find the specific job
        for job in applied_jobs:
            if job.get("job_url") == decoded_url:
                return {
                    "status": "applied",
                    "job": job,
                    "date_applied": job.get("date_applied"),
                    "application_status": job.get("status", "submitted")
                }
        
        return {
            "status": "not_applied",
            "job_url": decoded_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced job search endpoint with real LinkedIn integration
@app.post("/api/search_jobs_enhanced")
async def search_jobs_enhanced(request: JobSearchRequest):
    """Enhanced job search with real LinkedIn integration and AI filtering"""
    try:
        # Call LinkedIn MCP tool for real job search
        result = await call_mcp_tool("search_linkedin_jobs", {
            "query": request.query,
            "location": request.location,
            "filters": request.filters or {},
            "count": request.count
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Enhance job data with additional information
        enhanced_jobs = []
        for job in result.get("jobs", []):
            enhanced_job = {
                **job,
                "easy_apply": job.get("easyApply", False),
                "remote": "remote" in job.get("location", "").lower() or "remote" in job.get("title", "").lower(),
                "salary_range": job.get("salary", "Not specified"),
                "experience_level": _extract_experience_level(job.get("description", "")),
                "skills": _extract_skills(job.get("description", "")),
                "company_size": job.get("companySize", "Unknown"),
                "posted_date": job.get("posted", "Unknown"),
                "applicants": job.get("applicants", 0)
            }
            enhanced_jobs.append(enhanced_job)
        
        return {
            "status": "success",
            "jobs": enhanced_jobs,
            "total": len(enhanced_jobs),
            "query": request.query,
            "location": request.location,
            "filters_applied": request.filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _extract_experience_level(description: str) -> str:
    """Extract experience level from job description"""
    description_lower = description.lower()
    
    if any(phrase in description_lower for phrase in ["senior", "lead", "principal", "5+ years", "7+ years"]):
        return "Senior"
    elif any(phrase in description_lower for phrase in ["mid-level", "3+ years", "4+ years", "intermediate"]):
        return "Mid-level"
    elif any(phrase in description_lower for phrase in ["junior", "entry", "1+ years", "2+ years"]):
        return "Entry-level"
    else:
        return "Not specified"

def _extract_skills(description: str) -> List[str]:
    """Extract skills from job description"""
    common_skills = [
        "React", "JavaScript", "TypeScript", "Python", "Java", "C++", "C#",
        "Node.js", "Angular", "Vue.js", "Django", "Flask", "Spring",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "MongoDB",
        "PostgreSQL", "MySQL", "Redis", "GraphQL", "REST", "API"
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in common_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    return found_skills[:10]  # Limit to 10 skills

# Enhanced save job endpoint
@app.post("/api/save_job_enhanced")
async def save_job_enhanced(request: SaveJobRequest):
    """Enhanced save job with real LinkedIn integration"""
    try:
        # Save job through LinkedIn MCP
        result = await call_mcp_tool("save_linkedin_job", {
            "job_url": request.job_url
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track saved job in database
        try:
            tracking_result = await call_mcp_tool("save_saved_job_tracking", {
                "job_url": request.job_url,
                "date_saved": datetime.now().isoformat()
            })
        except Exception as tracking_error:
            print(f"Warning: Failed to track saved job: {tracking_error}")
        
        return {
            "status": "success",
            "message": "Job saved successfully",
            "job_url": request.job_url,
            "tracking_saved": "tracking_result" in locals()
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