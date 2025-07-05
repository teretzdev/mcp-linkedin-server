"""
Database Manager for Enhanced MCP Server
Handles database connections, sessions, and table creation.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Any, Optional, Generator
import structlog

from ..models import Base

logger = structlog.get_logger(__name__)

class DatabaseManager:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_url = db_config.get("url", "sqlite:///./linkedin_jobs.db")
        self.engine = create_engine(self.db_url, echo=db_config.get("echo", False))
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("DatabaseManager initialized", db_url=self.db_url)

    def initialize(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully.")
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            raise

    def get_db(self) -> Generator[Session, None, None]:
        """Get a new database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def cleanup(self):
        """Dispose of the database engine"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed.")