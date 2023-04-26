"""Cache Module"""

import logging

from aiocache import caches
from modules.exceptions import VoluspaError

from voluspa import CONFIG

logger = logging.getLogger('voluspa.cache')

if CONFIG.Voluspa.cache.get('redis', None):
    CACHE_NAME = 'redis'
else:
    CACHE_NAME = 'default'
CACHE_TYPE = CONFIG.Voluspa.cache[CACHE_NAME].cache
logger.info('Using "%s" cache (%s)', CACHE_NAME, CACHE_TYPE)


async def add(key, value, cache_name=CACHE_NAME):
    """Add a key and value to the cache"""
    # This will fail if the key already exists
    cache = caches.get(cache_name)
    if cache:
        await cache.add(key, value)
        result = await cache.get(key) == value
        if result:
            logger.info('(cache: %s) - SUCCESS wrote k/v [%s]:[%s]!', cache_name, key, value)
            return result

        logger.warning('(cache: %s) - ERROR writing k/v [%s]:[%s]!', cache_name, key, value)
        return result
    raise VoluspaError('Unable to retrieve cache')


async def write(key, value, cache_name=CACHE_NAME):
    """Write the value to a key, whether it exists or not"""
    # This also implies add -- AND is a forced overwrite
    cache = caches.get(cache_name)
    if cache:
        await cache.set(key, value)
        result = await cache.get(key) == value
        # assert await cache.get(key) == value
        if result:
            logger.info('(cache: %s) - SUCCESS wrote k/v [%s]:[%s]!', cache_name, key, value)
            return result

        logger.warning('(cache: %s) - ERROR writing k/v [%s]:[%s]!', cache_name, key, value)
        return result
    raise VoluspaError('Unable to retrieve cache')


async def read(key, cache_name=CACHE_NAME):
    """Read the value from the requested key"""
    cache = caches.get(cache_name)
    if cache:
        value = await cache.get(key)
        if value:
            logger.info('(cache: %s) - SUCCESS read k/v [%s]:[%s]!', cache_name, key, value)
            return value

        logger.warning('(cache: %s) - ERROR reading k/v [%s]:[%s]!', cache_name, key, value)
        return None
    raise VoluspaError('Unable to retrieve cache')


async def delete(key, cache_name=CACHE_NAME):
    """Delete the key (and value) requested"""
    cache = caches.get(cache_name)
    if cache:
        result = await cache.delete(key)
        if result:
            logger.info('(cache: %s) - SUCCESS deleted k/v [%s]!', cache_name, key)
            return result

        logger.warning('(cache: %s) - ERROR deleting k/v [%s]!', cache_name, key)
        return result
    raise VoluspaError('Unable to retrieve cache')
