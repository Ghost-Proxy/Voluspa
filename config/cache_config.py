import os


def redis_config(env_var):
    user, address, port = env_var.replace('redis://', '').split(':')
    password, ip = address.split('@')
    return {
        'endpoint': ip,
        'port': port,
        'password': password
    }


REDIS_URL = os.getenv('REDIS_URL')
REDIS_CONFIG = {}
if REDIS_URL:
    REDIS_CONFIG = redis_config(REDIS_URL)

CACHE_CONFIG = {
    'default': {
            'cache': "aiocache.SimpleMemoryCache",
            'serializer': {
                'class': "aiocache.serializers.StringSerializer"
            }
        },
    # 'memcache': {
    #     'cache': "aiocache.MemcachedCache",
    #     'endpoint': os.getenv('MEMCACHE_ENDPOINT', "127.0.0.1"),
    #     'port': 6379,
    #     'timeout': 1,
    #     'serializer': {
    #         'class': "aiocache.serializers.PickleSerializer"
    #     },
    #     'plugins': [
    #         {'class': "aiocache.plugins.HitMissRatioPlugin"},
    #         {'class': "aiocache.plugins.TimingPlugin"}
    #     ]
    # },
    'redis': {
            'cache': "aiocache.RedisCache",
            'endpoint': REDIS_CONFIG.get('endpoint', "127.0.0.1"),
            'port': REDIS_CONFIG.get('port', 6379),
            'timeout': 1,
            'serializer': {
                'class': "aiocache.serializers.PickleSerializer"
            },
            'plugins': [
                {'class': "aiocache.plugins.HitMissRatioPlugin"},
                {'class': "aiocache.plugins.TimingPlugin"}
            ]
        }
}

if REDIS_CONFIG.get('password', None):
    CACHE_CONFIG['redis']['password'] = REDIS_CONFIG['password']
