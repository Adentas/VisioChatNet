from flask_caching import Cache

cache = Cache(config = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300, 
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    }
)

def generate_chat_history_cache_key(chat_id):
    return f"chat_history_{chat_id}"

def generate_user_chat_cache_key(user_id):
    return f"user_chats_{user_id}"