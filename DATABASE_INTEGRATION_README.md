# Database Integration for LinkedIn Job Hunter

## 🎯 Overview

This database integration replaces the file-based storage system with a proper SQLite database using SQLAlchemy ORM. The system provides:

- **Structured Data Storage**: All data is now stored in a relational database
- **Data Migration**: Automatic migration from existing JSON files
- **Enhanced API**: New endpoints for database operations
- **Analytics**: Built-in analytics and logging
- **Backup & Recovery**: Database backup and maintenance features

## 🗄️ Database Schema

### Core Tables

#### Users
- **id**: Primary key
- **username**: Unique username
- **email**: User email
- **current_position**: Current job title
- **skills**: JSON array of skills
- **target_roles**: JSON array of target job roles
- **target_locations**: JSON array of target locations
- **experience_years**: Years of experience
- **resume_url**: URL to resume
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

#### Saved Jobs
- **id**: Primary key
- **user_id**: Foreign key to users
- **job_id**: LinkedIn job ID
- **title**: Job title
- **company**: Company name
- **location**: Job location
- **job_url**: LinkedIn job URL
- **description**: Job description
- **salary_range**: Salary information
- **job_type**: Full-time, Part-time, Contract
- **experience_level**: Entry, Mid, Senior
- **easy_apply**: Boolean for Easy Apply
- **remote_work**: Boolean for remote work
- **saved_at**: When job was saved
- **notes**: User notes
- **tags**: JSON array of custom tags

#### Applied Jobs
- **id**: Primary key
- **user_id**: Foreign key to users
- **job_id**: LinkedIn job ID
- **title**: Job title
- **company**: Company name
- **location**: Job location
- **job_url**: LinkedIn job URL
- **applied_at**: Application timestamp
- **application_status**: applied, viewed, interviewing, rejected, accepted
- **cover_letter**: Cover letter text
- **resume_used**: Resume file path
- **follow_up_date**: Follow-up reminder date
- **notes**: Application notes
- **response_received**: Boolean for response
- **response_date**: Response timestamp

#### Session Data
- **id**: Primary key
- **user_id**: Foreign key to users
- **session_id**: Unique session identifier
- **start_time**: Session start timestamp
- **end_time**: Session end timestamp
- **jobs_viewed**: Number of jobs viewed
- **jobs_applied**: Number of jobs applied to
- **jobs_saved**: Number of jobs saved
- **errors_encountered**: Number of errors
- **session_duration**: Duration in seconds
- **goals_processed**: Number of goals processed
- **automation_mode**: manual, automated, hybrid

#### Automation Logs
- **id**: Primary key
- **user_id**: Foreign key to users
- **timestamp**: Action timestamp
- **action**: Action type (login, search, apply, save, error)
- **details**: JSON details of the action
- **success**: Boolean success flag
- **error_message**: Error message if failed
- **duration_ms**: Action duration in milliseconds
- **job_id**: Related job ID if applicable

#### Job Recommendations
- **id**: Primary key
- **user_id**: Foreign key to users
- **job_id**: LinkedIn job ID
- **title**: Job title
- **company**: Company name
- **location**: Job location
- **job_url**: LinkedIn job URL
- **recommendation_score**: 1-100 score
- **reasoning**: AI reasoning for recommendation
- **skills_match**: JSON array of matching skills
- **created_at**: Recommendation timestamp
- **viewed**: Boolean for viewed status
- **applied**: Boolean for applied status

#### System Settings
- **id**: Primary key
- **setting_key**: Setting name
- **setting_value**: Setting value
- **setting_type**: string, integer, boolean, json
- **description**: Setting description
- **updated_at**: Last update timestamp

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install sqlalchemy alembic
```

### 2. Initialize Database

```bash
python database_integration.py
```

This will:
- Create the SQLite database
- Run all migrations
- Migrate existing JSON data
- Test the database functionality

### 3. Start API with Database

```bash
python api_bridge_with_database.py
```

### 4. Windows Users

Use the provided batch script:

```bash
start_database_integration.bat
```

## 📊 Database Operations

### User Management

```python
from database.database import DatabaseManager

# Initialize database
db = DatabaseManager("linkedin_jobs.db")

