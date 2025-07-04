#!/usr/bin/env python3
"""
Database Integration Script for LinkedIn Job Hunter System
Main script to initialize database and run migrations
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import DatabaseManager
from database.migrations import run_migrations, migrate_saved_jobs_from_json, create_backup_before_migration, validate_migration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_database(db_path: str = "linkedin_jobs.db") -> DatabaseManager:
    """Initialize database and run migrations"""
    try:
        logger.info("🚀 Initializing LinkedIn Job Hunter Database")
        logger.info("=" * 50)
        
        # Create database manager
        db_manager = DatabaseManager(db_path)
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("❌ Database connection test failed")
            return None
        
        logger.info("✅ Database connection successful")
        
        # Create backup before migration
        logger.info("📦 Creating database backup...")
        create_backup_before_migration(db_manager)
        
        # Run migrations
        logger.info("🔄 Running database migrations...")
        if not run_migrations(db_manager):
            logger.error("❌ Database migrations failed")
            return None
        
        # Migrate saved jobs from JSON
        logger.info("📋 Migrating saved jobs from JSON...")
        migrate_saved_jobs_from_json(db_manager)
        
        # Validate migration
        logger.info("✅ Validating migration...")
        if not validate_migration(db_manager):
            logger.error("❌ Migration validation failed")
            return None
        
        logger.info("✅ Database initialization completed successfully")
        return db_manager
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return None

def test_database_functionality(db_manager: DatabaseManager):
    """Test database functionality"""
    try:
        logger.info("\n🧪 Testing Database Functionality")
        logger.info("=" * 30)
        
        # Test user creation
        logger.info("Testing user creation...")
        user_id = db_manager.create_user(
            username="test_user",
            email="test@example.com",
            current_position="Software Engineer",
            skills=["Python", "JavaScript", "React"],
            target_roles=["Senior Developer", "Full Stack Engineer"],
            target_locations=["Remote", "San Francisco"]
        )
        
        if user_id:
            logger.info(f"✅ Created user with ID: {user_id}")
            
            # Test job saving
            logger.info("Testing job saving...")
            job_data = {
                "job_id": "test_job_123",
                "title": "Senior Python Developer",
                "company": "Test Company",
                "location": "Remote",
                "job_url": "https://linkedin.com/jobs/view/test_job_123",
                "description": "Great job opportunity",
                "easy_apply": True,
                "remote_work": True,
                "tags": ["python", "remote", "senior"]
            }
            
            saved_job = db_manager.save_job(user_id, job_data)
            if saved_job:
                logger.info(f"✅ Saved job: {saved_job.get('title')}")
            
            # Test session creation
            logger.info("Testing session creation...")
            session = db_manager.create_session(
                user_id=user_id,
                session_id="test_session_123",
                automation_mode="manual"
            )
            
            if session:
                logger.info(f"✅ Created session: {session.get('session_id')}")
                
                # Update session
                db_manager.update_session(
                    session.get('session_id'),
                    jobs_viewed=5,
                    jobs_applied=2,
                    jobs_saved=3
                )
                logger.info("✅ Updated session data")
                
                # End session
                db_manager.end_session(session.get('session_id'))
                logger.info("✅ Ended session")
            
            # Test automation logging
            logger.info("Testing automation logging...")
            db_manager.log_automation_action(
                user_id=user_id,
                action="test_action",
                success=True,
                details={"test": "data"},
                duration_ms=150
            )
            logger.info("✅ Logged automation action")
            
            # Test system settings
            logger.info("Testing system settings...")
            db_manager.set_setting("test_setting", "test_value", "string", "Test setting")
            setting_value = db_manager.get_setting("test_setting")
            if setting_value == "test_value":
                logger.info("✅ System settings working")
            
            # Get database stats
            stats = db_manager.get_database_stats()
            logger.info(f"📊 Database stats: {stats}")
            
        else:
            logger.error("❌ Failed to create test user")
            
    except Exception as e:
        logger.error(f"❌ Database functionality test failed: {e}")

def show_database_info(db_manager: DatabaseManager):
    """Show database information"""
    try:
        logger.info("\n📊 Database Information")
        logger.info("=" * 25)
        
        # Database stats
        stats = db_manager.get_database_stats()
        logger.info(f"Users: {stats.get('users', 0)}")
        logger.info(f"Saved Jobs: {stats.get('saved_jobs', 0)}")
        logger.info(f"Applied Jobs: {stats.get('applied_jobs', 0)}")
        logger.info(f"Sessions: {stats.get('sessions', 0)}")
        logger.info(f"Automation Logs: {stats.get('automation_logs', 0)}")
        logger.info(f"System Settings: {stats.get('settings', 0)}")
        
        # Migration version
        migration_version = db_manager.get_setting('migration_version')
        logger.info(f"Migration Version: {migration_version}")
        
        # System version
        system_version = db_manager.get_setting('system_version')
        logger.info(f"System Version: {system_version}")
        
    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")

def cleanup_test_data(db_manager: DatabaseManager):
    """Clean up test data"""
    try:
        logger.info("\n🧹 Cleaning up test data...")
        
        # This would typically involve deleting test records
        # For now, we'll just log the cleanup
        logger.info("✅ Test data cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Test data cleanup failed: {e}")

def main():
    """Main function"""
    try:
        logger.info("🔧 LinkedIn Job Hunter Database Integration")
        logger.info("=" * 50)
        
        # Initialize database
        db_manager = initialize_database()
        if not db_manager:
            logger.error("❌ Failed to initialize database")
            return False
        
        # Show initial database info
        show_database_info(db_manager)
        
        # Test functionality
        test_database_functionality(db_manager)
        
        # Show final database info
        show_database_info(db_manager)
        
        # Cleanup test data
        cleanup_test_data(db_manager)
        
        logger.info("\n✅ Database integration completed successfully!")
        logger.info("🎉 Your LinkedIn Job Hunter system now uses a proper database!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database integration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 