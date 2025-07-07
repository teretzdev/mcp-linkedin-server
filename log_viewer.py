#!/usr/bin/env python3
"""
Log Viewer Utility for LinkedIn Job Hunter
Provides easy access to view logs and errors across all services
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# Import the centralized logging system
from centralized_logging import log_manager, get_logger

class LogViewer:
    """Utility to view and analyze logs"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    def list_log_files(self) -> List[Path]:
        """List all available log files"""
        log_files = []
        for file_path in self.logs_dir.glob("*.log"):
            log_files.append(file_path)
        return sorted(log_files)
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of all log files"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'log_files': {},
            'total_files': 0,
            'total_size_mb': 0
        }
        
        for log_file in self.list_log_files():
            try:
                stat = log_file.stat()
                file_size_mb = stat.st_size / (1024 * 1024)
                
                # Count lines
                with open(log_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                # Get last modified time
                last_modified = datetime.fromtimestamp(stat.st_mtime)
                
                summary['log_files'][log_file.name] = {
                    'size_mb': round(file_size_mb, 2),
                    'line_count': line_count,
                    'last_modified': last_modified.isoformat(),
                    'path': str(log_file)
                }
                
                summary['total_files'] += 1
                summary['total_size_mb'] += file_size_mb
                
            except Exception as e:
                summary['log_files'][log_file.name] = {
                    'error': str(e)
                }
        
        summary['total_size_mb'] = round(summary['total_size_mb'], 2)
        return summary
    
    def view_log_file(self, filename: str, lines: int = 50, 
                     filter_level: Optional[str] = None,
                     search: Optional[str] = None,
                     show_errors_only: bool = False) -> List[str]:
        """View contents of a log file with filters"""
        log_file = self.logs_dir / filename
        
        if not log_file.exists():
            return [f"Error: Log file {filename} not found"]
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            # Apply filters
            filtered_lines = []
            
            for line in all_lines:
                # Skip if not matching search
                if search and search.lower() not in line.lower():
                    continue
                
                # Skip if not matching level filter
                if filter_level and filter_level.upper() not in line.upper():
                    continue
                
                # Skip if showing errors only but line is not an error
                if show_errors_only and 'ERROR' not in line.upper() and 'CRITICAL' not in line.upper():
                    continue
                
                filtered_lines.append(line)
            
            # Return last N lines
            return filtered_lines[-lines:] if lines > 0 else filtered_lines
            
        except Exception as e:
            return [f"Error reading log file: {e}"]
    
    def get_recent_errors(self, hours: int = 24) -> Dict[str, List[str]]:
        """Get recent errors from all log files"""
        errors = {}
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in self.list_log_files():
            if 'error' in log_file.name.lower():
                service_name = log_file.stem.replace('_errors', '')
                errors[service_name] = []
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Check if line contains ERROR or CRITICAL
                            if 'ERROR' in line.upper() or 'CRITICAL' in line.upper():
                                # Try to parse timestamp
                                try:
                                    # Extract timestamp from line
                                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                                    if timestamp_match:
                                        timestamp_str = timestamp_match.group(1)
                                        line_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                        
                                        if line_time >= cutoff_time:
                                            errors[service_name].append(line.strip())
                                except:
                                    # If timestamp parsing fails, include the line anyway
                                    errors[service_name].append(line.strip())
                
                except Exception as e:
                    errors[service_name] = [f"Error reading file: {e}"]
        
        return errors
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services based on logs"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # Get summaries from log manager
        summaries = log_manager.get_all_summaries()
        
        for service_name, service_data in summaries['system']['services'].items():
            error_summary = service_data['error_summary']
            perf_summary = service_data['performance_summary']
            
            # Determine service status
            if error_summary['error_count'] > 0:
                status_level = 'ERROR'
            elif perf_summary.get('avg_duration', 0) > 2.0:
                status_level = 'WARNING'
            else:
                status_level = 'HEALTHY'
            
            status['services'][service_name] = {
                'status': status_level,
                'error_count': error_summary['error_count'],
                'last_error': error_summary['last_error_time'],
                'avg_response_time': perf_summary.get('avg_duration', 0),
                'total_operations': perf_summary.get('operations', 0)
            }
        
        return status
    
    def search_logs(self, query: str, files: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Search across log files"""
        results = {}
        
        search_files = []
        if files:
            for filename in files:
                file_path = self.logs_dir / filename
                if file_path.exists():
                    search_files.append(file_path)
        else:
            search_files = self.list_log_files()
        
        for log_file in search_files:
            service_name = log_file.stem
            results[service_name] = []
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if query.lower() in line.lower():
                            results[service_name].append(f"Line {line_num}: {line.strip()}")
            except Exception as e:
                results[service_name] = [f"Error reading file: {e}"]
        
        # Remove empty results
        results = {k: v for k, v in results.items() if v}
        return results
    
    def clear_old_logs(self, days: int = 7) -> Dict[str, Any]:
        """Clear old log files"""
        cutoff_time = datetime.now() - timedelta(days=days)
        cleared_files = []
        errors = []
        
        for log_file in self.list_log_files():
            try:
                if log_file.stat().st_mtime < cutoff_time.timestamp():
                    log_file.unlink()
                    cleared_files.append(log_file.name)
            except Exception as e:
                errors.append(f"Error clearing {log_file.name}: {e}")
        
        return {
            'cleared_files': cleared_files,
            'errors': errors,
            'cutoff_date': cutoff_time.isoformat()
        }

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='LinkedIn Job Hunter Log Viewer')
    parser.add_argument('command', choices=['list', 'view', 'errors', 'status', 'search', 'clear', 'summary'],
                       help='Command to execute')
    parser.add_argument('--file', '-f', help='Log file to view')
    parser.add_argument('--lines', '-n', type=int, default=50, help='Number of lines to show')
    parser.add_argument('--level', '-l', choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Filter by log level')
    parser.add_argument('--search', '-s', help='Search term')
    parser.add_argument('--errors-only', '-e', action='store_true', help='Show only errors')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back for errors')
    parser.add_argument('--days', type=int, default=7, help='Days for clearing old logs')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    viewer = LogViewer()
    
    if args.command == 'list':
        log_files = viewer.list_log_files()
        if args.output == 'json':
            print(json.dumps([str(f) for f in log_files], indent=2))
        else:
            print("Available log files:")
            for log_file in log_files:
                print(f"  {log_file.name}")
    
    elif args.command == 'view':
        if not args.file:
            print("Error: --file argument required for view command")
            return
        
        lines = viewer.view_log_file(args.file, args.lines, args.level, args.search, args.errors_only)
        if args.output == 'json':
            print(json.dumps(lines, indent=2))
        else:
            for line in lines:
                print(line.rstrip())
    
    elif args.command == 'errors':
        errors = viewer.get_recent_errors(args.hours)
        if args.output == 'json':
            print(json.dumps(errors, indent=2))
        else:
            print(f"Recent errors (last {args.hours} hours):")
            for service, error_lines in errors.items():
                if error_lines:
                    print(f"\n{service.upper()}:")
                    for line in error_lines[-10:]:  # Show last 10 errors
                        print(f"  {line}")
    
    elif args.command == 'status':
        status = viewer.get_service_status()
        if args.output == 'json':
            print(json.dumps(status, indent=2))
        else:
            print("Service Status:")
            for service, data in status['services'].items():
                print(f"  {service}: {data['status']}")
                print(f"    Errors: {data['error_count']}")
                print(f"    Avg Response: {data['avg_response_time']:.3f}s")
                print(f"    Operations: {data['total_operations']}")
    
    elif args.command == 'search':
        if not args.search:
            print("Error: --search argument required for search command")
            return
        
        results = viewer.search_logs(args.search)
        if args.output == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"Search results for '{args.search}':")
            for service, matches in results.items():
                if matches:
                    print(f"\n{service.upper()}:")
                    for match in matches[:10]:  # Show first 10 matches
                        print(f"  {match}")
    
    elif args.command == 'clear':
        result = viewer.clear_old_logs(args.days)
        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(f"Cleared {len(result['cleared_files'])} old log files")
            if result['errors']:
                print("Errors:")
                for error in result['errors']:
                    print(f"  {error}")
    
    elif args.command == 'summary':
        summary = viewer.get_log_summary()
        if args.output == 'json':
            print(json.dumps(summary, indent=2))
        else:
            print("Log Summary:")
            print(f"Total files: {summary['total_files']}")
            print(f"Total size: {summary['total_size_mb']} MB")
            print("\nFiles:")
            for filename, data in summary['log_files'].items():
                if 'error' not in data:
                    print(f"  {filename}: {data['size_mb']} MB, {data['line_count']} lines")

if __name__ == "__main__":
    main() 