from centralized_logging import get_logger
logger = get_logger('aioredis_test')

import redis.asyncio as aioredis
logger.log_info('redis.asyncio imported successfully')
import asyncio
async def test():
    redis = await aioredis.from_url('redis://localhost:6379/0')
    await redis.set('aioredis_test_key', 'ok')
    val = await redis.get('aioredis_test_key')
    logger.log_info(f'Redis test key value: {val}')
    await redis.delete('aioredis_test_key')
asyncio.run(test()) 