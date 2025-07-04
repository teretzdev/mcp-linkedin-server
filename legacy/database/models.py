#!/usr/bin/env python3
"""
Database Models for LinkedIn Job Hunter System
Defines all database tables and relationships
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()

class User(Base):
    """User profile and credentials"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    current_position = Column(String(255), nullable=True)
    skills = Column(MutableList.as_mutable(JSON), default=list)
    target_roles = Column(MutableList.as_mutable(JSON), default=list)
    target_locations = Column(MutableList.as_mutable(JSON), default=list)
    experience_years = Column(Integer, nullable=True)
    resume_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    saved_jobs = relationship("SavedJob", back_populates="user")
    applied_jobs = relationship("AppliedJob", back_populates="user")
    session_data = relationship("SessionData", back_populates="user")
    automation_logs = relationship("AutomationLog", back_populates="user")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'current_position': self.current_position,
            'skills': self.skills or [],
            'target_roles': self.target_roles or [],
            'target_locations': self.target_locations or [],
            'experience_years': self.experience_years,
            'resume_url': self.resume_url,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }

class SavedJob(Base):
    """Saved jobs for later review"""
    __tablename__ = 'saved_jobs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(String(255), nullable=False)  # LinkedIn job ID
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    job_url = Column(String(1000), nullable=False)
    description = Column(Text, nullable=True)
    salary_range = Column(String(255), nullable=True)
    job_type = Column(String(100), nullable=True)  # Full-time, Part-time, Contract
    experience_level = Column(String(100), nullable=True)  # Entry, Mid, Senior
    easy_apply = Column(Boolean, default=False)
    remote_work = Column(Boolean, default=False)
    saved_at = Column(DateTime, default=func.now())
    notes = Column(Text, nullable=True)
    tags = Column(MutableList.as_mutable(JSON), default=list)  # Custom tags for organization
    
    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert saved job to dictionary"""
        return {
            'id': self.id,
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
            'saved_at': self.saved_at.isoformat() if self.saved_at is not None else None,
            'notes': self.notes,
            'tags': self.tags or []
        }

class AppliedJob(Base):
    """Jobs that have been applied to"""
    __tablename__ = 'applied_jobs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(String(255), nullable=False)  # LinkedIn job ID
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    job_url = Column(String(1000), nullable=False)
    applied_at = Column(DateTime, default=func.now())
    application_status = Column(String(100), default='applied')  # applied, viewed, interviewing, rejected, accepted
    cover_letter = Column(Text, nullable=True)
    resume_used = Column(String(500), nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="applied_jobs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert applied job to dictionary"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_url': self.job_url,
            'applied_at': self.applied_at.isoformat() if self.applied_at is not None else None,
            'application_status': self.application_status,
            'cover_letter': self.cover_letter,
            'resume_used': self.resume_used,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date is not None else None,
            'notes': self.notes,
            'response_received': self.response_received,
            'response_date': self.response_date.isoformat() if self.response_date is not None else None
        }

class SessionData(Base):
    """Session statistics and data"""
    __tablename__ = 'session_data'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(255), nullable=False)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    jobs_viewed = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    session_duration = Column(Integer, nullable=True)  # Duration in seconds
    goals_processed = Column(Integer, default=0)
    automation_mode = Column(String(100), default='manual')  # manual, automated, hybrid
    
    # Relationships
    user = relationship("User", back_populates="session_data")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time is not None else None,
            'end_time': self.end_time.isoformat() if self.end_time is not None else None,
            'jobs_viewed': self.jobs_viewed,
            'jobs_applied': self.jobs_applied,
            'jobs_saved': self.jobs_saved,
            'errors_encountered': self.errors_encountered,
            'session_duration': self.session_duration,
            'goals_processed': self.goals_processed,
            'automation_mode': self.automation_mode
        }

class AutomationLog(Base):
    """Automation activity logs"""
    __tablename__ = 'automation_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    action = Column(String(255), nullable=False)
    details = Column(JSON, nullable=True)  # Accept both dict and list
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    job_id = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="automation_logs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert automation log to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp is not None else None,
            'action': self.action,
            'details': self.details,
            'success': self.success,
            'error_message': self.error_message,
            'duration_ms': self.duration_ms,
            'job_id': self.job_id
        }

class JobRecommendation(Base):
    """AI-generated job recommendations"""
    __tablename__ = 'job_recommendations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_id = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    job_url = Column(String(1000), nullable=False)
    recommendation_score = Column(Integer, nullable=False)  # 1-100 score
    reasoning = Column(Text, nullable=True)  # AI reasoning for recommendation
    skills_match = Column(MutableList.as_mutable(JSON), default=list)  # Matching skills
    created_at = Column(DateTime, default=func.now())
    viewed = Column(Boolean, default=False)
    applied = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job recommendation to dictionary"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_url': self.job_url,
            'recommendation_score': self.recommendation_score,
            'reasoning': self.reasoning,
            'skills_match': self.skills_match or [],
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'viewed': self.viewed,
            'applied': self.applied
        }

class SystemSettings(Base):
    """System configuration and settings"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    setting_type = Column(String(50), default='string')  # string, integer, boolean, json
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert system setting to dictionary"""
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        } 