"""Cache Config"""

import os
from urllib.parse import urlparse

from modules.misc import memoize


def url_config(raw_url):
    """URL config parser"""
    url = urlparse(raw_url)
    return {
        'endpoint': url.hostname,
        'port': url.port,
        'username': url.username,
        'password': url.password,
        'scheme': url.scheme
    }


REDIS_URL = os.getenv('REDIS_URL', None)


def read_and_build_config():
    """Reads and builds the config"""
    # 'memcache': { },  # TODO: Once this gets properly supported...
    cache_config = {
        'default': {
                'cache': "aiocache.SimpleMemoryCache",
                'serializer': {
                    'class': "aiocache.serializers.StringSerializer"
                }
            },
    }

    if REDIS_URL:
        redis_url_info = url_config(REDIS_URL)
        redis_config = {
            'redis': {
                    'cache': "aiocache.RedisCache",
                    'endpoint': redis_url_info.get('endpoint', "127.0.0.1"),
                    'port': redis_url_info.get('port', 6379),
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
        cache_config['redis'] = redis_config['redis']
        if redis_url_info.get('password', None):
            cache_config['redis']['password'] = redis_url_info['password']

    return cache_config


memozied_config = memoize(read_and_build_config)
CACHE_CONFIG = memozied_config()
