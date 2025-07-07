#!/usr/bin/env python3
"""
Database Manager for LinkedIn Job Hunter System
Handles database connections, sessions, and operations
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Generator
from datetime import datetime, timedelta
import json

from .models import Base, User, SavedJob, AppliedJob, SessionData, AutomationLog, JobRecommendation, SystemSettings
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
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.log_info(f"Database initialized successfully: {self.db_path}")
            
        except Exception as e:
            logger.log_error(f"Failed to initialize database: {e}")
            raise
    
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
    
    # Job Management
    def save_job(self, user_id: int, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a job for later review and return as dict"""
        try:
            with self.get_session() as session:
                existing_job = session.query(SavedJob).filter(
                    SavedJob.user_id == user_id,
                    SavedJob.job_id == job_data.get('job_id')
                ).first()
                if existing_job:
                    logger.log_info(f"Job already saved: {job_data.get('job_id')}")
                    return existing_job.to_dict()
                saved_job = SavedJob(
                    user_id=user_id,
                    job_id=job_data.get('job_id'),
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    job_url=job_data.get('job_url'),
                    description=job_data.get('description'),
                    salary_range=job_data.get('salary_range'),
                    job_type=job_data.get('job_type'),
                    experience_level=job_data.get('experience_level'),
                    easy_apply=job_data.get('easy_apply', False),
                    remote_work=job_data.get('remote_work', False),
                    notes=job_data.get('notes'),
                    tags=job_data.get('tags', [])
                )
                session.add(saved_job)
                session.flush()
                logger.log_info(f"Saved job: {job_data.get('title')}")
                return saved_job.to_dict()
        except Exception as e:
            logger.log_error(f"Failed to save job: {e}")
            return None
    
    def get_saved_jobs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get saved jobs for user as list of dicts"""
        try:
            with self.get_session() as session:
                jobs = session.query(SavedJob).filter(
                    SavedJob.user_id == user_id
                ).order_by(SavedJob.saved_at.desc()).limit(limit).all()
                return [job.to_dict() for job in jobs]
        except Exception as e:
            logger.log_error(f"Failed to get saved jobs: {e}")
            return []
    
    def apply_to_job(self, user_id: int, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Record a job application and return as dict"""
        try:
            with self.get_session() as session:
                existing_application = session.query(AppliedJob).filter(
                    AppliedJob.user_id == user_id,
                    AppliedJob.job_id == job_data.get('job_id')
                ).first()
                if existing_application:
                    logger.log_info(f"Already applied to job: {job_data.get('job_id')}")
                    return existing_application.to_dict()
                applied_job = AppliedJob(
                    user_id=user_id,
                    job_id=job_data.get('job_id'),
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    job_url=job_data.get('job_url'),
                    cover_letter=job_data.get('cover_letter'),
                    resume_used=job_data.get('resume_used'),
                    notes=job_data.get('notes')
                )
                session.add(applied_job)
                session.flush()
                logger.log_info(f"Applied to job: {job_data.get('title')}")
                return applied_job.to_dict()
        except Exception as e:
            logger.log_error(f"Failed to apply to job: {e}")
            return None
    
    def get_applied_jobs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get applied jobs for user as list of dicts"""
        try:
            with self.get_session() as session:
                jobs = session.query(AppliedJob).filter(
                    AppliedJob.user_id == user_id
                ).order_by(AppliedJob.applied_at.desc()).limit(limit).all()
                return [job.to_dict() for job in jobs]
        except Exception as e:
            logger.log_error(f"Failed to get applied jobs: {e}")
            return []
    
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
                    'saved_jobs': session.query(SavedJob).count(),
                    'applied_jobs': session.query(AppliedJob).count(),
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