from flask_caching import Cache

cache = Cache(config = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300, 
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    }
)