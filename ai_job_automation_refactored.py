#!/usr/bin/env python3
"""
AI Job Automation - Refactored Architecture
A complete rewrite using modern design patterns and clean architecture.
"""
import asyncio
import argparse
import logging
import sys
from typing import Optional

from core.config.settings import AutomationConfig, get_config, reload_config
from core.models.job_data import SearchCriteria
from orchestrators.job_automation_orchestrator import JobAutomationOrchestrator


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/ai_job_automation_refactored.log')
        ]
    )


async def run_reconnaissance(
    query: str,
    location: str = "Remote",
    count: int = 20,
    config_file: Optional[str] = None
) -> None:
    """Run reconnaissance phase only"""
    
    # Load configuration
    config = reload_config(config_file) if config_file else get_config()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logging.error("Configuration errors:")
        for error in errors:
            logging.error(f"  - {error}")
        return
    
    # Create search criteria
    search_criteria = SearchCriteria(
        query=query,
        location=location,
        count=count,
        remote_only=True,
        easy_apply_only=True
    )
    
    # Initialize orchestrator
    orchestrator = JobAutomationOrchestrator(config=config)
    
    # Run reconnaissance
    logging.info(f"Starting reconnaissance for: {query}")
    result = await orchestrator.run_reconnaissance_phase(search_criteria)
    
    # Print results
    print("\n" + "="*60)
    print("RECONNAISSANCE RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'success':
        print(f"Jobs found: {result['total_found']}")
        print(f"New jobs added: {result['new_jobs_added']}")
    
    if 'stats' in result:
        stats = result['stats']
        print(f"Duration: {stats.get('duration_seconds', 0):.1f} seconds")
        if stats.get('errors', 0) > 0:
            print(f"Errors: {stats['errors']}")


async def run_application(
    max_applications: Optional[int] = None,
    config_file: Optional[str] = None
) -> None:
    """Run application phase only"""
    
    # Load configuration
    config = reload_config(config_file) if config_file else get_config()
    
    # Initialize orchestrator
    orchestrator = JobAutomationOrchestrator(config=config)
    
    # Run application phase
    logging.info("Starting application phase")
    result = await orchestrator.run_application_phase(max_applications)
    
    # Print results
    print("\n" + "="*60)
    print("APPLICATION RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Applications submitted: {result.get('applications_submitted', 0)}")
    print(f"Jobs available: {result.get('jobs_available', 0)}")


async def run_full_cycle(
    query: str,
    location: str = "Remote",
    count: int = 20,
    max_applications: Optional[int] = None,
    config_file: Optional[str] = None
) -> None:
    """Run full automation cycle"""
    
    # Load configuration
    config = reload_config(config_file) if config_file else get_config()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logging.error("Configuration errors:")
        for error in errors:
            logging.error(f"  - {error}")
        return
    
    # Create search criteria
    search_criteria = SearchCriteria(
        query=query,
        location=location,
        count=count,
        remote_only=True,
        easy_apply_only=True
    )
    
    # Initialize orchestrator
    orchestrator = JobAutomationOrchestrator(config=config)
    
    # Run full cycle
    logging.info(f"Starting full automation cycle for: {query}")
    result = await orchestrator.run_full_automation_cycle(search_criteria)
    
    # Print results
    print("\n" + "="*60)
    print("FULL AUTOMATION CYCLE RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['status'] == 'success':
        total_stats = result.get('total_stats', {})
        print(f"Jobs found: {total_stats.get('jobs_found', 0)}")
        print(f"New jobs added: {total_stats.get('new_jobs_added', 0)}")
        print(f"Applications submitted: {total_stats.get('applications_submitted', 0)}")
        if total_stats.get('total_errors', 0) > 0:
            print(f"Total errors: {total_stats['total_errors']}")


async def show_status(config_file: Optional[str] = None) -> None:
    """Show automation status"""
    
    # Load configuration
    config = reload_config(config_file) if config_file else get_config()
    
    # Initialize orchestrator
    orchestrator = JobAutomationOrchestrator(config=config)
    
    # Get status
    summary = orchestrator.get_automation_summary()
    
    # Print status
    print("\n" + "="*60)
    print("AUTOMATION STATUS")
    print("="*60)
    
    if 'error' in summary:
        print(f"Error: {summary['error']}")
        return
    
    print(f"Scraped jobs (ready for application): {summary['scraped_jobs']}")
    print(f"Applied jobs: {summary['applied_jobs']}")
    print(f"Failed jobs: {summary['failed_jobs']}")
    print(f"Recent jobs (last 24h): {summary['recent_jobs']}")
    
    print("\nConfiguration:")
    config_info = summary.get('config', {})
    print(f"  Max applications per cycle: {config_info.get('max_applications_per_cycle', 'N/A')}")
    print(f"  Search timeout: {config_info.get('search_timeout', 'N/A')} seconds")
    print(f"  Application timeout: {config_info.get('application_timeout', 'N/A')} seconds")


async def test_connection(config_file: Optional[str] = None) -> None:
    """Test LinkedIn connection"""
    
    # Load configuration
    config = reload_config(config_file) if config_file else get_config()
    
    # Initialize orchestrator
    orchestrator = JobAutomationOrchestrator(config=config)
    
    # Test connection
    print("Testing LinkedIn connection...")
    success = await orchestrator.job_search_service.test_connection()
    
    if success:
        print("✅ LinkedIn connection test successful")
    else:
        print("❌ LinkedIn connection test failed")
        print("Check your credentials and network connection")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Job Automation - Refactored")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Reconnaissance command
    recon_parser = subparsers.add_parser('recon', help='Run reconnaissance phase')
    recon_parser.add_argument('query', help='Job search query')
    recon_parser.add_argument('--location', default='Remote', help='Job location')
    recon_parser.add_argument('--count', type=int, default=20, help='Number of jobs to search')
    
    # Application command
    app_parser = subparsers.add_parser('apply', help='Run application phase')
    app_parser.add_argument('--max-applications', type=int, help='Maximum applications to submit')
    
    # Full cycle command
    full_parser = subparsers.add_parser('full', help='Run full automation cycle')
    full_parser.add_argument('query', help='Job search query')
    full_parser.add_argument('--location', default='Remote', help='Job location')
    full_parser.add_argument('--count', type=int, default=20, help='Number of jobs to search')
    full_parser.add_argument('--max-applications', type=int, help='Maximum applications to submit')
    
    # Status command
    subparsers.add_parser('status', help='Show automation status')
    
    # Test command
    subparsers.add_parser('test', help='Test LinkedIn connection')

    # Validate command
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Legacy compatibility commands
    legacy_parser = subparsers.add_parser('start_recon', help='Legacy: Start reconnaissance')
    legacy_parser.add_argument('--query', default='software engineer', help='Job search query')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Handle legacy commands first
    if args.command == 'start_recon':
        logging.info("Running legacy start_recon command")
        asyncio.run(run_reconnaissance(
            query=args.query,
            config_file=args.config
        ))
        return
    
    # Handle new commands
    if args.command == 'recon':
        asyncio.run(run_reconnaissance(
            query=args.query,
            location=args.location,
            count=args.count,
            config_file=args.config
        ))
    elif args.command == 'apply':
        asyncio.run(run_application(
            max_applications=args.max_applications,
            config_file=args.config
        ))
    elif args.command == 'full':
        asyncio.run(run_full_cycle(
            query=args.query,
            location=args.location,
            count=args.count,
            max_applications=args.max_applications,
            config_file=args.config
        ))
    elif args.command == 'status':
        asyncio.run(show_status(config_file=args.config))
    elif args.command == 'test':
        asyncio.run(test_connection(config_file=args.config))
    elif args.command == 'validate':
        # Reload config to ensure it's the latest and validate
        config = reload_config(args.config)
        errors = config.validate()
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            print("Please fix these errors before running automation.")
        else:
            print("✅ Configuration is valid. Ready to run automation.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 