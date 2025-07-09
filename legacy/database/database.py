#!/usr/bin/env python3
"""
Database Manager for LinkedIn Job Hunter System
Handles database connections, sessions, and operations
"""

import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime, timedelta
import json

from .models import Base, User, ScrapedJob, SessionData, AutomationLog, JobRecommendation, SystemSettings
from centralized_logging import get_logger

# Configure logging
logger = get_logger("database")

class DatabaseManager:
    """Main database manager class"""
    
    def __init__(self, db_path: str = "linkedin_jobs.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create SQLite database URL
            database_url = f"sqlite:///{self.db_path}"
            
            # Create engine with SQLite-specific settings
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},  # SQLite specific
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create all tables if they don't exist
            Base.metadata.create_all(bind=self.engine)

            # Verify and update table schema
            self._verify_schema()
            
            logger.log_info(f"Database initialized successfully: {self.db_path}")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize database: {e}")
            raise

    def _verify_schema(self):
        """Verify and update the database schema."""
        inspector = inspect(self.engine)
        with self.engine.connect() as connection:
            user_columns = [col['name'] for col in inspector.get_columns('users')]
            
            # Define all expected columns for the User model
            expected_user_columns = {
                'id': 'INTEGER', 'username': 'VARCHAR(255)', 'email': 'VARCHAR(255)',
                'password_hash': 'VARCHAR(255)', 'created_at': 'DATETIME', 'updated_at': 'DATETIME',
                'full_name': 'VARCHAR', 'current_position': 'VARCHAR(255)',
                'skills': 'JSON', 'experience_years': 'INTEGER', 'resume_url': 'VARCHAR(500)'
            }

            for col_name, col_type in expected_user_columns.items():
                if col_name not in user_columns:
                    logger.log_info(f"Adding '{col_name}' column to 'users' table.")
                    # Use execute with text for safety
                    connection.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}'))
            
            # Commit the changes after altering the table
            connection.commit()
            
            # You can add more schema checks here for other tables in the future

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.log_error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.log_error(f"Database connection test failed: {e}")
            return False
    
    # User Management
    def create_user(self, username: str, email: Optional[str] = None, **kwargs) -> Optional[int]:
        """Create a new user and return user_id"""
        try:
            with self.get_session() as session:
                existing_user = session.query(User).filter(User.username == username).first()
                if existing_user:
                    logger.log_warning(f"User already exists: {username}")
                    if isinstance(existing_user.id, int):
                        return existing_user.id
                    else:
                        return None
                user = User(username=username, email=email, **kwargs)
                session.add(user)
                session.flush()
                logger.log_info(f"Created user: {username}")
                if isinstance(user.id, int):
                    return user.id
                else:
                    return None
        except Exception as e:
            logger.log_error(f"Failed to create user: {e}")
            return None
    
    def get_user(self, username: str) -> Optional[int]:
        """Get user_id by username"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                if user and isinstance(user.id, int):
                    return user.id
                else:
                    return None
        except Exception as e:
            logger.log_error(f"Failed to get user: {e}")
            return None
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user profile"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                if not user:
                    logger.log_warning(f"User not found: {username}")
                    return False
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                setattr(user, 'updated_at', datetime.now())
                logger.log_info(f"Updated user: {username}")
                return True
        except Exception as e:
            logger.log_error(f"Failed to update user: {e}")
            return False

    # --- New ScrapedJob Management ---

    def add_scraped_job(self, user_id: int, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Adds or updates a scraped job in the database.
        Prevents duplicates based on job_url.
        """
        try:
            with self.get_session() as session:
                # Check if a job with this URL already exists
                existing_job = session.query(ScrapedJob).filter(ScrapedJob.job_url == job_data.get('job_url')).first()
                if existing_job:
                    # Optionally, you could update the existing job here if needed
                    logger.log_info(f"Job already exists in database: {job_data.get('job_url')}")
                    return existing_job.to_dict()

                # Create new ScrapedJob object
                scraped_job = ScrapedJob(
                    user_id=user_id,
                    job_id=job_data.get('job_id'),
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    job_url=job_data.get('job_url'),
                    description=job_data.get('description'),
                    easy_apply=job_data.get('easy_apply', False),
                    salary_range=job_data.get('salary_range'),
                    job_type=job_data.get('job_type'),
                    experience_level=job_data.get('experience_level'),
                    remote_work=job_data.get('remote_work', False),
                    status='scraped' # Initial status
                )
                session.add(scraped_job)
                session.flush()
                logger.log_info(f"Added new scraped job: {scraped_job.title}")
                return scraped_job.to_dict()
        except Exception as e:
            logger.log_error(f"Failed to add scraped job: {e}")
            return None

    def get_jobs_by_status(self, user_id: int, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs by status - alias for get_scraped_jobs_by_status"""
        return self.get_scraped_jobs_by_status(user_id, status, limit)
    
    def get_scraped_jobs_by_status(self, user_id: int, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get scraped jobs for a user by their status."""
        try:
            with self.get_session() as session:
                jobs = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.status == status
                ).order_by(ScrapedJob.scraped_at.desc()).limit(limit).all()
                return [job.to_dict() for job in jobs]
        except Exception as e:
            logger.log_error(f"Failed to get scraped jobs by status '{status}': {e}")
            return []

    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """Update the status and optionally an error message for a job."""
        try:
            with self.get_session() as session:
                job = session.query(ScrapedJob).filter(ScrapedJob.job_id == job_id).first()
                if not job:
                    logger.log_warning(f"Job not found for status update: {job_id}")
                    return False
                
                job.status = status
                job.status_updated_at = datetime.now()
                if status == 'applied':
                    job.applied_at = datetime.now()
                if error_message:
                    job.error_message = error_message
                
                logger.log_info(f"Updated job {job_id} status to '{status}'")
                return True
        except Exception as e:
            logger.log_error(f"Failed to update job status for {job_id}: {e}")
            return False

    def get_job_by_url(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Check if a job already exists in the database by its URL."""
        try:
            with self.get_session() as session:
                job = session.query(ScrapedJob).filter(ScrapedJob.job_url == job_url).first()
                return job.to_dict() if job else None
        except Exception as e:
            logger.log_error(f"Failed to get job by URL '{job_url}': {e}")
            return None

    # --- Deprecated Job Management ---
    # The methods save_job, get_saved_jobs, apply_to_job, and get_applied_jobs
    # are now deprecated in favor of the new ScrapedJob workflow.
    
    # Session Management
    def create_session(self, user_id: int, session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new session and return as dict"""
        try:
            with self.get_session() as session:
                session_data = SessionData(
                    user_id=user_id,
                    session_id=session_id,
                    **kwargs
                )
                session.add(session_data)
                session.flush()
                logger.log_info(f"Created session: {session_id}")
                return session_data.to_dict()
        except Exception as e:
            logger.log_error(f"Failed to create session: {e}")
            return None
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        try:
            with self.get_session() as session:
                session_data = session.query(SessionData).filter(
                    SessionData.session_id == session_id
                ).first()
                if not session_data:
                    logger.log_warning(f"Session not found: {session_id}")
                    return False
                for key, value in kwargs.items():
                    if hasattr(session_data, key):
                        setattr(session_data, key, value)
                logger.log_info(f"Updated session: {session_id}")
                return True
        except Exception as e:
            logger.log_error(f"Failed to update session: {e}")
            return False
    
    def end_session(self, session_id: str) -> bool:
        """End a session"""
        try:
            with self.get_session() as session:
                session_data = session.query(SessionData).filter(
                    SessionData.session_id == session_id
                ).first()
                if not session_data:
                    logger.log_warning(f"Session not found: {session_id}")
                    return False
                setattr(session_data, 'end_time', datetime.now())
                if getattr(session_data, 'start_time', None):
                    setattr(session_data, 'session_duration', int((session_data.end_time - session_data.start_time).total_seconds()))
                logger.log_info(f"Ended session: {session_id}")
                return True
        except Exception as e:
            logger.log_error(f"Failed to end session: {e}")
            return False
    
    # Logging
    def log_automation_action(self, user_id: int, action: str, success: bool = True, 
                            details: Optional[Dict] = None, error_message: Optional[str] = None,
                            duration_ms: Optional[int] = None, job_id: Optional[str] = None) -> bool:
        """Log an automation action"""
        try:
            with self.get_session() as session:
                log_entry = AutomationLog(
                    user_id=user_id,
                    action=action,
                    details=details,
                    success=success,
                    error_message=error_message,
                    duration_ms=duration_ms,
                    job_id=job_id
                )
                session.add(log_entry)
                logger.log_info(f"Logged action: {action} (success: {success})")
                return True
        except Exception as e:
            logger.log_error(f"Failed to log action: {e}", e)
            return False
    
    def get_automation_logs(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get automation logs for user as list of dicts"""
        try:
            with self.get_session() as session:
                logs = session.query(AutomationLog).filter(
                    AutomationLog.user_id == user_id
                ).order_by(AutomationLog.timestamp.desc()).limit(limit).all()
                return [log.to_dict() for log in logs]
        except Exception as e:
            logger.log_error(f"Failed to get automation logs: {e}", e)
            return []
    
    # System Settings
    def get_setting(self, key: str) -> Optional[str]:
        """Get system setting"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter(
                    SystemSettings.setting_key == key
                ).first()
                return str(setting.setting_value) if setting and setting.setting_value is not None else None
        except Exception as e:
            logger.log_error(f"Failed to get setting: {e}")
            return None
    
    def set_setting(self, key: str, value: str, setting_type: str = 'string', 
                   description: Optional[str] = None) -> bool:
        """Set system setting"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter(
                    SystemSettings.setting_key == key
                ).first()
                if setting:
                    setattr(setting, 'setting_value', value)
                    setattr(setting, 'setting_type', setting_type)
                    if description:
                        setattr(setting, 'description', description)
                else:
                    setting = SystemSettings(
                        setting_key=key,
                        setting_value=value,
                        setting_type=setting_type,
                        description=description
                    )
                    session.add(setting)
                logger.log_info(f"Set setting: {key} = {value}")
                return True
        except Exception as e:
            logger.log_error(f"Failed to set setting: {e}")
            return False
    
    # Database Maintenance
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.log_info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.log_error(f"Failed to backup database: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_session() as session:
                stats = {
                    'users': session.query(User).count(),
                    'saved_jobs': session.query(ScrapedJob).count(), # Changed from SavedJob to ScrapedJob
                    'applied_jobs': session.query(ScrapedJob).filter(ScrapedJob.status == 'applied').count(), # Changed from AppliedJob to ScrapedJob
                    'sessions': session.query(SessionData).count(),
                    'automation_logs': session.query(AutomationLog).count(),
                    'recommendations': session.query(JobRecommendation).count(),
                    'settings': session.query(SystemSettings).count()
                }
                return stats
        except Exception as e:
            logger.log_error(f"Failed to get database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old data (logs, sessions, etc.)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            with self.get_session() as session:
                # Clean old automation logs
                old_logs = session.query(AutomationLog).filter(
                    AutomationLog.timestamp < cutoff_date
                ).delete()
                deleted_count += old_logs
                
                # Clean old sessions
                old_sessions = session.query(SessionData).filter(
                    SessionData.start_time < cutoff_date
                ).delete()
                deleted_count += old_sessions
                
                logger.log_info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            logger.log_error(f"Failed to cleanup old data: {e}")
            return 0
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get User as dict by user_id"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user is not None and hasattr(user, 'to_dict'):
                    return user.to_dict()
                return None
        except Exception as e:
            logger.log_error(f"Failed to get user by id: {e}")
            return None
    
    def get_credentials(self, username: str) -> Optional[dict]:
        """Get credentials for a user (for test endpoint)"""
        try:
            with self.get_session() as session:
                username_setting = session.query(SystemSettings).filter(SystemSettings.setting_key == "linkedin_username").first()
                password_setting = session.query(SystemSettings).filter(SystemSettings.setting_key == "linkedin_password").first()
                if username_setting and password_setting:
                    return {
                        "username": str(username_setting.setting_value),
                        "password": str(password_setting.setting_value)
                    }
                return None
        except Exception as e:
            logger.log_error(f"Failed to get credentials: {e}")
            return None
    
    def save_resume_path(self, username: str, resume_path: str) -> bool:
        """Save resume path to user profile"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                if not user:
                    return False
                setattr(user, 'resume_url', resume_path)
                setattr(user, 'updated_at', datetime.now())
                return True
        except Exception as e:
            logger.log_error(f"Failed to save resume path: {e}")
            return False
    
    # Additional methods for refactored system
    def get_jobs_count_by_status(self, user_id: int, status: str) -> int:
        """Get count of jobs by status for a user"""
        try:
            with self.get_session() as session:
                count = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.status == status
                ).count()
                return count
        except Exception as e:
            logger.log_error(f"Failed to get job count by status: {e}")
            return 0
    
    def get_recent_jobs(self, user_id: int, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently scraped jobs"""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                jobs = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.scraped_at >= cutoff_date
                ).order_by(ScrapedJob.scraped_at.desc()).limit(limit).all()
                
                return [job.to_dict() for job in jobs]
        except Exception as e:
            logger.log_error(f"Failed to get recent jobs: {e}")
            return []
    
    def get_job_by_id(self, user_id: int, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by job_id"""
        try:
            with self.get_session() as session:
                job = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.job_id == job_id
                ).first()
                
                if job:
                    return job.to_dict()
                return None
        except Exception as e:
            logger.log_error(f"Failed to get job by ID: {e}")
            return None
    
    def delete_job(self, user_id: int, job_id: str) -> bool:
        """Delete a job"""
        try:
            with self.get_session() as session:
                job = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.job_id == job_id
                ).first()
                
                if job:
                    session.delete(job)
                    logger.log_info(f"Deleted job: {job_id}")
                    return True
                else:
                    logger.log_warning(f"Job not found for deletion: {job_id}")
                    return False
        except Exception as e:
            logger.log_error(f"Failed to delete job: {e}")
            return False
    
    def update_job_status_new(self, user_id: int, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update job status and other fields (refactored version)"""
        try:
            with self.get_session() as session:
                job = session.query(ScrapedJob).filter(
                    ScrapedJob.user_id == user_id,
                    ScrapedJob.job_id == job_id
                ).first()
                
                if job:
                    for key, value in update_data.items():
                        if hasattr(job, key):
                            setattr(job, key, value)
                    job.updated_at = datetime.now()
                    logger.log_info(f"Updated job {job_id} status")
                    return True
                else:
                    logger.log_warning(f"Job not found for update: {job_id}")
                    return False
        except Exception as e:
            logger.log_error(f"Failed to update job status: {e}")
            return False 