# Create user
user = db.create_user(
    username="john_doe",
    email="john@example.com",
    current_position="Software Engineer",
    skills=["Python", "JavaScript", "React"],
    target_roles=["Senior Developer", "Full Stack Engineer"],
    target_locations=["Remote", "San Francisco"]
)

# Get user
user = db.get_user("john_doe")

# Update user
db.update_user(
    username="john_doe",
    current_position="Senior Software Engineer",
    skills=["Python", "JavaScript", "React", "Node.js"]
)
```

### Job Management

```python
# Save a job
job_data = {
    "job_id": "linkedin_job_123",
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "job_url": "https://linkedin.com/jobs/view/123",
    "description": "Great opportunity...",
    "easy_apply": True,
    "remote_work": True,
    "tags": ["python", "remote", "senior"]
}

saved_job = db.save_job(user.id, job_data)

# Apply to a job
applied_job = db.apply_to_job(user.id, job_data)

# Get saved jobs
saved_jobs = db.get_saved_jobs(user.id, limit=50)

# Get applied jobs
applied_jobs = db.get_applied_jobs(user.id, limit=50)
```

### Session Management

```python
# Start session
session = db.create_session(
    user_id=user.id,
    session_id="session_123",
    automation_mode="manual"
)

# Update session
db.update_session(
    session_id="session_123",
    jobs_viewed=5,
    jobs_applied=2,
    jobs_saved=3
)

# End session
db.end_session("session_123")
```

### Analytics and Logging

```python
# Log automation action
db.log_automation_action(
    user_id=user.id,
    action="job_search",
    success=True,
    details={"query": "python developer", "count": 10},
    duration_ms=1500
)

# Get automation logs
logs = db.get_automation_logs(user.id, limit=100)

# Get database statistics
stats = db.get_database_stats()
```

### System Settings

```python
# Set setting
db.set_setting("cache_enabled", "true", "boolean", "Enable caching")

# Get setting
cache_enabled = db.get_setting("cache_enabled")
```

## 🔄 Data Migration

The system automatically migrates existing data from JSON files:

### Migration Process

1. **User Profiles**: Migrates `user_profile.json`
2. **Saved Jobs**: Migrates `saved_jobs.json`
3. **Session Data**: Migrates `session_data.json`
4. **System Settings**: Creates default settings

### Migration Files

- `database/migrations.py`: Migration logic
- `database_integration.py`: Main migration script

### Manual Migration

```python
from database.migrations import migrate_saved_jobs_from_json

# Migrate saved jobs from specific file
migrate_saved_jobs_from_json(db_manager, "custom_saved_jobs.json")
```

## 🛠️ API Endpoints

### New Database-Enabled Endpoints

#### User Management
- `POST /api/user/profile` - Update user profile
- `GET /api/user/profile` - Get user profile

#### Job Management
- `POST /api/save_job` - Save job with full details
- `POST /api/apply_job` - Apply to job with tracking
- `GET /api/saved_jobs` - Get saved jobs
- `GET /api/applied_jobs` - Get applied jobs

#### Session Management
- `POST /api/session/start` - Start new session
- `POST /api/session/end` - End session
- `POST /api/session/update` - Update session data

#### Analytics
- `GET /api/analytics/logs` - Get automation logs
- `GET /api/analytics/stats` - Get user statistics

#### Database Management
- `GET /api/database/stats` - Get database statistics
- `POST /api/database/backup` - Create database backup
- `POST /api/database/cleanup` - Clean up old data

#### System Settings
- `GET /api/settings/{key}` - Get system setting
- `POST /api/settings/{key}` - Set system setting

### Legacy Endpoints

For backward compatibility, these endpoints still work:
- `POST /api/update_credentials` - Update credentials
- `POST /api/search_jobs` - Search jobs (enhanced)
- `GET /api/health` - Health check (enhanced)

## 📈 Analytics Features

### Built-in Analytics

The database provides comprehensive analytics:

```python
# Get user statistics
stats = {
    "total_saved_jobs": 45,
    "total_applied_jobs": 23,
    "total_automation_actions": 156,
    "successful_actions": 142,
    "failed_actions": 14,
    "recent_activity": {
        "last_7_days": 25,
        "last_30_days": 89
    }
}
```

### Automation Logs

Track all automation activities:

```python
# Example log entry
{
    "id": 1,
    "user_id": 1,
    "timestamp": "2025-01-15T10:30:00",
    "action": "job_search",
    "details": {"query": "python developer", "count": 10},
    "success": true,
    "duration_ms": 1500,
    "job_id": null
}
```

## 🔧 Database Maintenance

### Backup

```python
# Create backup
success = db.backup_database("backups/linkedin_jobs_backup_20250115.db")
```

### Cleanup

```python
# Clean up old data (default: 30 days)
deleted_count = db.cleanup_old_data(days=30)
```

### Statistics

```python
# Get database statistics
stats = db.get_database_stats()
# Returns: {"users": 1, "saved_jobs": 45, "applied_jobs": 23, ...}
```

## 🚨 Error Handling

The database system includes comprehensive error handling:

### Connection Errors
- Automatic retry logic
- Graceful degradation
- Detailed error logging

### Migration Errors
- Rollback capability
- Backup before migration
- Validation after migration

### Data Integrity
- Foreign key constraints
- Data validation
- Transaction management

## 🔒 Security Features

### Data Protection
- SQL injection prevention
- Input validation
- Secure session management

### Backup Security
- Encrypted backups (optional)
- Access control
- Audit logging

## 📝 Configuration

### Environment Variables

```bash
# Database configuration
DATABASE_PATH=linkedin_jobs.db
DATABASE_BACKUP_DIR=backups
DATABASE_CLEANUP_DAYS=30

