import os
import json
import time
import threading
import logging
from typing import Callable, Any
import redis

# Basic Redis connection setup (uses environment variables or defaults)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

QUEUE_NAME = 'job_automation_queue'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('redis_queue')

def enqueue_job(job_type: str, payload: dict):
    """Add a job to the Redis queue."""
    job = {
        'type': job_type,
        'payload': payload,
        'timestamp': time.time()
    }
    redis_client.rpush(QUEUE_NAME, json.dumps(job))
    logger.info(f"Enqueued job: {job_type} | Payload: {payload}")

def worker_loop(job_handlers: dict[str, Callable[[dict], Any]], poll_interval: float = 1.0):
    """Continuously process jobs from the Redis queue."""
    logger.info("Starting Redis worker loop...")
    while True:
        job_data = redis_client.lpop(QUEUE_NAME)
        if job_data:
            try:
                job = json.loads(job_data)
                job_type = job.get('type')
                payload = job.get('payload', {})
                handler = job_handlers.get(job_type)
                if handler:
                    logger.info(f"Processing job: {job_type} | Payload: {payload}")
                    handler(payload)
                else:
                    logger.warning(f"No handler for job type: {job_type}")
            except Exception as e:
                logger.error(f"Error processing job: {e}")
        else:
            time.sleep(poll_interval)

# Example job handlers for testing

def handle_scrape_job(payload):
    logger.info(f"[TEST] Would scrape jobs with: {payload}")
    # Place scraping logic here

def handle_apply_job(payload):
    logger.info(f"[TEST] Would apply to job with: {payload}")
    # Place application logic here

if __name__ == "__main__":
    # For testing: enqueue a test job and start the worker in a thread
    enqueue_job('scrape', {'query': 'Software Engineer', 'location': 'Remote', 'count': 5})
    enqueue_job('apply', {'job_id': '12345', 'resume': 'Resume.pdf'})

    handlers = {
        'scrape': handle_scrape_job,
        'apply': handle_apply_job
    }
    worker_thread = threading.Thread(target=worker_loop, args=(handlers,), daemon=True)
    worker_thread.start()
    logger.info("Worker started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting worker.") 