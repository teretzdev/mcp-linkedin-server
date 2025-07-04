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
from dataclasses import dataclass, asdict
from pathlib import Path

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

logger = setup_logging()

# Setup Gemini
def setup_gemini():
    """Setup Gemini API"""
    if not GEMINI_AVAILABLE:
        logger.warning("Gemini not available. Install with: pip install google-generativeai")
        return None
        
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        genai.configure(api_key=gemini_key)
        return genai.GenerativeModel('gemini-pro')
    else:
        logger.warning("GEMINI_API_KEY not found. Gemini matching will be disabled.")
        return None

@dataclass
class JobPreferences:
    """User job preferences for matching"""
    keywords: List[str]
    location: str
    experience_level: str
    job_type: str  # full-time, part-time, contract, etc.
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_preference: bool = True
    companies_to_avoid: List[str] = None
    companies_to_target: List[str] = None
    skills_required: List[str] = None
    skills_preferred: List[str] = None
    selected_resume: str = "resume1.pdf"  # Default resume

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
                logger.error(f"Resume file not found: {file_path}")
                return False
            
            # Check if we have space for another resume
            existing_resumes = self.list_resumes()
            if len(existing_resumes) >= self.max_resumes:
                logger.warning(f"Maximum {self.max_resumes} resumes reached. Delete one first.")
                return False
            
            # Copy to resumes directory
            dest_path = self.resume_dir / f"{resume_name}.pdf"
            shutil.copy2(source_path, dest_path)
            logger.info(f"Resume uploaded: {resume_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload resume: {e}")
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
                logger.info(f"Resume deleted: {resume_name}")
                return True
            else:
                logger.error(f"Resume not found: {resume_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete resume: {e}")
            return False
    
    def get_resume_path(self, resume_name: str) -> Optional[str]:
        """Get the full path of a resume"""
        resume_path = self.resume_dir / f"{resume_name}.pdf"
        return str(resume_path) if resume_path.exists() else None

