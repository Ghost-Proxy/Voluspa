import logging

import modules.cache as cache
from modules.custom_embed import default_embed, success_embed, error_embed

from discord.ext import commands

logger = logging.getLogger('voluspa.cog.cache')


class Cache(commands.Cog):
    """Test of Caches"""
    def __init__(self, bot):
        self.bot = bot

    # TODO: This needs some refactoring/DRY'ing

    @commands.command(name='cache-add', aliases=['ca', 'cache-create'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_add(self, ctx, cache_key: str, *, cache_value: str):
        """Adds key/value to cache

        Errors if Key already exists!"""
        cache_name = cache.CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name = cache_key.split('cache_name=')[1]
            cache_key, cache_value = cache_value.split(' ')
        try:
            await cache.add(cache_key, cache_value, cache_name=cache_name)
        except ValueError as e:
            logger.info(f'Key already exists: {e}')
            embed = error_embed(
                title='Cache Add (K/V)',
                description=f'Error adding Key/Value to "{cache_name}" cache!\n\n'
                            f'_Must use `cache-overwrite` to update Key:_\n`{cache_key}`'
            )
        else:
            embed = success_embed(
                title='Cache Add (K/V)',
                description=f'Added the following Key/Value to "{cache_name}" cache'
            )
            embed.add_field(
                name=f'{cache_key}',
                value=f'{cache_value}',
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name='cache-overwrite', aliases=['cow', 'cache-update'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_overwrite(self, ctx, cache_key: str, *, cache_value: str):
        """Writes key/value to cache (CAUTION!)

        This implies creating if not present
        OR
        This implies overwriting if present"""
        cache_name = cache.CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name = cache_key.split('cache_name=')[1]
            cache_key, cache_value = cache_value.split(' ')
        original_value = await cache.read(cache_key, cache_name=cache_name)
        await cache.write(cache_key, cache_value, cache_name=cache_name)
        embed = default_embed(
            title='Cache Update (K/V)',
            description=f'Updated the following Key/Value in "{cache_name}" cache'
        )
        embed.add_field(
            name=f'Original {cache_key}',
            value=f'{original_value}',
            inline=False
        )
        embed.add_field(
            name=f'Updated {cache_key}',
            value=f'{cache_value}',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name='cache-read', aliases=['cr', 'cg', 'cache-get'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_read(self, ctx, *, cache_key: str):
        """Reads value for key from cache"""
        cache_name = cache.CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name, cache_key = cache_key.split(' ')
            cache_name = cache_name.split('cache_name=')[1]
        cache_value = await cache.read(cache_key, cache_name=cache_name)
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

    @commands.command(name='cache-delete', aliases=['cd'])  # , 'cr', 'cache-remove'])
    @commands.has_any_role('founder', 'ghost-proxy-vanguard', 'ghost-proxy-gatekeeper')
    async def cache_delete(self, ctx, *, cache_key: str):
        """Deletes key/value from cache (CAUTION!)"""
        cache_name = cache.CACHE_NAME
        if 'cache_name=' in cache_key:
            cache_name, cache_key = cache_key.split(' ')
            cache_name = cache_name.split('cache_name=')[1]
        cache_value = await cache.delete(cache_key, cache_name=cache_name)
        embed = default_embed(
            title='Cache Delete (K/V)',
            description=f'Deleted the following Key from "{cache_name}" cache'
        )
        embed.add_field(
            name=f'{cache_key}',
            value=f'_deleted_',
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Cache(bot))



'''

2019-11-14T00:06:34.893853+00:00 app[worker.1]: Ignoring exception in command cache-add:
2019-11-14T00:06:34.894347+00:00 app[worker.1]: Traceback (most recent call last):
2019-11-14T00:06:34.894521+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/discord/ext/commands/core.py", line 79, in wrapped
2019-11-14T00:06:34.894524+00:00 app[worker.1]: ret = await coro(*args, **kwargs)
2019-11-14T00:06:34.894606+00:00 app[worker.1]: File "/app/cogs/cache.py", line 28, in cache_add
2019-11-14T00:06:34.894610+00:00 app[worker.1]: await cache.add(cache_key, cache_value, cache_name=cache_name)
2019-11-14T00:06:34.894653+00:00 app[worker.1]: File "/app/modules/cache.py", line 20, in add
2019-11-14T00:06:34.894656+00:00 app[worker.1]: await cache.add(key, value)
2019-11-14T00:06:34.894702+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/base.py", line 61, in _enabled
2019-11-14T00:06:34.894706+00:00 app[worker.1]: return await func(*args, **kwargs)
2019-11-14T00:06:34.894822+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/base.py", line 45, in _timeout
2019-11-14T00:06:34.894825+00:00 app[worker.1]: return await asyncio.wait_for(func(self, *args, **kwargs), timeout)
2019-11-14T00:06:34.894976+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/asyncio/tasks.py", line 442, in wait_for
2019-11-14T00:06:34.894980+00:00 app[worker.1]: return fut.result()
2019-11-14T00:06:34.895026+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/base.py", line 75, in _plugins
2019-11-14T00:06:34.895031+00:00 app[worker.1]: ret = await func(self, *args, **kwargs)
2019-11-14T00:06:34.895078+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/base.py", line 163, in add
2019-11-14T00:06:34.895096+00:00 app[worker.1]: await self._add(ns_key, dumps(value), ttl=self._get_ttl(ttl), _conn=_conn)
2019-11-14T00:06:34.895159+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/backends/redis.py", line 24, in wrapper
2019-11-14T00:06:34.895163+00:00 app[worker.1]: return await func(self, *args, _conn=_conn, **kwargs)
2019-11-14T00:06:34.895208+00:00 app[worker.1]: File "/app/.heroku/python/lib/python3.7/site-packages/aiocache/backends/redis.py", line 158, in _add
2019-11-14T00:06:34.895212+00:00 app[worker.1]: raise ValueError("Key {} already exists, use .set to update the value".format(key))
2019-11-14T00:06:34.895536+00:00 app[worker.1]: ValueError: Key test already exists, use .set to update the value

'''
