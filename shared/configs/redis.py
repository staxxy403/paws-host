import os
from arq.connections import RedisSettings

REDIS_URL = os.getenv('REDIS_URL')

arq_redis_settings = RedisSettings.from_dsn(dsn=REDIS_URL)
