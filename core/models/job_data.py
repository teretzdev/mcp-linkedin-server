"""
Core job data models for the LinkedIn automation system.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class JobStatus(Enum):
    """Job processing status"""
    SCRAPED = "scraped"
    APPLYING = "applying"
    APPLIED = "applied"
    FAILED = "failed"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class ApplicationStatus(Enum):
    """Application submission status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"


@dataclass
class JobData:
    """Structured job data model"""
    job_id: str
    title: str
    company: str
    location: str
    job_url: str
    description: str = ""
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    easy_apply: bool = False
    remote_work: bool = False
    posted_date: Optional[datetime] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    status: JobStatus = JobStatus.SCRAPED
    
    # Metadata
    source: str = "linkedin"
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/database storage"""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_url': self.job_url,
            'description': self.description,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'easy_apply': self.easy_apply,
            'remote_work': self.remote_work,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'scraped_at': self.scraped_at.isoformat(),
            'status': self.status.value,
            'source': self.source,
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobData':
        """Create from dictionary"""
        # Handle datetime fields
        scraped_at = data.get('scraped_at')
        if isinstance(scraped_at, str):
            scraped_at = datetime.fromisoformat(scraped_at)
        elif scraped_at is None:
            scraped_at = datetime.now()
            
        posted_date = data.get('posted_date')
        if isinstance(posted_date, str):
            posted_date = datetime.fromisoformat(posted_date)
            
        # Handle status enum
        status = data.get('status', JobStatus.SCRAPED.value)
        if isinstance(status, str):
            status = JobStatus(status)
            
        return cls(
            job_id=data['job_id'],
            title=data['title'],
            company=data['company'],
            location=data['location'],
            job_url=data['job_url'],
            description=data.get('description', ''),
            salary_range=data.get('salary_range'),
            job_type=data.get('job_type'),
            experience_level=data.get('experience_level'),
            easy_apply=data.get('easy_apply', False),
            remote_work=data.get('remote_work', False),
            posted_date=posted_date,
            scraped_at=scraped_at,
            status=status,
            source=data.get('source', 'linkedin'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )


@dataclass
class SearchCriteria:
    """Job search criteria"""
    query: str
    location: str = "Remote"
    count: int = 50
    experience_levels: List[str] = field(default_factory=list)
    job_types: List[str] = field(default_factory=list)
    remote_only: bool = False
    easy_apply_only: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            'query': self.query,
            'location': self.location,
            'count': self.count,
            'experience_levels': self.experience_levels,
            'job_types': self.job_types,
            'remote_only': self.remote_only,
            'easy_apply_only': self.easy_apply_only
        }


@dataclass
class ApplicationResult:
    """Result of a job application attempt"""
    job_id: str
    status: ApplicationStatus
    message: str = ""
    error_details: Optional[str] = None
    applied_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'status': self.status.value,
            'message': self.message,
            'error_details': self.error_details,
            'applied_at': self.applied_at.isoformat()
        } 