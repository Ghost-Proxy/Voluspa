import logging

from voluspa import CONFIG
from modules.custom_embed import default_embed

from discord.ext import commands
from aiocache import caches

logger = logging.getLogger('voluspa.cog.cache')

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


class Cache(commands.Cog):
    """Test of Caches"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cache-write', aliases=['cw', 'ca', 'cache-add'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_write(self, ctx, cache_key: str, *, cache_value: str):
        """Writes key/value to cache"""
        cache_name = CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name = cache_key.split('cache_name=')[1]
            cache_key, cache_value = cache_value.split(' ')
        await write_cache(cache_key, cache_value, cache_name=cache_name)
        # await ctx.send(f'Wrote the following to cache:\nkey: {cache_key}\nvalue: {cache_value}')
        embed = default_embed(
            title='Cache Write (K/V)',
            description=f'Wrote the following Key/Value to "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='cache-read', aliases=['cr', 'cg', 'cache-get'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_read(self, ctx, *, cache_key: str):
        """Reads value for key from cache"""
        cache_name = CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name, cache_key = cache_key.split(' ')
            cache_name = cache_name.split('cache_name=')[1]
        cache_value = await read_cache(cache_key, cache_name=cache_name)
        # await ctx.send(f'Read the following from cache:\nkey: {cache_key}\nvalue: {cache_value}')
        embed = default_embed(
            title='Cache Read (K/V)',
            description=f'Read the following Key/Value from "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Cache(bot))
