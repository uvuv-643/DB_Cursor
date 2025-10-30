import redis.asyncio as redis

from ..settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True  # чтобы работать с str вместо bytes
)
