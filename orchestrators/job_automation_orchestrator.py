"""
Job automation orchestrator that coordinates the entire process.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import importlib.util

from core.models.job_data import JobData, SearchCriteria, JobStatus, ApplicationResult
from core.config.settings import get_config, AutomationConfig
from services.job_search_service import JobSearchService, JobSearchError, JobSearchTimeoutError
from repositories.job_repository import JobRepository
from legacy.database.database import DatabaseManager
from centralized_logging import get_logger


class JobAutomationStats:
    """Statistics tracking for automation runs"""
    
    def __init__(self):
        self.jobs_searched = 0
        self.new_jobs_added = 0
        self.jobs_applied = 0
        self.errors = 0
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            'jobs_searched': self.jobs_searched,
            'new_jobs_added': self.new_jobs_added,
            'jobs_applied': self.jobs_applied,
            'errors': self.errors,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': duration
        }


class JobAutomationOrchestrator:
    """Main orchestrator for job automation process"""
    
    def __init__(
        self,
        config: Optional[AutomationConfig] = None,
        job_search_service: Optional[JobSearchService] = None,
        job_repository: Optional[JobRepository] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        self.config = config or get_config()
        self.logger = get_logger('orchestrator')
        
        # Initialize services with dependency injection
        self.db_manager = db_manager or DatabaseManager()
        self.job_repository = job_repository or JobRepository(self.db_manager)
        self.job_search_service = job_search_service or JobSearchService()
        
        # Initialize user
        self.user_id = self._get_or_create_default_user()
        
        # Statistics
        self.stats = JobAutomationStats()
    
    def _get_or_create_default_user(self) -> int:
        """Get or create the default automation user"""
        try:
            user_id = self.db_manager.get_user("default_user")
            if not user_id:
                user_id = self.db_manager.create_user(
                    username="default_user",
                    email="automation@example.com",
                    current_position="Software Engineer"
                )
            return user_id
        except Exception as e:
            self.logger.log_error(f"Failed to get/create default user: {e}")
            raise
    
    async def enqueue_scrape_job(self, search_criteria: SearchCriteria):
        """Enqueue a scrape job to the aioredis queue instead of running immediately."""
        if aioredis_queue is None:
            self.logger.log_error("aioredis_queue.py not found. Cannot enqueue job.")
            return
        redis = await aioredis_queue.get_redis()
        await aioredis_queue.enqueue_job(redis, 'scrape', {
            'query': search_criteria.query,
            'location': search_criteria.location,
            'count': search_criteria.count
        })
        self.logger.log_info(f"[ENQUEUED] Scrape job: {search_criteria.query}, {search_criteria.location}, {search_criteria.count}")

    async def enqueue_apply_job(self, job_id: str, resume: str = ""):  # Example for application jobs
        if aioredis_queue is None:
            self.logger.log_error("aioredis_queue.py not found. Cannot enqueue job.")
            return
        redis = await aioredis_queue.get_redis()
        await aioredis_queue.enqueue_job(redis, 'apply', {
            'job_id': job_id,
            'resume': resume
        })
        self.logger.log_info(f"[ENQUEUED] Apply job: {job_id}, {resume}")

    async def run_reconnaissance_phase(self, search_criteria: SearchCriteria) -> Dict[str, Any]:
        """
        Run Phase 1: Job reconnaissance (search and scrape).
        
        Args:
            search_criteria: Search parameters
            
        Returns:
            Dictionary with results and statistics
        """
        self.logger.log_info("=== Starting Phase 1: Reconnaissance ===")
        self.stats = JobAutomationStats()  # Reset stats
        
        try:
            # Test connection first
            self.logger.log_info("Testing LinkedIn connection...")
            connection_ok = await self.job_search_service.test_connection()
            if not connection_ok:
                raise JobSearchError("LinkedIn connection test failed")
            
            # Perform job search
            self.logger.log_info(f"Searching for jobs: '{search_criteria.query}' in '{search_criteria.location}'")
            jobs = await self.job_search_service.search_jobs(search_criteria)
            
            self.stats.jobs_searched = len(jobs)
            self.logger.log_info(f"Found {len(jobs)} jobs from search")
            
            # Save jobs to database
            new_jobs_count = 0
            for job in jobs:
                try:
                    if self.job_repository.save_scraped_job(self.user_id, job):
                        new_jobs_count += 1
                except Exception as e:
                    self.logger.log_warning(f"Failed to save job {job.job_id}: {e}")
                    self.stats.errors += 1
            
            self.stats.new_jobs_added = new_jobs_count
            self.stats.end_time = datetime.now()
            
            result = {
                'status': 'success',
                'message': f'Reconnaissance complete: {new_jobs_count} new jobs added',
                'total_found': len(jobs),
                'new_jobs_added': new_jobs_count,
                'stats': self.stats.to_dict()
            }
            
            self.logger.log_info(f"Reconnaissance phase completed: {new_jobs_count} new jobs added")
            return result
            
        except JobSearchTimeoutError as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Job search timed out: {str(e)}"
            self.logger.log_error(error_msg)
            return {
                'status': 'timeout',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
            
        except JobSearchError as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Job search failed: {str(e)}"
            self.logger.log_error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
            
        except Exception as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Unexpected error in reconnaissance: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
    
    async def run_application_phase(self, max_applications: Optional[int] = None) -> Dict[str, Any]:
        """
        Run Phase 2: Job application.
        
        Args:
            max_applications: Maximum number of applications to submit
            
        Returns:
            Dictionary with results and statistics
        """
        self.logger.log_info("=== Starting Phase 2: Application ===")
        
        if max_applications is None:
            max_applications = self.config.automation.max_applications_per_cycle
        
        try:
            # Get scraped jobs ready for application
            scraped_jobs = self.job_repository.get_jobs_by_status(
                self.user_id, 
                JobStatus.SCRAPED, 
                max_applications
            )
            
            if not scraped_jobs:
                self.logger.log_info("No scraped jobs available for application")
                return {
                    'status': 'success',
                    'message': 'No jobs available for application',
                    'applications_submitted': 0,
                    'jobs_available': 0
                }
            
            self.logger.log_info(f"Found {len(scraped_jobs)} jobs ready for application")
            
            # Apply to jobs
            applications_submitted = 0
            for job in scraped_jobs[:max_applications]:
                try:
                    # Update status to applying
                    self.job_repository.update_job_status(
                        self.user_id, 
                        job.job_id, 
                        JobStatus.APPLYING
                    )
                    
                    # TODO: Implement actual job application logic
                    # For now, we'll simulate the application process
                    application_result = await self._simulate_job_application(job)
                    
                    if application_result.status.value == 'submitted':
                        self.job_repository.update_job_status(
                            self.user_id, 
                            job.job_id, 
                            JobStatus.APPLIED
                        )
                        applications_submitted += 1
                        self.logger.log_info(f"Applied to: {job.title} at {job.company}")
                    else:
                        self.job_repository.update_job_status(
                            self.user_id, 
                            job.job_id, 
                            JobStatus.FAILED,
                            application_result.error_details
                        )
                        self.logger.log_warning(f"Failed to apply to {job.title}: {application_result.message}")
                    
                except Exception as e:
                    self.logger.log_error(f"Error applying to job {job.job_id}: {e}")
                    self.job_repository.update_job_status(
                        self.user_id, 
                        job.job_id, 
                        JobStatus.FAILED,
                        str(e)
                    )
                    self.stats.errors += 1
            
            self.stats.jobs_applied = applications_submitted
            
            result = {
                'status': 'success',
                'message': f'Application phase complete: {applications_submitted} applications submitted',
                'applications_submitted': applications_submitted,
                'jobs_available': len(scraped_jobs),
                'stats': self.stats.to_dict()
            }
            
            self.logger.log_info(f"Application phase completed: {applications_submitted} applications submitted")
            return result
            
        except Exception as e:
            error_msg = f"Error in application phase: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
    
    async def _simulate_job_application(self, job: JobData) -> ApplicationResult:
        """
        Simulate job application process.
        TODO: Replace with actual application logic.
        """
        # Simulate processing time
        await asyncio.sleep(1)
        
        # For now, just mark as submitted
        from core.models.job_data import ApplicationStatus
        return ApplicationResult(
            job_id=job.job_id,
            status=ApplicationStatus.SUBMITTED,
            message="Application submitted successfully (simulated)"
        )
    
    async def run_full_automation_cycle(self, search_criteria: SearchCriteria) -> Dict[str, Any]:
        """
        Run a complete automation cycle: reconnaissance + application.
        
        Args:
            search_criteria: Search parameters for reconnaissance
            
        Returns:
            Dictionary with complete results
        """
        self.logger.log_info("=== Starting Full Automation Cycle ===")
        
        try:
            # Phase 1: Reconnaissance
            recon_result = await self.run_reconnaissance_phase(search_criteria)
            
            if recon_result['status'] != 'success':
                self.logger.log_error(f"Reconnaissance failed: {recon_result['message']}")
                return recon_result
            
            # Wait between phases
            delay = self.config.automation.cycle_delay_minutes * 60
            if delay > 0:
                self.logger.log_info(f"Waiting {delay} seconds between phases...")
                await asyncio.sleep(delay)
            
            # Phase 2: Application
            app_result = await self.run_application_phase()
            
            # Combine results
            combined_result = {
                'status': 'success',
                'message': 'Full automation cycle completed',
                'reconnaissance': recon_result,
                'application': app_result,
                'total_stats': {
                    'jobs_found': recon_result.get('total_found', 0),
                    'new_jobs_added': recon_result.get('new_jobs_added', 0),
                    'applications_submitted': app_result.get('applications_submitted', 0),
                    'total_errors': recon_result.get('stats', {}).get('errors', 0) + 
                                   app_result.get('stats', {}).get('errors', 0)
                }
            }
            
            self.logger.log_info("Full automation cycle completed successfully")
            return combined_result
            
        except Exception as e:
            error_msg = f"Error in full automation cycle: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def get_automation_summary(self) -> Dict[str, Any]:
        """Get summary of automation status"""
        try:
            return {
                'scraped_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.SCRAPED),
                'applied_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.APPLIED),
                'failed_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.FAILED),
                'recent_jobs': len(self.job_repository.get_recent_jobs(self.user_id, days=1)),
                'config': {
                    'max_applications_per_cycle': self.config.automation.max_applications_per_cycle,
                    'search_timeout': self.config.automation.job_search_timeout_seconds,
                    'application_timeout': self.config.automation.application_timeout_seconds
                }
            }
        except Exception as e:
            self.logger.log_error(f"Failed to get automation summary: {e}")
            return {'error': str(e)} 

# Try to import aioredis_queue for async job queueing
aioredis_queue_spec = importlib.util.find_spec('services.aioredis_queue')
aioredis_queue = None
if aioredis_queue_spec is not None:
    aioredis_queue = importlib.util.module_from_spec(aioredis_queue_spec)
    aioredis_queue_spec.loader.exec_module(aioredis_queue)

class JobAutomationOrchestrator:
    """Main orchestrator for job automation process"""
    
    def __init__(
        self,
        config: Optional[AutomationConfig] = None,
        job_search_service: Optional[JobSearchService] = None,
        job_repository: Optional[JobRepository] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        self.config = config or get_config()
        self.logger = get_logger('orchestrator')
        
        # Initialize services with dependency injection
        self.db_manager = db_manager or DatabaseManager()
        self.job_repository = job_repository or JobRepository(self.db_manager)
        self.job_search_service = job_search_service or JobSearchService()
        
        # Initialize user
        self.user_id = self._get_or_create_default_user()
        
        # Statistics
        self.stats = JobAutomationStats()
    
    def _get_or_create_default_user(self) -> int:
        """Get or create the default automation user"""
        try:
            user_id = self.db_manager.get_user("default_user")
            if not user_id:
                user_id = self.db_manager.create_user(
                    username="default_user",
                    email="automation@example.com",
                    current_position="Software Engineer"
                )
            return user_id
        except Exception as e:
            self.logger.log_error(f"Failed to get/create default user: {e}")
            raise
    
    async def enqueue_scrape_job(self, search_criteria: SearchCriteria):
        """Enqueue a scrape job to the aioredis queue instead of running immediately."""
        if aioredis_queue is None:
            self.logger.log_error("aioredis_queue.py not found. Cannot enqueue job.")
            return
        redis = await aioredis_queue.get_redis()
        await aioredis_queue.enqueue_job(redis, 'scrape', {
            'query': search_criteria.query,
            'location': search_criteria.location,
            'count': search_criteria.count
        })
        self.logger.log_info(f"[ENQUEUED] Scrape job: {search_criteria.query}, {search_criteria.location}, {search_criteria.count}")

    async def enqueue_apply_job(self, job_id: str, resume: str = ""):  # Example for application jobs
        if aioredis_queue is None:
            self.logger.log_error("aioredis_queue.py not found. Cannot enqueue job.")
            return
        redis = await aioredis_queue.get_redis()
        await aioredis_queue.enqueue_job(redis, 'apply', {
            'job_id': job_id,
            'resume': resume
        })
        self.logger.log_info(f"[ENQUEUED] Apply job: {job_id}, {resume}")

    async def run_reconnaissance_phase(self, search_criteria: SearchCriteria) -> Dict[str, Any]:
        """
        Run Phase 1: Job reconnaissance (search and scrape).
        
        Args:
            search_criteria: Search parameters
            
        Returns:
            Dictionary with results and statistics
        """
        self.logger.log_info("=== Starting Phase 1: Reconnaissance ===")
        self.stats = JobAutomationStats()  # Reset stats
        
        try:
            # Test connection first
            self.logger.log_info("Testing LinkedIn connection...")
            connection_ok = await self.job_search_service.test_connection()
            if not connection_ok:
                raise JobSearchError("LinkedIn connection test failed")
            
            # Perform job search
            self.logger.log_info(f"Searching for jobs: '{search_criteria.query}' in '{search_criteria.location}'")
            jobs = await self.job_search_service.search_jobs(search_criteria)
            
            self.stats.jobs_searched = len(jobs)
            self.logger.log_info(f"Found {len(jobs)} jobs from search")
            
            # Save jobs to database
            new_jobs_count = 0
            for job in jobs:
                try:
                    if self.job_repository.save_scraped_job(self.user_id, job):
                        new_jobs_count += 1
                except Exception as e:
                    self.logger.log_warning(f"Failed to save job {job.job_id}: {e}")
                    self.stats.errors += 1
            
            self.stats.new_jobs_added = new_jobs_count
            self.stats.end_time = datetime.now()
            
            result = {
                'status': 'success',
                'message': f'Reconnaissance complete: {new_jobs_count} new jobs added',
                'total_found': len(jobs),
                'new_jobs_added': new_jobs_count,
                'stats': self.stats.to_dict()
            }
            
            self.logger.log_info(f"Reconnaissance phase completed: {new_jobs_count} new jobs added")
            return result
            
        except JobSearchTimeoutError as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Job search timed out: {str(e)}"
            self.logger.log_error(error_msg)
            return {
                'status': 'timeout',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
            
        except JobSearchError as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Job search failed: {str(e)}"
            self.logger.log_error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
            
        except Exception as e:
            self.stats.errors += 1
            self.stats.end_time = datetime.now()
            error_msg = f"Unexpected error in reconnaissance: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
    
    async def run_application_phase(self, max_applications: Optional[int] = None) -> Dict[str, Any]:
        """
        Run Phase 2: Job application.
        
        Args:
            max_applications: Maximum number of applications to submit
            
        Returns:
            Dictionary with results and statistics
        """
        self.logger.log_info("=== Starting Phase 2: Application ===")
        
        if max_applications is None:
            max_applications = self.config.automation.max_applications_per_cycle
        
        try:
            # Get scraped jobs ready for application
            scraped_jobs = self.job_repository.get_jobs_by_status(
                self.user_id, 
                JobStatus.SCRAPED, 
                max_applications
            )
            
            if not scraped_jobs:
                self.logger.log_info("No scraped jobs available for application")
                return {
                    'status': 'success',
                    'message': 'No jobs available for application',
                    'applications_submitted': 0,
                    'jobs_available': 0
                }
            
            self.logger.log_info(f"Found {len(scraped_jobs)} jobs ready for application")
            
            # Apply to jobs
            applications_submitted = 0
            for job in scraped_jobs[:max_applications]:
                try:
                    # Update status to applying
                    self.job_repository.update_job_status(
                        self.user_id, 
                        job.job_id, 
                        JobStatus.APPLYING
                    )
                    
                    # TODO: Implement actual job application logic
                    # For now, we'll simulate the application process
                    application_result = await self._simulate_job_application(job)
                    
                    if application_result.status.value == 'submitted':
                        self.job_repository.update_job_status(
                            self.user_id, 
                            job.job_id, 
                            JobStatus.APPLIED
                        )
                        applications_submitted += 1
                        self.logger.log_info(f"Applied to: {job.title} at {job.company}")
                    else:
                        self.job_repository.update_job_status(
                            self.user_id, 
                            job.job_id, 
                            JobStatus.FAILED,
                            application_result.error_details
                        )
                        self.logger.log_warning(f"Failed to apply to {job.title}: {application_result.message}")
                    
                except Exception as e:
                    self.logger.log_error(f"Error applying to job {job.job_id}: {e}")
                    self.job_repository.update_job_status(
                        self.user_id, 
                        job.job_id, 
                        JobStatus.FAILED,
                        str(e)
                    )
                    self.stats.errors += 1
            
            self.stats.jobs_applied = applications_submitted
            
            result = {
                'status': 'success',
                'message': f'Application phase complete: {applications_submitted} applications submitted',
                'applications_submitted': applications_submitted,
                'jobs_available': len(scraped_jobs),
                'stats': self.stats.to_dict()
            }
            
            self.logger.log_info(f"Application phase completed: {applications_submitted} applications submitted")
            return result
            
        except Exception as e:
            error_msg = f"Error in application phase: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg,
                'stats': self.stats.to_dict()
            }
    
    async def _simulate_job_application(self, job: JobData) -> ApplicationResult:
        """
        Simulate job application process.
        TODO: Replace with actual application logic.
        """
        # Simulate processing time
        await asyncio.sleep(1)
        
        # For now, just mark as submitted
        from core.models.job_data import ApplicationStatus
        return ApplicationResult(
            job_id=job.job_id,
            status=ApplicationStatus.SUBMITTED,
            message="Application submitted successfully (simulated)"
        )
    
    async def run_full_automation_cycle(self, search_criteria: SearchCriteria) -> Dict[str, Any]:
        """
        Run a complete automation cycle: reconnaissance + application.
        
        Args:
            search_criteria: Search parameters for reconnaissance
            
        Returns:
            Dictionary with complete results
        """
        self.logger.log_info("=== Starting Full Automation Cycle ===")
        
        try:
            # Phase 1: Reconnaissance
            recon_result = await self.run_reconnaissance_phase(search_criteria)
            
            if recon_result['status'] != 'success':
                self.logger.log_error(f"Reconnaissance failed: {recon_result['message']}")
                return recon_result
            
            # Wait between phases
            delay = self.config.automation.cycle_delay_minutes * 60
            if delay > 0:
                self.logger.log_info(f"Waiting {delay} seconds between phases...")
                await asyncio.sleep(delay)
            
            # Phase 2: Application
            app_result = await self.run_application_phase()
            
            # Combine results
            combined_result = {
                'status': 'success',
                'message': 'Full automation cycle completed',
                'reconnaissance': recon_result,
                'application': app_result,
                'total_stats': {
                    'jobs_found': recon_result.get('total_found', 0),
                    'new_jobs_added': recon_result.get('new_jobs_added', 0),
                    'applications_submitted': app_result.get('applications_submitted', 0),
                    'total_errors': recon_result.get('stats', {}).get('errors', 0) + 
                                   app_result.get('stats', {}).get('errors', 0)
                }
            }
            
            self.logger.log_info("Full automation cycle completed successfully")
            return combined_result
            
        except Exception as e:
            error_msg = f"Error in full automation cycle: {type(e).__name__}: {str(e)}"
            self.logger.log_error(error_msg, exc_info=True)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def get_automation_summary(self) -> Dict[str, Any]:
        """Get summary of automation status"""
        try:
            return {
                'scraped_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.SCRAPED),
                'applied_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.APPLIED),
                'failed_jobs': self.job_repository.get_jobs_count_by_status(self.user_id, JobStatus.FAILED),
                'recent_jobs': len(self.job_repository.get_recent_jobs(self.user_id, days=1)),
                'config': {
                    'max_applications_per_cycle': self.config.automation.max_applications_per_cycle,
                    'search_timeout': self.config.automation.job_search_timeout_seconds,
                    'application_timeout': self.config.automation.application_timeout_seconds
                }
            }
        except Exception as e:
            self.logger.log_error(f"Failed to get automation summary: {e}")
            return {'error': str(e)} 

# Optionally, add a mode to run the orchestrator in enqueue mode
async def run_reconnaissance_phase_enqueue(self, search_criteria: SearchCriteria):
    await self.enqueue_scrape_job(search_criteria)
    return {'status': 'enqueued', 'message': 'Scrape job enqueued', 'criteria': search_criteria.__dict__}

async def run_application_phase_enqueue(self, job_id: str, resume: str = ""):
    await self.enqueue_apply_job(job_id, resume)
    return {'status': 'enqueued', 'message': 'Apply job enqueued', 'job_id': job_id, 'resume': resume} 