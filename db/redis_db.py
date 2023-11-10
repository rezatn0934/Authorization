import redis.asyncio as aioredis

from config.config import settings

redis = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}', encoding='utf-8',
                          db=settings.REDIS_DATABASE_NUMBER,
                          decode_responses=True)


def get_redis_client():
    """
    The get_redis_client function returns a Redis client object.

    :return: The redis object
    :doc-author: Trelent
    """
    return redis
