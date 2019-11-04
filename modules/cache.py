import logging

from voluspa import CONFIG

from aiocache import caches

logger = logging.getLogger('voluspa.cache')

if CONFIG.Voluspa.cache.get('redis', None):
    CACHE_NAME = 'redis'
else:
    CACHE_NAME = 'default'
CACHE_TYPE = CONFIG.Voluspa.cache[CACHE_NAME].cache
logger.info(f'Using "{CACHE_NAME}" cache ({CACHE_TYPE})')


async def write_cache(key, value, cache_name=CACHE_NAME):
    cache = caches.get(cache_name)
    await cache.set(key, value)
    result = await cache.get(key) == value
    # assert await cache.get(key) == value
    if result:
        logger.info(f'(cache: {cache_name}) - SUCCESS wrote k/v [{key}]:[{value}]!')
        return result
    else:
        logger.warning(f'(cache: {cache_name}) - ERROR writing k/v [{key}]:[{value}]!')
        return result


async def read_cache(key, cache_name=CACHE_NAME):
    cache = caches.get(cache_name)
    value = await cache.get(key)
    if value:
        logger.info(f'(cache: {cache_name}) - SUCCESS read k/v [{key}]:[{value}]')
        return value
    else:
        logger.warning(f'(cache: {cache_name}) - ERROR reading k/v [{key}]:[{value}]!')
        return None


async def delete_cache(key, cache_name=CACHE_NAME):
    cache = caches.get(cache_name)
    result = await cache.delete(key)
    if result:
        logger.info(f'(cache: {cache_name}) - SUCCESS deleted k/v [{key}]!')
        return result
    else:
        logger.warning(f'(cache: {cache_name}) - ERROR deleting k/v [{key}]!')
        return result
