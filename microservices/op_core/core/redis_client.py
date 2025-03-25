import redis
from .config import settings

redis_client = redis.Redis(
    host=settings.REDIS_CONFIG['host'],
    port=settings.REDIS_CONFIG['port'],
    db=settings.REDIS_CONFIG['default_db'],
    password=settings.REDIS_CONFIG['password'],
    decode_responses=True
)

def get_redis():
    try:
        yield redis_client
    finally:
        pass  # Redis connection is managed by the client pool

def set_key(key: str, value: str, expire: int = None):
    return redis_client.set(key, value, ex=expire)

def get_key(key: str):
    return redis_client.get(key)

def delete_key(key: str):
    return redis_client.delete(key)

def set_hash(name: str, mapping: dict):
    return redis_client.hmset(name, mapping)

def get_hash(name: str):
    return redis_client.hgetall(name) 