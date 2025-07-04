import threading
import time
from typing import List, Dict, Optional

class Job:
    """Represents a single job search or application task."""
    def __init__(self, job_id: int, job_data: dict):
        self.job_id = job_id
        self.job_data = job_data
        self.status = 'pending'  # pending, in_progress, applied, skipped, failed
        self.result: Optional[str] = None
        self.timestamp = time.time()

class JobQueue:
    """Manages the queue of jobs to search/apply."""
    def __init__(self):
        self.jobs: List[Job] = []
        self.lock = threading.Lock()
        self.next_id = 1

    def add_job(self, job_data: dict) -> int:
        with self.lock:
            job = Job(self.next_id, job_data)
            self.jobs.append(job)
            self.next_id += 1
            return job.job_id

    def get_jobs(self) -> List[Dict]:
        with self.lock:
            return [vars(job) for job in self.jobs]

    def update_job_status(self, job_id: int, status: str, result: Optional[str] = None):
        with self.lock:
            for job in self.jobs:
                if job.job_id == job_id:
                    job.status = status
                    if result:
                        job.result = result
                    break

class AutomationScheduler:
    """Handles scheduling and running the job automation loop."""
    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.running = False
        self.thread = None
        self.interval = 3600  # default: run every hour
        self.log: List[str] = []

    def start(self, interval: Optional[int] = None):
        if interval:
            self.interval = interval
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_loop, daemon=True)
            self.thread.start()
            self.log.append(f"Automation started. Interval: {self.interval}s")

    def stop(self):
        self.running = False
        self.log.append("Automation stopped.")

    def run_loop(self):
        while self.running:
            self.log.append(f"Running job automation at {time.ctime()}...")
            # TODO: Implement job search/apply logic here
            time.sleep(self.interval)

    def get_status(self) -> Dict:
        return {
            'running': self.running,
            'interval': self.interval,
            'log': self.log[-20:],  # last 20 log entries
        }

# Singleton instances for use in API
job_queue = JobQueue()
automation_scheduler = AutomationScheduler(job_queue) 