# Performance settings
CACHE_DURATION=300
MAX_SAVED_JOBS=1000
MAX_APPLIED_JOBS=500
```

### System Settings

Key system settings stored in database:

```python
default_settings = [
    ("system_version", "2.0.0"),
    ("database_version", "1"),
    ("auto_backup_enabled", "true"),
    ("backup_retention_days", "30"),
    ("log_retention_days", "90"),
    ("cache_enabled", "true"),
    ("cache_duration_seconds", "300"),
    ("rate_limiting_enabled", "true"),
    ("max_requests_per_minute", "60")
]
```

## 🧪 Testing

### Database Tests

```bash
# Run database integration tests
python database_integration.py

# Test specific functionality
python -c "
from database.database import DatabaseManager
db = DatabaseManager('test.db')
print('Database test successful')
"
```

### API Tests

```bash
# Test API endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api/database/stats
```

## 🔄 Migration from File-Based System

### Before Migration

Your existing system uses:
- `user_profile.json` - User data
- `saved_jobs.json` - Saved jobs
- `session_data.json` - Session statistics

### After Migration

All data is stored in SQLite database:
- `linkedin_jobs.db` - Main database file
- `backups/` - Database backups
- Enhanced API endpoints

### Migration Benefits

1. **Better Performance**: Faster queries and data access
2. **Data Integrity**: ACID compliance and constraints
3. **Scalability**: Handle more data efficiently
4. **Analytics**: Built-in reporting and statistics
5. **Backup & Recovery**: Automated backup system
6. **Multi-user Support**: Ready for multiple users

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if database file exists
ls -la linkedin_jobs.db

# Reinitialize database
python database_integration.py
```

#### Migration Errors
```bash
# Check migration logs
tail -f logs/database.log

# Restore from backup
cp backups/linkedin_jobs_backup_*.db linkedin_jobs.db
```

#### API Errors
```bash
# Check API logs
tail -f logs/api.log

# Restart API
python api_bridge_with_database.py
```

### Performance Issues

#### Slow Queries
- Check database indexes
- Optimize query patterns
- Monitor query performance

#### Memory Usage
- Clean up old data regularly
- Monitor cache size
- Restart services if needed

## 📚 Additional Resources

### Documentation
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Tools
- [DB Browser for SQLite](https://sqlitebrowser.org/) - GUI database browser
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [SQLite Studio](https://sqlitestudio.pl/) - Database management tool

## 🤝 Contributing

To contribute to the database integration:

1. Follow the existing code structure
2. Add proper error handling
3. Include tests for new features
4. Update documentation
5. Follow SQLAlchemy best practices

## 📄 License

This database integration is part of the LinkedIn Job Hunter project and follows the same license terms. 