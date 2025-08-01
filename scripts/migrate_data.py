#!/usr/bin/env python3
"""
One-time migration script to transition from SavedJob/AppliedJob tables
to the new unified ScrapedJob table.

This script will:
1. Connect to the SQLite database.
2. Drop the 'saved_jobs' and 'applied_jobs' tables if they exist.
3. Create the new 'scraped_jobs' table based on the updated models.

WARNING: This is a destructive operation and will remove existing data
in the 'saved_jobs' and 'applied_jobs' tables.
"""

import sys
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Ensure the script can find the database models and manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from legacy.database.database import DatabaseManager, DATABASE_URL
from legacy.database.models import Base, ScrapedJob, SavedJob, AppliedJob

def migrate_database():
    """
    Performs the database migration.
    """
    print("Starting database migration...")
    
    # Create an engine and inspector
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Get table names from the models
    saved_jobs_table = SavedJob.__tablename__
    applied_jobs_table = AppliedJob.__tablename__
    scraped_jobs_table = ScrapedJob.__tablename__

    # 1. Drop the old tables if they exist
    print(f"Checking for old tables ('{saved_jobs_table}', '{applied_jobs_table}')...")
    with engine.begin() as connection:
        if inspector.has_table(saved_jobs_table):
            print(f"Dropping table: {saved_jobs_table}")
            SavedJob.__table__.drop(connection)
            print(f"'{saved_jobs_table}' table dropped.")
        else:
            print(f"Table '{saved_jobs_table}' not found, skipping drop.")
            
        if inspector.has_table(applied_jobs_table):
            print(f"Dropping table: {applied_jobs_table}")
            AppliedJob.__table__.drop(connection)
            print(f"'{applied_jobs_table}' table dropped.")
        else:
            print(f"Table '{applied_jobs_table}' not found, skipping drop.")

    # 2. Create the new table
    print(f"Creating new '{scraped_jobs_table}' table...")
    try:
        Base.metadata.create_all(engine, tables=[ScrapedJob.__table__])
        print(f"'{scraped_jobs_table}' table created successfully.")
    except Exception as e:
        print(f"Error creating '{scraped_jobs_table}' table: {e}")
        print("Migration failed.")
        return

    print("\nMigration completed successfully!")
    print(f"The database now contains the '{scraped_jobs_table}' table.")
    print("Old 'saved_jobs' and 'applied_jobs' tables have been removed.")

if __name__ == "__main__":
    # Simple confirmation prompt
    confirm = input("WARNING: This will delete the 'saved_jobs' and 'applied_jobs' tables.\nAre you sure you want to continue? (y/n): ")
    if confirm.lower() == 'y':
        migrate_database()
    else:
        print("Migration cancelled.")
