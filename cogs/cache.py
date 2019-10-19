import discord
from discord.ext import commands

from aiocache import caches

CACHE = caches.get('redis')


class Cache(commands.Cog):
    """Test of Caches"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cache-write', aliases=['cache-add', 'cw', 'ca'])
    @commands.is_owner()
    async def cache_write(self, ctx, cache_key: str, *, cache_value: str):
        """"""
        async def _write_cache(_key, _value):
            await CACHE.set(_key, _value)
            result = await CACHE.get(_key) == _value
            # assert await cache.get(_key) == _value
            if result:
                print(f'Wrote key: [{_key}] with value: [{_value}]')
            else:
                print(f'ERROR writing key: [{_key}] with value: [{_value}]!')
        await _write_cache(cache_key, cache_value)
        await ctx.send(f'Wrote the following to cache:\nkey: {cache_key}\nvalue: {cache_value}')

    @commands.command(name='cache-read', aliases=['cr'])
    @commands.is_owner()
    async def cache_read(self, ctx, cache_key: str):
        """"""
        async def _read_cache(_key):
            _value = await CACHE.get(_key)
            if _value:
                print(f'Read key: [{_key}] with value: [{_value}]')
                return _value
            else:
                print(f'>>> ERROR reading key: [{_key}]!')
                return None
        cache_value = await _read_cache(cache_key)
        await ctx.send(f'Read the following from cache:\nkey: {cache_key}\nvalue: {cache_value}')


def setup(bot):
    bot.add_cog(Cache(bot))
