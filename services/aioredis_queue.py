import os
import json
import asyncio
import logging
from typing import Callable, Awaitable, Dict, Any
import redis.asyncio as aioredis
from centralized_logging import get_logger
import sys

class DualLogger:
    def __init__(self, logger):
        self.logger = logger
    def log_info(self, msg):
        self.logger.log_info(msg)
        print(msg, file=sys.stdout)
    def log_error(self, msg):
        self.logger.log_error(msg)
        print(f"\033[91m{msg}\033[0m", file=sys.stderr)  # Red text for errors
    def log_warning(self, msg):
        self.logger.log_warning(msg)
        print(f"\033[93m{msg}\033[0m", file=sys.stdout)  # Yellow text for warnings

logger = DualLogger(get_logger('aioredis_queue'))
logger.log_info('aioredis_queue.py loaded - initializing...')

UPSTASH_REDIS_URL = "rediss://default:Ab4LAAIjcDE1YjJiNGIwYzUyYzQ0ZGQxOTQ2Zjc0OTliZGRkMWUyOXAxMA@pleasing-fawn-48651.upstash.io:6379"

QUEUE_NAME = 'job_automation_queue'

async def get_redis():
    """Create and return an Upstash Redis connection."""
    return await aioredis.from_url(UPSTASH_REDIS_URL, decode_responses=True)

async def enqueue_job(redis, job_type: str, payload: dict):
    """Add a job to the Redis queue asynchronously."""
    job = {
        'type': job_type,
        'payload': payload,
        'timestamp': asyncio.get_event_loop().time()
    }
    await redis.rpush(QUEUE_NAME, json.dumps(job))
    logger.log_info(f"Enqueued job: {job_type} | Payload: {payload}")

async def worker_loop(redis, job_handlers: Dict[str, Callable[[dict], Awaitable[Any]]], poll_interval: float = 1.0):
    """Continuously process jobs from the Redis queue asynchronously."""
    logger.log_info("Starting aioredis worker loop...")
    while True:
        job_data = await redis.lpop(QUEUE_NAME)
        if job_data:
            try:
                job = json.loads(job_data)
                job_type = job.get('type')
                payload = job.get('payload', {})
                handler = job_handlers.get(job_type)
                if handler:
                    logger.log_info(f"Processing job: {job_type} | Payload: {payload}")
                    await handler(payload)
                else:
                    logger.log_warning(f"No handler for job type: {job_type}")
            except Exception as e:
                logger.log_error(f"Error processing job: {e}")
        else:
            await asyncio.sleep(poll_interval)

# Example async job handlers for testing
async def handle_scrape_job(job):
    query = job.get("query")
    location = job.get("location")
    count = job.get("count", 10)
    logger.log_info(f"[REAL] Scraping jobs: {query}, {location}, {count}")

    cmd = [
        sys.executable,
        "linkedin_browser_mcp.py",
        f'--query={query}',
        f'--location={location}',
        f'--count={count}',
        '--headless'
    ]
    logger.log_info(f"Running: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    logger.log_info(f"Scraper exited with code {proc.returncode}")
    if stdout:
        logger.log_info(f"Scraper stdout: {stdout.decode()[:500]}")
    if stderr:
        logger.log_error(f"Scraper stderr: {stderr.decode()[:500]}")
    if proc.returncode != 0:
        logger.log_error("Scraping failed.")
    else:
        logger.log_info("Scraping completed successfully.")

async def handle_apply_job(payload):
    logger.log_info(f"[TEST] Would apply to job with: {payload}")
    await asyncio.sleep(1)  # Simulate async work

if __name__ == "__main__":
    async def main():
        redis = await get_redis()
        # Enqueue test jobs
        await enqueue_job(redis, 'scrape', {'query': 'Software Engineer', 'location': 'Remote', 'count': 5})
        await enqueue_job(redis, 'apply', {'job_id': '12345', 'resume': 'Resume.pdf'})
        # Start worker
        handlers = {
            'scrape': handle_scrape_job,
            'apply': handle_apply_job
        }
        worker = asyncio.create_task(worker_loop(redis, handlers))
        logger.log_info("Worker started. Press Ctrl+C to exit.")
        try:
            await worker
        except KeyboardInterrupt:
            logger.log_info("Exiting worker.")
    asyncio.run(main()) 