"""
Job repository for database operations with clean abstraction.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.models.job_data import JobData, JobStatus
from legacy.database.database import DatabaseManager


class JobRepository:
    """Repository for job data operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def save_scraped_job(self, user_id: int, job_data: JobData) -> bool:
        """
        Save a scraped job to the database.
        
        Args:
            user_id: ID of the user who owns this job
            job_data: JobData object to save
            
        Returns:
            True if saved successfully, False if already exists
        """
        try:
            # Convert JobData to database format (matching actual ScrapedJob schema)
            db_job_data = {
                'job_id': job_data.job_id,
                'title': job_data.title,
                'company': job_data.company,
                'location': job_data.location,
                'job_url': job_data.job_url,  # Database uses 'job_url'
                'description': job_data.description,
                'status': job_data.status.value,
                'easy_apply': job_data.easy_apply,
                'salary_range': job_data.salary_range,
                'job_type': job_data.job_type,
                'experience_level': job_data.experience_level,
                'remote_work': job_data.remote_work
            }
            
            success = self.db.add_scraped_job(user_id, db_job_data)
            if success:
                self.logger.info(f"Saved job: {job_data.job_id} - {job_data.title}")
            else:
                self.logger.debug(f"Job already exists: {job_data.job_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to save job {job_data.job_id}: {e}")
            return False
    
    def get_jobs_by_status(self, user_id: int, status: JobStatus, limit: int = 50) -> List[JobData]:
        """
        Get jobs by status for a user.
        
        Args:
            user_id: ID of the user
            status: Job status to filter by
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobData objects
        """
        try:
            # Get jobs from database
            raw_jobs = self.db.get_jobs_by_status(user_id, status.value, limit)
            
            # Convert to JobData objects
            jobs = []
            for raw_job in raw_jobs:
                try:
                    job_data = self._convert_db_job(raw_job)
                    jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Failed to convert job data: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(jobs)} jobs with status {status.value}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get jobs by status {status.value}: {e}")
            return []
    
    def update_job_status(self, user_id: int, job_id: str, status: JobStatus, error_message: Optional[str] = None) -> bool:
        """
        Update job status.
        
        Args:
            user_id: ID of the user
            job_id: Job ID to update
            status: New status
            error_message: Optional error message if status is FAILED
            
        Returns:
            True if updated successfully
        """
        try:
            # Prepare update data
            update_data = {
                'status': status.value,
                'updated_at': datetime.now()
            }
            
            if error_message:
                update_data['error_message'] = error_message
            
            success = self.db.update_job_status_new(user_id, job_id, update_data)
            if success:
                self.logger.info(f"Updated job {job_id} status to {status.value}")
            else:
                self.logger.warning(f"Failed to update job {job_id} status")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update job {job_id} status: {e}")
            return False
    
    def get_job_by_id(self, user_id: int, job_id: str) -> Optional[JobData]:
        """
        Get a specific job by ID.
        
        Args:
            user_id: ID of the user
            job_id: Job ID to retrieve
            
        Returns:
            JobData object or None if not found
        """
        try:
            raw_job = self.db.get_job_by_id(user_id, job_id)
            if raw_job:
                return self._convert_db_job(raw_job)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def get_jobs_count_by_status(self, user_id: int, status: JobStatus) -> int:
        """
        Get count of jobs by status.
        
        Args:
            user_id: ID of the user
            status: Job status to count
            
        Returns:
            Number of jobs with the given status
        """
        try:
            count = self.db.get_jobs_count_by_status(user_id, status.value)
            return count
        except Exception as e:
            self.logger.error(f"Failed to get job count for status {status.value}: {e}")
            return 0
    
    def get_recent_jobs(self, user_id: int, days: int = 7, limit: int = 50) -> List[JobData]:
        """
        Get recently scraped jobs.
        
        Args:
            user_id: ID of the user
            days: Number of days to look back
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobData objects
        """
        try:
            raw_jobs = self.db.get_recent_jobs(user_id, days, limit)
            
            jobs = []
            for raw_job in raw_jobs:
                try:
                    job_data = self._convert_db_job(raw_job)
                    jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Failed to convert job data: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get recent jobs: {e}")
            return []
    
    def delete_job(self, user_id: int, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            user_id: ID of the user
            job_id: Job ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            success = self.db.delete_job(user_id, job_id)
            if success:
                self.logger.info(f"Deleted job: {job_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def _convert_db_job(self, raw_job: Dict[str, Any]) -> JobData:
        """Convert database job record to JobData object"""
        try:
            # Handle datetime fields - database uses scraped_at
            scraped_at = raw_job.get('scraped_at')
            if isinstance(scraped_at, str):
                scraped_at = datetime.fromisoformat(scraped_at)
            elif scraped_at is None:
                scraped_at = datetime.now()
            
            # No posted_date in current schema
            posted_date = None
            
            # Handle status
            status_str = raw_job.get('status', JobStatus.SCRAPED.value)
            status = JobStatus(status_str) if status_str else JobStatus.SCRAPED
            
            # Handle tags - not stored in current schema
            tags = []
            
            return JobData(
                job_id=raw_job['job_id'],
                title=raw_job['title'],
                company=raw_job['company'],
                location=raw_job.get('location', ''),
                job_url=raw_job.get('job_url', ''),  # Database uses 'job_url'
                description=raw_job.get('description', ''),
                salary_range=raw_job.get('salary_range'),
                job_type=raw_job.get('job_type'),
                experience_level=raw_job.get('experience_level'),
                easy_apply=raw_job.get('easy_apply', False),
                remote_work=raw_job.get('remote_work', False),
                posted_date=posted_date,
                scraped_at=scraped_at,
                status=status,
                source='linkedin',
                tags=tags,
                notes=''  # Not stored in current schema
            )
            
        except Exception as e:
            raise ValueError(f"Failed to convert database job record: {e}") from e 