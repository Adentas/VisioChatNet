from flask_caching import Cache
import os

redis_host = os.getenv("REDIS_HOST", "localhost") 
redis_port = os.getenv("REDIS_PORT", "6379") 
redis_password = os.getenv("REDIS_PASSWORD", "") 

redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"

# Configure the cache with the dynamic Redis URL
cache = Cache(
    config={
        "CACHE_TYPE": "redis",
        "CACHE_DEFAULT_TIMEOUT": 300,
        "CACHE_REDIS_URL": redis_url,
    }
)

def generate_chat_history_cache_key(chat_id):
    return f"chat_history_{chat_id}"

def generate_user_chat_cache_key(user_id):
    return f"user_chats_{user_id}"