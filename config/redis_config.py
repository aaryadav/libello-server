import redis
from config.settings import *

redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
)
