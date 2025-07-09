#!/usr/bin/env python3
"""
Database Migrations for LinkedIn Job Hunter System
Handles database schema migrations and data migration from JSON files
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import inspect, text

if TYPE_CHECKING:
    from .database import DatabaseManager

from .models import User, SessionData, SystemSettings
from .migrations.m008_add_password_hash_to_user import add_password_hash_to_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations(db_manager: DatabaseManager) -> bool:
    MIGRATIONS: Dict[str, Any] = {
        '001_initial_setup': None,  # Placeholder for initial schema setup
        '002_add_user_profile_fields': add_user_profile_fields,
        '003_add_job_recommendations': add_job_recommendations,
        '004_add_system_settings': add_system_settings,
        '005_update_job_models': update_job_models,
        '006_add_session_data': add_session_data,
        '007_refine_automation_logs': refine_automation_logs,
        '008_add_password_hash_to_user': add_password_hash_to_user,
    }

    try:
        with db_manager.engine.connect() as connection:
            inspector = inspect(db_manager.engine)
            
            # Simplified migration tracking: just check for a 'migrations' table
            if 'migrations' not in inspector.get_table_names():
                logger.info("Creating migrations table.")
                connection.execute(text("""
                    CREATE TABLE migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))

            # Get completed migrations
            completed_migrations = {
                row[0] for row in connection.execute(text("SELECT name FROM migrations")).fetchall()
            }

            for name, func in sorted(MIGRATIONS.items()):
                if name not in completed_migrations:
                    logger.info(f"Running migration: {name}")
                    if func:
                        func(db_manager.engine)
                    
                    connection.execute(
                        text("INSERT INTO migrations (name) VALUES (:name)"),
                        {'name': name}
                    )
                    logger.info(f"Migration {name} completed and recorded.")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False

def migrate_v1_initial_schema(db_manager: DatabaseManager) -> bool:
    """Initial schema migration - tables are created automatically by SQLAlchemy"""
    try:
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return False
        
        # Create default system settings
        default_settings = [
            ('system_version', '1.0.0', 'string', 'Current system version'),
            ('database_version', '1', 'string', 'Current database schema version'),
            ('auto_backup_enabled', 'true', 'boolean', 'Enable automatic database backups'),
            ('backup_retention_days', '30', 'integer', 'Number of days to keep backups'),
            ('log_retention_days', '90', 'integer', 'Number of days to keep automation logs'),
            ('max_saved_jobs', '1000', 'integer', 'Maximum number of saved jobs per user'),
            ('max_applied_jobs', '500', 'integer', 'Maximum number of applied jobs per user')
        ]
        
        for key, value, setting_type, description in default_settings:
            db_manager.set_setting(key, value, setting_type, description)
        
        logger.info("Initial schema migration completed")
        return True
        
    except Exception as e:
        logger.error(f"Initial schema migration failed: {e}")
        return False

def migrate_v2_user_profiles(db_manager: DatabaseManager) -> bool:
    """Migrate user profiles from JSON files"""
    try:
        # Check if user_profile.json exists
        profile_file = Path('user_profile.json')
        if not profile_file.exists():
            logger.info("No user_profile.json found, skipping user profile migration")
            return True
        
        # Load user profile data
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        # Create or update user
        username = profile_data.get('username', 'default_user')
        user = db_manager.get_user(username)
        
        if not user:
            # Create new user
            user = db_manager.create_user(
                username=username,
                email=profile_data.get('email'),
                current_position=profile_data.get('current_position'),
                skills=profile_data.get('skills', []),
                target_roles=profile_data.get('target_roles', []),
                target_locations=profile_data.get('target_locations', []),
                experience_years=profile_data.get('experience_years'),
                resume_url=profile_data.get('resume_url')
            )
        else:
            # Update existing user
            db_manager.update_user(
                username=username,
                current_position=profile_data.get('current_position'),
                skills=profile_data.get('skills', []),
                target_roles=profile_data.get('target_roles', []),
                target_locations=profile_data.get('target_locations', []),
                experience_years=profile_data.get('experience_years'),
                resume_url=profile_data.get('resume_url')
            )
        
        if user:
            logger.info(f"Migrated user profile for: {username}")
            return True
        else:
            logger.error("Failed to create/update user during migration")
            return False
        
    except Exception as e:
        logger.error(f"User profile migration failed: {e}")
        return False

def migrate_v3_session_data(db_manager: DatabaseManager) -> bool:
    """Migrate session data from JSON files"""
    try:
        # Check if session_data.json exists
        session_file = Path('session_data.json')
        if not session_file.exists():
            logger.info("No session_data.json found, skipping session data migration")
            return True
        
        # Load session data
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Get default user_id
        user_id = db_manager.get_user('default_user')
        if not user_id:
            db_manager.create_user(username='default_user')
            user_id = db_manager.get_user('default_user')
        if not user_id:
            logger.error("Failed to create user for session migration")
            return False
        
        # Create session record
        session_stats = session_data.get('session_stats', {})
        session_id = f"migrated_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_record = db_manager.create_session(
            user_id=user_id,
            session_id=session_id,
            jobs_viewed=session_stats.get('jobs_viewed', 0),
            jobs_applied=session_stats.get('jobs_applied', 0),
            jobs_saved=session_stats.get('jobs_saved', 0),
            start_time=datetime.fromisoformat(session_stats.get('start_time', datetime.now().isoformat())),
            automation_mode='manual'
        )
        
        if session_record:
            logger.info("Migrated session data successfully")
            return True
        else:
            logger.error("Failed to create session record during migration")
            return False
        
    except Exception as e:
        logger.error(f"Session data migration failed: {e}")
        return False