class AIJobAutomation:
    """AI-powered job automation system"""
    
    def __init__(self, api_base_url: str = "http://localhost:8001"):
        self.api_base_url = api_base_url
        self.preferences = self._load_preferences()
        self.applied_jobs = self._load_applied_jobs()
        self.saved_jobs = self._load_saved_jobs()
        self.resume_manager = ResumeManager()
        self.gemini_model = setup_gemini()
        
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
                    return JobPreferences(**data)
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
        
        # Default preferences
        return JobPreferences(
            keywords=["software engineer", "developer", "programmer"],
            location="Remote",
            experience_level="mid-level",
            job_type="full-time",
            remote_preference=True,
            companies_to_avoid=[],
            companies_to_target=[],
            skills_required=[],
            skills_preferred=[]
        )
    
    def _save_preferences(self):
        """Save user preferences to file"""
        try:
            with open('job_preferences.json', 'w') as f:
                json.dump(asdict(self.preferences), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def _load_applied_jobs(self) -> List[str]:
        """Load list of applied job URLs"""
        try:
            if os.path.exists('applied_jobs.json'):
                with open('applied_jobs.json', 'r') as f:
                    data = json.load(f)
                    return [job.get('job_url', '') for job in data if job.get('job_url')]
        except Exception as e:
            logger.error(f"Failed to load applied jobs: {e}")
        return []
    
    def _load_saved_jobs(self) -> List[str]:
        """Load list of saved job URLs"""
        try:
            if os.path.exists('saved_jobs.json'):
                with open('saved_jobs.json', 'r') as f:
                    data = json.load(f)
                    return [job.get('job_url', '') for job in data if job.get('job_url')]
        except Exception as e:
            logger.error(f"Failed to load saved jobs: {e}")
        return []
    
    def update_preferences(self, **kwargs):
        """Update job preferences"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self._save_preferences()
        logger.info("Job preferences updated")
    
    async def search_jobs(self, query: str = None, location: str = None, count: int = 20) -> List[Dict]:
        """Search for jobs using LinkedIn API"""
        try:
            search_query = query or " ".join(self.preferences.keywords)
            search_location = location or self.preferences.location
            
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
                        logger.info(f"Found {len(jobs)} jobs for query: {search_query}")
                        return jobs
                    else:
                        logger.error(f"Job search failed: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Job search error: {e}")
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
            logger.error(f"Gemini analysis failed: {e}")
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
            job_url = job.get('jobUrl', '')
            if not job_url:
                return False
            
            # Get resume path
            resume_path = self.resume_manager.get_resume_path(self.preferences.selected_resume)
            if not resume_path:
                logger.warning(f"Selected resume not found: {self.preferences.selected_resume}")
                resume_path = ""
            
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
                            logger.info(f"Successfully applied to: {job.get('title', 'Unknown')} with resume: {self.preferences.selected_resume}")
                            return True
                        else:
                            logger.warning(f"Application failed: {data.get('message', 'Unknown error')}")
                            return False
                    else:
                        logger.error(f"Application request failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Application error: {e}")
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
                            logger.info(f"Saved job: {job.get('title', 'Unknown')}")
                            return True
                        else:
                            logger.warning(f"Save failed: {data.get('message', 'Unknown error')}")
                            return False
                    else:
                        logger.error(f"Save request failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Save error: {e}")
            self.automation_stats["errors"] += 1
            return False
    
    async def run_automation_cycle(self, apply_threshold: float = 0.6, save_threshold: float = 0.4):
        """Run one automation cycle"""
        start_time = time.time()
        logger.info("Starting automation cycle...")
        
        # Search for jobs
        jobs = await self.search_jobs()
        if not jobs:
            logger.info("No jobs found in this cycle")
            return
        
        # Score and process jobs
        job_matches = []
        for job in jobs:
            match = self.score_job(job)
            
            # Add Gemini analysis if available
            if self.gemini_model and match.should_apply:
                match.gemini_analysis = await self.analyze_job_with_gemini(job, self.preferences)
                if match.gemini_analysis:
                    logger.info(f"Gemini analysis for {job.get('title', 'Unknown')}: {match.gemini_analysis}")
            
            job_matches.append(match)
            
            if match.should_apply and match.match_score >= apply_threshold:
                # Apply to high-matching jobs
                await self.apply_to_job(job)
            elif match.match_score >= save_threshold:
                # Save medium-matching jobs
                await self.save_job(job)
        
        # Update stats
        self.automation_stats["jobs_matched"] += len([m for m in job_matches if m.should_apply])
        self.automation_stats["last_run"] = datetime.now().isoformat()
        self.automation_stats["total_runtime"] += time.time() - start_time
        self.automation_stats["cycles_completed"] += 1
        
        # Log results
        high_matches = [m for m in job_matches if m.match_score >= apply_threshold]
        medium_matches = [m for m in job_matches if save_threshold <= m.match_score < apply_threshold]
        
        logger.info(f"Cycle complete: {len(high_matches)} high matches, {len(medium_matches)} medium matches")
        
        return {
            "jobs_processed": len(jobs),
            "high_matches": len(high_matches),
            "medium_matches": len(medium_matches),
            "applied": len([m for m in high_matches if m.should_apply]),
            "saved": len([m for m in medium_matches if m.should_apply])
        }
    
    async def run_continuous_automation(self, interval_minutes: int = 30, max_runs: Optional[int] = None):
        """Run continuous automation with specified interval"""
        logger.info(f"Starting continuous automation (interval: {interval_minutes} minutes)")
        
        run_count = 0
        while max_runs is None or run_count < max_runs:
            try:
                cycle_result = await self.run_automation_cycle()
                run_count += 1
                
                if cycle_result:
                    logger.info(f"Run {run_count}: {cycle_result}")
                
                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Automation stopped by user")
                break
            except Exception as e:
                logger.error(f"Automation cycle failed: {e}")
                self.automation_stats["errors"] += 1
                await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("Continuous automation completed")
    
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
    
    # Run one cycle
    result = await automation.run_automation_cycle(apply_threshold=0.7, save_threshold=0.5)
    print(f"Automation result: {result}")
    
    # Get stats
    stats = automation.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
