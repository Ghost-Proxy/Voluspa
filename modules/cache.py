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
            logger.info(f'(cache: {cache_name}) - SUCCESS wrote k/v [{key}]:[{value}]!')
            return result

        logger.warning(f'(cache: {cache_name}) - ERROR writing k/v [{key}]:[{value}]!')
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
            logger.info(f'(cache: {cache_name}) - SUCCESS wrote k/v [{key}]:[{value}]!')
            return result

        logger.warning(f'(cache: {cache_name}) - ERROR writing k/v [{key}]:[{value}]!')
        return result
    raise VoluspaError('Unable to retrieve cache')


async def read(key, cache_name=CACHE_NAME):
    """Read the value from the requested key"""
    cache = caches.get(cache_name)
    if cache:
        value = await cache.get(key)
        if value:
            logger.info(f'(cache: {cache_name}) - SUCCESS read k/v [{key}]:[{value}]')
            return value

        logger.warning(f'(cache: {cache_name}) - ERROR reading k/v [{key}]:[{value}]!')
        return None
    raise VoluspaError('Unable to retrieve cache')


async def delete(key, cache_name=CACHE_NAME):
    """Delete the key (and value) requested"""
    cache = caches.get(cache_name)
    if cache:
        result = await cache.delete(key)
        if result:
            logger.info(f'(cache: {cache_name}) - SUCCESS deleted k/v [{key}]!')
            return result

        logger.warning(f'(cache: {cache_name}) - ERROR deleting k/v [{key}]!')
        return result
    raise VoluspaError('Unable to retrieve cache')
