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

print("[DEBUG] ai_job_automation.py script started.")
logging.basicConfig(level=logging.INFO)
logging.info("[DEBUG] ai_job_automation.py script started (logger).")

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure central logging
def setup_logging():
    """Setup central logging to both file and console"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "automation.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Root logger
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
            
            # Check if we have space for another resume
            existing_resumes = self.list_resumes()
            if len(existing_resumes) >= self.max_resumes:
                central_logger.log_warning(f"Maximum {self.max_resumes} resumes reached. Delete one first.")
                return False
            
            # Copy to resumes directory
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
    """AI-powered job automation system"""
    
    def __init__(self, api_base_url: str = ""):
        # Load port from config if available
        config_port = 8002
        config_path = os.path.join('enhanced-mcp-server', 'config', 'mcp_config.json')
        if os.path.exists(config_path):
            import json
            with open(config_path) as f:
                config = json.load(f)
                config_port = config.get('server', {}).get('port', 8002)
        # Fallback to 8002 if detection fails
        if not config_port:
            config_port = 8002
        self.api_base_url = api_base_url or f"http://localhost:{config_port}"
        print(f"[Startup] Using backend port: {config_port}")
        print(f"[Startup] API base URL: {self.api_base_url}")
        self.preferences = self._load_preferences()
        self.applied_jobs = self._load_applied_jobs()
        self.saved_jobs = self._load_saved_jobs()
        self.failed_jobs = self._load_failed_jobs()
        self.resume_manager = ResumeManager()
        self.gemini_model = setup_gemini()
        # Port management logic
        self.used_ports = self.get_used_ports()
        self.avoid_port_range = range(8000, 8010)
        # if config_port in self.used_ports:
        #     print(f"[Startup] Port {config_port} is already in use. Attempting to free it...")
        #     self.kill_process_on_port(config_port)
        # # Check backend health before running automation
        # if not self.check_backend_health():
        #     print(f"[Startup] Backend at {self.api_base_url} is not healthy. Attempting to restart backend...")
        #     self.restart_backend(config_port)
        #     if not self.check_backend_health():
        #         raise RuntimeError(f"[Startup] Backend at {self.api_base_url} is still not healthy after restart.")
        # print(f"[Startup] Backend at {self.api_base_url} is healthy.")
        
        self.automation_stats = {
            "jobs_searched": 0,
            "jobs_matched": 0,
            "jobs_applied": 0,
            "jobs_saved": 0,
            "last_run": None,
            "total_runtime": 0,
            "cycles_completed": 0,
            "errors": 0
        }
        
    def _load_preferences(self) -> JobPreferences:
        """Load user preferences from file"""
        try:
            if os.path.exists('job_preferences.json'):
                with open('job_preferences.json', 'r') as f:
                    data = json.load(f)
                    # Only keep fields that are in JobPreferences
                    allowed_fields = set(JobPreferences.__dataclass_fields__.keys())
                    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                    # Ensure all list fields are lists, not None
                    for key in ['keywords', 'companies_to_avoid', 'companies_to_target', 'skills_required', 'skills_preferred']:
                        if key in filtered_data and filtered_data[key] is None:
                            filtered_data[key] = []
                    return JobPreferences(**filtered_data)
        except Exception as e:
            central_logger.log_error(f"Failed to load preferences: {e}")
        
        # Default preferences
        return JobPreferences()
    
    def _save_preferences(self):
        """Save user preferences to file"""
        try:
            with open('job_preferences.json', 'w') as f:
                json.dump(asdict(self.preferences), f, indent=2)
        except Exception as e:
            central_logger.log_error(f"Failed to save preferences: {e}")
    
    def _load_applied_jobs(self) -> List[str]:
        """Load list of applied job URLs"""
        try:
            if os.path.exists('applied_jobs.json'):
                with open('applied_jobs.json', 'r') as f:
                    data = json.load(f)
                    return [job.get('job_url', '') for job in data if job.get('job_url')]
        except Exception as e:
            central_logger.log_error(f"Failed to load applied jobs: {e}")
        return []
    
    def _load_saved_jobs(self) -> List[str]:
        """Load list of saved job URLs"""
        try:
            if os.path.exists('saved_jobs.json'):
                with open('saved_jobs.json', 'r') as f:
                    data = json.load(f)
                    return [job.get('job_url', '') for job in data if job.get('job_url')]
        except Exception as e:
            central_logger.log_error(f"Failed to load saved jobs: {e}")
        return []
    
    def _load_failed_jobs(self) -> List[str]:
        try:
            if os.path.exists('failed_jobs.json'):
                with open('failed_jobs.json', 'r') as f:
                    data = json.load(f)
                    return [job.get('job_url', '') for job in data if job.get('job_url')]
        except Exception as e:
            central_logger.log_error(f"Failed to load failed jobs: {e}")
        return []
    
    def update_preferences(self, **kwargs):
        """Update job preferences"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self._save_preferences()
        central_logger.log_info("Job preferences updated")
    
    async def search_jobs(self, query: str = "", location: str = "", count: int = 20) -> List[Dict]:
        """Search for jobs using LinkedIn API"""
        try:
            search_query = query if query else " ".join(self.preferences.keywords)
            search_location = location if location else self.preferences.location
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/search_jobs", json={
                    "query": search_query,
                    "location": search_location,
                    "count": count
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("jobs", [])
                        self.automation_stats["jobs_searched"] += len(jobs)
                        central_logger.log_info(f"Found {len(jobs)} jobs for query: {search_query}")
                        return jobs
                    else:
                        central_logger.log_error(f"Job search failed: {response.status}")
                        return []
        except Exception as e:
            central_logger.log_error(f"Job search error: {e}")
            self.automation_stats["errors"] += 1
            return []
    
    async def analyze_job_with_gemini(self, job: Dict, preferences: JobPreferences) -> Optional[str]:
        """Use Gemini to analyze job fit"""
        if not self.gemini_model:
            return None
            
        try:
            prompt = f"""
            Analyze this job posting for a candidate with these preferences:
            
            CANDIDATE PREFERENCES:
            - Keywords: {', '.join(preferences.keywords)}
            - Location: {preferences.location}
            - Experience: {preferences.experience_level}
            - Job Type: {preferences.job_type}
            - Remote Preference: {preferences.remote_preference}
            - Required Skills: {', '.join(preferences.skills_required or [])}
            - Preferred Skills: {', '.join(preferences.skills_preferred or [])}
            
            JOB POSTING:
            - Title: {job.get('title', '')}
            - Company: {job.get('company', '')}
            - Location: {job.get('location', '')}
            - Description: {job.get('descriptionSnippet', '')}
            
            Provide a brief analysis (2-3 sentences) of how well this job matches the candidate's preferences.
            Focus on skills match, location fit, and overall suitability.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            return response.text
            
        except Exception as e:
            central_logger.log_error(f"Gemini analysis failed: {e}")
            return None
    
    def score_job(self, job: Dict) -> JobMatch:
        """Score a job based on user preferences"""
        score = 0.0
        reasons = []
        
        # Skip if already applied or saved
        job_url = job.get('jobUrl', '')
        if job_url in self.applied_jobs:
            return JobMatch(job, 0.0, ["Already applied"], False)
        if job_url in self.saved_jobs:
            return JobMatch(job, 0.0, ["Already saved"], False)
        if job_url in self.failed_jobs:
            return JobMatch(job, 0.0, ["Previously failed"], False)
        
        # Title matching (40% weight)
        title = job.get('title', '')
        title_score = 0
        for keyword in self.preferences.keywords:
            if keyword.lower() in title.lower():
                title_score += 1
                reasons.append(f"Title contains '{keyword}'")
        
        if title_score > 0:
            score += (title_score / len(self.preferences.keywords)) * 0.4
        
        # Company matching (20% weight)
        company = job.get('company', '')
        if self.preferences.companies_to_target and any(target.lower() in company.lower() for target in self.preferences.companies_to_target):
            score += 0.2
            reasons.append("Target company")
        
        if self.preferences.companies_to_avoid and any(avoid.lower() in company.lower() for avoid in self.preferences.companies_to_avoid):
            score -= 0.3
            reasons.append("Company to avoid")
        
        # Location matching (15% weight)
        location = job.get('location', '')
        if self.preferences.remote_preference and ('remote' in location.lower() or 'anywhere' in location.lower()):
            score += 0.15
            reasons.append("Remote position")
        elif self.preferences.location.lower() in location.lower():
            score += 0.15
            reasons.append("Location match")
        
        # Description matching (15% weight)
        description = job.get('descriptionSnippet', '')
        desc_score = 0
        for keyword in self.preferences.keywords:
            if keyword.lower() in description.lower():
                desc_score += 1
        
        if desc_score > 0:
            score += (desc_score / len(self.preferences.keywords)) * 0.15
            reasons.append("Description contains keywords")
        
        # Skills matching (10% weight)
        if self.preferences.skills_required:
            skills_score = 0
            for skill in self.preferences.skills_required:
                if skill.lower() in title.lower() or skill.lower() in description.lower():
                    skills_score += 1
            
            if skills_score > 0:
                score += (skills_score / len(self.preferences.skills_required)) * 0.1
                reasons.append("Required skills match")
        
        # Determine if should apply (threshold-based)
        should_apply = score >= 0.6  # 60% threshold
        
        return JobMatch(job, score, reasons, should_apply)
    
    async def apply_to_job(self, job: Dict) -> bool:
        """Apply to a job with selected resume"""
        try:
            job_url = job.get('jobUrl', '') or ''
            if not job_url:
                return False
            
            # Get resume path
            resume_path = self.resume_manager.get_resume_path(self.preferences.selected_resume) or ""
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/apply_job", json={
                    "job_url": job_url,
                    "resume_path": resume_path
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            self.applied_jobs.append(job_url)
                            self.automation_stats["jobs_applied"] += 1
                            central_logger.log_info(f"Successfully applied to: {job.get('title', 'Unknown')} with resume: {self.preferences.selected_resume}")
                            return True
                        else:
                            central_logger.log_warning(f"Application failed: {data.get('message', 'Unknown error')}")
                            return False
                    else:
                        central_logger.log_error(f"Application request failed: {response.status}")
                        return False
        except Exception as e:
            central_logger.log_error(f"Application error: {e}")
            self.automation_stats["errors"] += 1
            return False
    
    async def save_job(self, job: Dict) -> bool:
        """Save a job for later"""
        try:
            job_url = job.get('jobUrl', '')
            if not job_url:
                return False
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base_url}/api/save_job", json={
                    "job_url": job_url
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            self.saved_jobs.append(job_url)
                            self.automation_stats["jobs_saved"] += 1
                            central_logger.log_info(f"Saved job: {job.get('title', 'Unknown')}")
                            return True
                        else:
                            central_logger.log_warning(f"Save failed: {data.get('message', 'Unknown error')}")
                            return False
                    else:
                        central_logger.log_error(f"Save request failed: {response.status}")
                        return False
        except Exception as e:
            central_logger.log_error(f"Save error: {e}")
            self.automation_stats["errors"] += 1
            return False
    
    async def run_automation_cycle(self, apply_threshold: float = 0.4, save_threshold: float = 0.2, count: int = 20):
        """Run one automation cycle"""
        start_time = time.time()
        central_logger.log_info("Starting automation cycle...")
        jobs = await self.search_jobs(count=count)
        if not jobs:
            central_logger.log_info("No jobs found in this cycle")
            print("[STATUS] Applied: 0 | Failed: 0 | Saved: 0")
            return
        job_matches = []
        applied_jobs = []
        not_applied_jobs = []
        failed_jobs = []
        saved_jobs = []
        for job in jobs:
            match = self.score_job(job)
            job_matches.append(match)
            if match.should_apply and match.match_score >= apply_threshold:
                success = await self.apply_to_job(job)
                if success:
                    applied_jobs.append(job)
                else:
                    failed_jobs.append(job)
            elif save_threshold <= match.match_score < apply_threshold:
                saved_jobs.append(job)
            else:
                not_applied_jobs.append(job)
        # Export details
        with open('applied_jobs_detailed.json', 'w', encoding='utf-8') as f:
            json.dump(applied_jobs, f, indent=2, ensure_ascii=False)
        with open('not_applied_jobs_detailed.json', 'w', encoding='utf-8') as f:
            json.dump(not_applied_jobs, f, indent=2, ensure_ascii=False)
        # Persistently update applied, saved, and failed jobs
        # Load existing jobs from file (full job dicts)
        existing_applied = []
        if os.path.exists('applied_jobs.json'):
            with open('applied_jobs.json', 'r', encoding='utf-8') as f:
                existing_applied = json.load(f)
        existing_saved = []
        if os.path.exists('saved_jobs.json'):
            with open('saved_jobs.json', 'r', encoding='utf-8') as f:
                existing_saved = json.load(f)
        existing_failed = []
        if os.path.exists('failed_jobs.json'):
            with open('failed_jobs.json', 'r', encoding='utf-8') as f:
                existing_failed = json.load(f)
        # Add new jobs, avoiding duplicates
        def merge_jobs(existing, new):
            urls = {job.get('job_url', job.get('jobUrl', '')) for job in existing}
            for job in new:
                url = job.get('job_url', job.get('jobUrl', ''))
                if url and url not in urls:
                    existing.append(job)
                    urls.add(url)
            return existing
        self._save_applied_jobs(merge_jobs(existing_applied, applied_jobs))
        self._save_saved_jobs(merge_jobs(existing_saved, saved_jobs))
        self._save_failed_jobs(merge_jobs(existing_failed, failed_jobs))
        # Update stats
        self.automation_stats["jobs_matched"] += len([m for m in job_matches if m.should_apply])
        self.automation_stats["last_run"] = datetime.now().isoformat()
        self.automation_stats["total_runtime"] += time.time() - start_time
        self.automation_stats["cycles_completed"] += 1
        # Log results
        high_matches = [m for m in job_matches if m.match_score >= apply_threshold]
        medium_matches = [m for m in job_matches if save_threshold <= m.match_score < apply_threshold]
        central_logger.log_info(f"Cycle complete: {len(high_matches)} high matches, {len(medium_matches)} medium matches")
        # Concise status update (single line)
        print(f"[STATUS] Applied: {len(applied_jobs)} | Failed: {len(failed_jobs)} | Saved: {len(saved_jobs)}")
        return {
            "jobs_processed": len(jobs),
            "high_matches": len(high_matches),
            "medium_matches": len(medium_matches),
            "applied": len([m for m in high_matches if m.should_apply]),
            "saved": len([m for m in medium_matches if m.should_apply])
        }
    
    async def run_continuous_automation(self, interval_minutes: int = 30, max_runs: Optional[int] = None):
        """Run continuous automation with specified interval"""
        central_logger.log_info(f"Starting continuous automation (interval: {interval_minutes} minutes)")
        
        run_count = 0
        while max_runs is None or run_count < max_runs:
            try:
                cycle_result = await self.run_automation_cycle()
                run_count += 1
                
                if cycle_result:
                    central_logger.log_info(f"Run {run_count}: {cycle_result}")
                
                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                central_logger.log_info("Automation stopped by user")
                break
            except Exception as e:
                central_logger.log_error(f"Automation cycle failed: {e}")
                self.automation_stats["errors"] += 1
                await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        central_logger.log_info("Continuous automation completed")
    
    def get_stats(self) -> Dict:
        """Get automation statistics"""
        return {
            **self.automation_stats,
            "preferences": asdict(self.preferences),
            "applied_count": len(self.applied_jobs),
            "saved_count": len(self.saved_jobs),
            "resumes": self.resume_manager.list_resumes(),
            "gemini_available": self.gemini_model is not None
        }
    
    def get_job_matches(self, jobs: List[Dict]) -> List[JobMatch]:
        """Get scored matches for a list of jobs"""
        return [self.score_job(job) for job in jobs]

    def get_used_ports(self):
        used_ports = set()
        for conn in psutil.net_connections():
            if conn.status == 'LISTEN' and conn.laddr:
                used_ports.add(conn.laddr.port)
        return used_ports

    def kill_process_on_port(self, port):
        """Kill a process running on a specific port"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        central_logger.log_info(f"Killing process {proc.name()} (PID: {proc.pid}) on port {port}")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except Exception as e:
                # Catch other potential errors like missing permissions
                central_logger.log_warning(f"Could not check connections for process {proc.pid}: {e}")

    def check_backend_health(self):
        try:
            resp = requests.get(f"{self.api_base_url}/api/health", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"[Startup] Health check failed: {e}")
            return False

    def restart_backend(self, port):
        # Attempt to kill and restart backend process on the given port
        self.kill_process_on_port(port)
        # Try to start backend using auto_startup.py
        try:
            import subprocess
            subprocess.Popen(["python", "auto_startup.py"])
            import time
            time.sleep(5)  # Wait for backend to start
        except Exception as e:
            print(f"[Startup] Failed to restart backend: {e}")

    def _save_applied_jobs(self, jobs: List[Dict]):
        try:
            with open('applied_jobs.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            central_logger.log_error(f"Failed to save applied jobs: {e}")

    def _save_saved_jobs(self, jobs: List[Dict]):
        try:
            with open('saved_jobs.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            central_logger.log_error(f"Failed to save saved jobs: {e}")

    def _save_failed_jobs(self, jobs: List[Dict]):
        try:
            with open('failed_jobs.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            central_logger.log_error(f"Failed to save failed jobs: {e}")

# Global automation instance
automation_instance = None

def get_automation_instance() -> AIJobAutomation:
    """Get or create the global automation instance"""
    global automation_instance
    if automation_instance is None:
        automation_instance = AIJobAutomation()
    return automation_instance

# Example usage
async def main():
    """Example of how to use the AI job automation"""
    automation = AIJobAutomation()
    
    # Update preferences
    automation.update_preferences(
        keywords=["python developer", "software engineer", "backend developer"],
        location="Remote",
        experience_level="mid-level",
        job_type="full-time",
        remote_preference=True,
        skills_required=["Python", "Django", "PostgreSQL"],
        skills_preferred=["React", "AWS", "Docker"]
    )
    
    # Run one cycle for 5 applications (user request)
    result = await automation.run_automation_cycle(apply_threshold=0.7, save_threshold=0.5, count=5)
    print(f"Automation result: {result}")
    
    # Get stats
    stats = automation.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())

# --- Logging Setup ---
logger = logging.getLogger("ai_job_automation")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler (rotating)
fh = RotatingFileHandler('logs/ai_job_automation.log', maxBytes=2*1024*1024, backupCount=3)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
