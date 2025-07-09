# AI Job Automation System
import asyncio
import json
import logging
import time
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass, asdict, field
from pathlib import Path
import psutil
import requests
import centralized_logging
from logging.handlers import RotatingFileHandler
import sys
from shared.linkedin_login import robust_linkedin_login_selenium
import importlib.util

print("[DEBUG] ai_job_automation.py script started.")
logging.basicConfig(level=logging.INFO)
logging.info("[DEBUG] ai_job_automation.py script started (logger).")

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import aioredis_queue for async job queueing
aioredis_queue_spec = importlib.util.find_spec('services.aioredis_queue')
if aioredis_queue_spec is not None:
    aioredis_queue = importlib.util.module_from_spec(aioredis_queue_spec)
    aioredis_queue_spec.loader.exec_module(aioredis_queue)
else:
    aioredis_queue = None

# Configure central logging
def setup_logging():
    """Setup central logging to both file and console"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler(log_dir / "automation.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

central_logger = centralized_logging.get_logger("ai_job_automation")

# Setup Gemini
def setup_gemini():
    """Setup Gemini API"""
    if not GEMINI_AVAILABLE:
        central_logger.log_warning("Gemini not available. Install with: pip install google-generativeai")
        return None
        
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        genai.configure(api_key=gemini_key)
        return genai.GenerativeModel('gemini-pro')
    else:
        central_logger.log_warning("GEMINI_API_KEY not found. Gemini matching will be disabled.")
        return None

@dataclass
class JobPreferences:
    """User job preferences for matching"""
    keywords: List[str] = field(default_factory=list)
    location: str = "Remote"
    experience_level: str = "mid-level"
    job_type: str = "full-time"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_preference: bool = True
    companies_to_avoid: List[str] = field(default_factory=list)
    companies_to_target: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    skills_preferred: List[str] = field(default_factory=list)
    selected_resume: str = "resume1.pdf"

@dataclass
class JobMatch:
    """Job with matching score"""
    job_data: Dict[str, Any]
    match_score: float
    match_reasons: List[str]
    should_apply: bool
    gemini_analysis: Optional[str] = None

class ResumeManager:
    """Manages resume storage and selection"""
    
    def __init__(self):
        self.resume_dir = Path("resumes")
        self.resume_dir.mkdir(exist_ok=True)
        self.max_resumes = 3
    
    def upload_resume(self, file_path: str, resume_name: str) -> bool:
        """Upload a resume file"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                central_logger.log_error(f"Resume file not found: {file_path}")
                return False
            
            existing_resumes = self.list_resumes()
            if len(existing_resumes) >= self.max_resumes:
                central_logger.log_warning(f"Maximum {self.max_resumes} resumes reached. Delete one first.")
                return False
            
            dest_path = self.resume_dir / f"{resume_name}.pdf"
            shutil.copy2(source_path, dest_path)
            central_logger.log_info(f"Resume uploaded: {resume_name}")
            return True
            
        except Exception as e:
            central_logger.log_error(f"Failed to upload resume: {e}")
            return False
    
    def list_resumes(self) -> List[Dict]:
        """List all available resumes"""
        resumes = []
        for file_path in self.resume_dir.glob("*.pdf"):
            resumes.append({
                "name": file_path.stem,
                "filename": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "uploaded": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        return resumes
    
    def delete_resume(self, resume_name: str) -> bool:
        """Delete a resume"""
        try:
            resume_path = self.resume_dir / f"{resume_name}.pdf"
            if resume_path.exists():
                resume_path.unlink()
                central_logger.log_info(f"Resume deleted: {resume_name}")
                return True
            else:
                central_logger.log_error(f"Resume not found: {resume_name}")
                return False
        except Exception as e:
            central_logger.log_error(f"Failed to delete resume: {e}")
            return False
    
    def get_resume_path(self, resume_name: str) -> str:
        """Get the full path of a resume"""
        if not resume_name:
            return ""
        for file_path in self.resume_dir.glob("*"):
            if file_path.stem == Path(resume_name).stem:
                return str(file_path)
        return ""

class AIJobAutomation:
    """AI-powered job automation system with a two-phase process."""
    
    def __init__(self, api_base_url: str | None = None):
        # Load port configuration from service_ports.json
        import json
        import os
        
        try:
            with open('service_ports.json', 'r') as f:
                ports = json.load(f)
            api_port = ports.get('api_bridge', 8001)
            job_mgmt_port = ports.get('job_management_api', 8006)
        except:
            # Fallback to default ports
            api_port = 8001
            job_mgmt_port = 8006
            
        self.api_base_url = api_base_url or f"http://localhost:{api_port}"
        self.job_management_api_base_url = f"http://localhost:{job_mgmt_port}"
        self.preferences = self._load_preferences()
        self.resume_manager = ResumeManager()
        self.gemini_model = setup_gemini()
        
        self.automation_stats = {
            "jobs_searched": 0,
            "new_jobs_added": 0,
            "jobs_applied": 0,
            "last_run": None,
            "total_runtime": 0,
            "cycles_completed": 0,
            "errors": 0
        }
        
    async def wait_for_api(self, timeout: int = 60):
        """Waits for the backend API to be available."""
        central_logger.log_info(f"Waiting for API to be available at {self.api_base_url}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_base_url}/api/health") as response:
                        if response.status == 200:
                            central_logger.log_info("API is available.")
                            return True
            except aiohttp.ClientConnectorError:
                pass
            await asyncio.sleep(2)
        central_logger.log_error("API did not become available in time.")
        return False

    def _load_preferences(self) -> JobPreferences:
        """Load user preferences from file"""
        try:
            if os.path.exists('job_preferences.json'):
                with open('job_preferences.json', 'r') as f:
                    data = json.load(f)
                    allowed_fields = set(JobPreferences.__dataclass_fields__.keys())
                    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                    for key in ['keywords', 'companies_to_avoid', 'companies_to_target', 'skills_required', 'skills_preferred']:
                        if key in filtered_data and filtered_data[key] is None:
                            filtered_data[key] = []
                    return JobPreferences(**filtered_data)
        except Exception as e:
            central_logger.log_error(f"Failed to load preferences: {e}")
        return JobPreferences()
    
    def _save_preferences(self):
        """Save user preferences to file"""
        try:
            with open('job_preferences.json', 'w') as f:
                json.dump(asdict(self.preferences), f, indent=2)
        except Exception as e:
            central_logger.log_error(f"Failed to save preferences: {e}")
    
    def update_preferences(self, **kwargs):
        self.preferences = self._load_preferences()
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self._save_preferences()

    async def run_recon_phase(self, query: str = "", location: str = "", count: int = 50):
        """Phase 1: Search for jobs and populate the database."""
        central_logger.log_info("--- Starting Phase 1: Reconnaissance ---")
        
        if not await self.wait_for_api():
            return

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/api/search_jobs_internal"
                payload = {"query": query, "location": location, "count": count}
                async with session.post(url, json=payload, timeout=300) as response:
                    response_text = await response.text()
                    central_logger.log_info(f"API Response Status: {response.status}")
                    central_logger.log_info(f"API Response (first 500 chars): {response_text[:500]}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            added_count = result.get("jobs_added_to_db", 0)
                            total_found = result.get('total', 0)
                            self.automation_stats['jobs_searched'] += total_found
                            self.automation_stats['new_jobs_added'] += added_count
                            central_logger.log_info(f"Recon complete. Found: {total_found}. New jobs in DB: {added_count}")
                        except Exception as json_error:
                            central_logger.log_error(f"Failed to parse JSON response: {json_error}")
                            central_logger.log_error(f"Raw response: {response_text}")
                            self.automation_stats['errors'] += 1
                    else:
                        central_logger.log_error(f"Recon failed. API status {response.status}: {response_text}")
                        self.automation_stats['errors'] += 1
        except Exception as e:
            central_logger.log_error(f"An error occurred during recon phase: {type(e).__name__}: {str(e)}")
            central_logger.log_error(f"Full traceback:", exc_info=True)
            self.automation_stats['errors'] += 1
        central_logger.log_info("--- Reconnaissance Phase Completed Successfully ---")

    def get_stats(self) -> Dict:
        """Get automation statistics"""
        self.automation_stats["last_run"] = datetime.now().isoformat()
        return self.automation_stats

def get_automation_instance() -> AIJobAutomation:
    """Get an instance of the automation system"""
    # This might be expanded to handle different API URLs
    return AIJobAutomation()

async def enqueue_scrape_job(query, location, count):
    if aioredis_queue is None:
        print("[ERROR] aioredis_queue.py not found. Cannot enqueue job.")
        return
    redis = await aioredis_queue.get_redis()
    await aioredis_queue.enqueue_job(redis, 'scrape', {'query': query, 'location': location, 'count': count})
    print(f"[ENQUEUED] Scrape job: {query}, {location}, {count}")

async def start_aioredis_worker():
    if aioredis_queue is None:
        print("[ERROR] aioredis_queue.py not found. Cannot start worker.")
        return
    redis = await aioredis_queue.get_redis()
    handlers = {
        'scrape': aioredis_queue.handle_scrape_job,
        'apply': aioredis_queue.handle_apply_job
    }
    await aioredis_queue.worker_loop(redis, handlers)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Job Automation controlled by command-line arguments.")
    parser.add_argument('phase', nargs='?', choices=['start_recon', 'enqueue_scrape', 'start_worker'], default='start_recon',
                        help="Specify the phase to run: 'start_recon', 'enqueue_scrape', or 'start_worker'.")
    parser.add_argument('--query', default='Software Engineer', help='Job search query')
    parser.add_argument('--location', default='Remote', help='Job location')
    parser.add_argument('--count', type=int, default=10, help='Number of jobs to search')
    args = parser.parse_args()

    if args.phase == 'enqueue_scrape':
        asyncio.run(enqueue_scrape_job(args.query, args.location, args.count))
    elif args.phase == 'start_worker':
        asyncio.run(start_aioredis_worker())
    else:
        asyncio.run(main_async(args))

def main_async(args):
    # Existing main logic for direct recon
    automation = get_automation_instance()
    if args.phase == 'start_recon':
        central_logger.log_info("--- Starting AI Job Automation (Recon Phase) ---")
        search_query = args.query
        search_location = args.location
        asyncio.run(automation.run_recon_phase(query=search_query, location=search_location, count=args.count))
    central_logger.log_info("--- Automation Run Finished ---")
    stats = automation.get_stats()
    central_logger.log_info(f"Final Stats: {json.dumps(stats, indent=2)}")

if __name__ == '__main__':
    main()