def migrate_v4_automation_logs(db_manager: DatabaseManager) -> bool:
    """Migrate automation logs and create initial log entries"""
    try:
        # Get default user_id
        user_id = db_manager.get_user('default_user')
        if not user_id:
            db_manager.create_user(username='default_user')
            user_id = db_manager.get_user('default_user')
        if not user_id:
            logger.warning("No default user found for automation logs migration")
            return True
        
        # Create initial automation log entry
        db_manager.log_automation_action(
            user_id=user_id,
            action='database_migration',
            success=True,
            details={'migration_version': '4', 'description': 'Automation logs migration'},
            duration_ms=100
        )
        
        logger.info("Automation logs migration completed")
        return True
        
    except Exception as e:
        logger.error(f"Automation logs migration failed: {e}")
        return False

def migrate_v5_system_settings(db_manager: DatabaseManager) -> bool:
    """Migrate system settings and create additional configuration"""
    try:
        # Add performance monitoring settings
        performance_settings = [
            ('performance_monitoring_enabled', 'true', 'boolean', 'Enable performance monitoring'),
            ('monitoring_interval_seconds', '30', 'integer', 'Performance monitoring interval'),
            ('alert_cpu_threshold', '80', 'integer', 'CPU usage alert threshold (%)'),
            ('alert_memory_threshold', '85', 'integer', 'Memory usage alert threshold (%)'),
            ('alert_disk_threshold', '90', 'integer', 'Disk usage alert threshold (%)'),
            ('cache_enabled', 'true', 'boolean', 'Enable API response caching'),
            ('cache_duration_seconds', '300', 'integer', 'Cache duration in seconds'),
            ('rate_limiting_enabled', 'true', 'boolean', 'Enable rate limiting'),
            ('max_requests_per_minute', '60', 'integer', 'Maximum requests per minute')
        ]
        
        for key, value, setting_type, description in performance_settings:
            db_manager.set_setting(key, value, setting_type, description)
        
        logger.info("System settings migration completed")
        return True
        
    except Exception as e:
        logger.error(f"System settings migration failed: {e}")
        return False

def migrate_saved_jobs_from_json(db_manager: DatabaseManager, json_file_path: str = 'saved_jobs.json') -> bool:
    """Migrate saved jobs from JSON file to database"""
    try:
        # Check if saved_jobs.json exists
        jobs_file = Path(json_file_path)
        if not jobs_file.exists():
            logger.info(f"No {json_file_path} found, skipping saved jobs migration")
            return True
        
        # Load saved jobs data
        with open(jobs_file, 'r', encoding='utf-8') as f:
            saved_jobs = json.load(f)
        
        # Get default user_id
        user_id = db_manager.get_user('default_user')
        if not user_id:
            db_manager.create_user(username='default_user')
            user_id = db_manager.get_user('default_user')
        if not user_id:
            logger.error("Failed to create user for saved jobs migration")
            return False
        
        # Migrate each saved job
        migrated_count = 0
        for job_data in saved_jobs:
            # Extract job ID from URL if not present
            if 'job_id' not in job_data and 'job_url' in job_data:
                job_url = job_data['job_url']
                # Try to extract job ID from LinkedIn URL
                if '/jobs/view/' in job_url:
                    job_id = job_url.split('/jobs/view/')[-1].split('?')[0]
                    job_data['job_id'] = job_id
                else:
                    job_data['job_id'] = f"migrated_{migrated_count}"
            
            # Set default values for missing fields
            job_data.setdefault('job_id', f"migrated_{migrated_count}")
            job_data.setdefault('easy_apply', False)
            job_data.setdefault('remote_work', False)
            job_data.setdefault('tags', [])
            
            # Convert date_saved to saved_at if present
            if 'date_saved' in job_data:
                try:
                    saved_date = datetime.fromisoformat(job_data['date_saved'].replace('Z', '+00:00'))
                    job_data['saved_at'] = saved_date
                except:
                    job_data['saved_at'] = datetime.now()
            
            # Save job to database
            saved_job = db_manager.save_job(user_id, job_data)
            if saved_job:
                migrated_count += 1
        
        logger.info(f"Migrated {migrated_count} saved jobs successfully")
        return True
        
    except Exception as e:
        logger.error(f"Saved jobs migration failed: {e}")
        return False

def create_backup_before_migration(db_manager: DatabaseManager) -> bool:
    """Create a backup of the database before running migrations"""
    try:
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"linkedin_jobs_backup_{timestamp}.db"
        
        if db_manager.backup_database(str(backup_path)):
            logger.info(f"Database backup created: {backup_path}")
            return True
        else:
            logger.error("Failed to create database backup")
            return False
            
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return False

def validate_migration(db_manager: DatabaseManager) -> bool:
    """Validate that migration was successful"""
    try:
        # Check database connection
        if not db_manager.test_connection():
            logger.error("Database connection validation failed")
            return False
        
        # Check that tables exist and have data
        stats = db_manager.get_database_stats()
        logger.info(f"Database stats after migration: {stats}")
        
        # Check that system settings were created
        version = db_manager.get_setting('migration_version')
        if not version:
            logger.error("Migration version not set")
            return False
        
        logger.info(f"Migration validation successful. Version: {version}")
        return True
        
    except Exception as e:
        logger.error(f"Migration validation failed: {e}")
        return False 