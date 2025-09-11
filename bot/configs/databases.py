from dotenv import load_dotenv
import os
import asyncpg
import redis as redis_lib
load_dotenv()

class Postgresql:
    def __init__(self):
        self.db_name = os.getenv('POSTGRES_DB')
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')
        self.host = os.getenv('POSTGRES_HOST')
        self.port = os.getenv('POSTGRES_PORT')

    def __getattr__(self, item):
        return getattr(self, item, None)

postgresql = Postgresql()

class Redis:
    def __init__(self):
        self.host = os.getenv('REDIS_HOST')
        self.port = os.getenv('REDIS_PORT')
        self.db = os.getenv('REDIS_DB')
        self.password = os.getenv('REDIS_PASSWORD')

    def __getattr__(self, item):
        return getattr(self, item, None)

class LangRedis:
    def __init__(self):
        self.host = os.getenv('LANG_REDIS_HOST')
        self.port = os.getenv('LANG_REDIS_PORT')
        self.db = os.getenv('LANG_REDIS_DB')
        self.password = os.getenv('LANG_REDIS_PASSWORD')

    def __getattr__(self, item):
        return getattr(self, item, None)

redis = Redis()

# Підключення до Redis
r = redis_lib.Redis(
    host=redis.host,
    port=redis.port,
    db=redis.db,
    decode_responses=True
)
